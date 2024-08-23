# Load necessary packages
pacman::p_load("tidyverse", "here", "plyr", "jsonlite")

# Load json
# Data from desc2matrix_wcharlist.py
wcharlist_dat <- read_json(here::here("../outputs/wcharlist_output/wcharlist_subset.json"))
# Data from desctmatrix_wcharlist_followup.py
wcharlist_f_dat <- read_json(here::here("../outputs/wcharlist_output/wcharlist_f_subset.json"))
# Data from desc2matrix_langchain_wcharlist.py
wcharlist_lc_dat <- read_json(here::here("../outputs/wcharlist_output/wcharlist_langchain_subset.json"))

# Vector of the method names
method_names <- c("wcharlist", "wcharlist_f", "wcharlist_lc")
method_labels <- c("Without follow-up Q", "With follow-up Q", "Without follow-up Q, with LangChain")

# ===== Generate figures to determine whether the extracted characteristics conform to the given list =====


# Extract character lists
charlists_given <- list(
  wcharlist = wcharlist_dat$charlist,
  wcharlist_f = wcharlist_f_dat$charlist,
  wcharlist_lc = wcharlist_lc_dat$metadata$charlist
)

# Extract the lists of characters actually returned by the model
data2charlist <- function(char_data) {
  if(char_data$status == "success") { # If the species description was successfully parsed
    lapply(char_data$char_json, function(trait) {
      trait$characteristic
    })
  } else {
    NULL
  }
}

# Collate actual lists of characteristics returned by the model across the runs
charlists_actual <- list(
  wcharlist = lapply(wcharlist_dat$data, data2charlist),
  wcharlist_f = lapply(wcharlist_f_dat$data, data2charlist),
  wcharlist_lc = lapply(wcharlist_lc_dat$data, data2charlist)
)

# Build collated list with pairs of given character lists and actual character lists
charlists_pair <- lapply(seq_along(charlists_given), function(run_id) {
  lapply(charlists_actual[[run_id]], function(actual_charlist) {
    list(given = charlists_given[[run_id]], actual = actual_charlist)
  })
})

# Go through the characteristics and compare
compare_charlists <- function(charlist_pairs) {
  lapply(seq_along(charlist_pairs), function(charlist_pair_i) {
    charlist_pair <- charlist_pairs[[charlist_pair_i]]
    # Determine the shared and exclusive characteristics between the provided character list and the actual output list
    chars_common <- intersect(charlist_pair$given, charlist_pair$actual)
    chars_given_only <- setdiff(charlist_pair$given, charlist_pair$actual)
    chars_actual_only <- setdiff(charlist_pair$actual, charlist_pair$given)
    
    list(
      sp_id = charlist_pair_i,
      given = charlist_pair$given,
      actual = charlist_pair$actual,
      common = if(is.null(charlist_pair$actual)) { NULL } else { chars_common },
      given_only = if(is.null(charlist_pair$actual)) { NULL } else { chars_given_only },
      actual_only = if(is.null(charlist_pair$actual)) { NULL } else { chars_actual_only }
    )
  })
}
charlists_compare <- lapply(charlists_pair, compare_charlists)

# Count up data
compare_dfs <- lapply(seq_along(charlists_compare), function(run_i) {
  run <- charlists_compare[[run_i]]
  run_name <- method_names[run_i]
  bind_rows(lapply(run, function(comp_row) {
    df_row <- comp_row
    df_row[-1] <- lapply(df_row[-1], function(charlist) { ifelse(is.null(charlist), NA, length(charlist)) })
    df_row$prop_given_in_actual <- df_row$common / df_row$given
    df_row$prop_actual_in_given <- df_row$common / df_row$actual
    df_row$method <- run_name
    df_row
  }))
})

compare_dfs

# Merge data into single df
compare_merged_df <- bind_rows(compare_dfs)
# Reorder methods
compare_merged_df$method <- factor(compare_merged_df$method, levels = method_names)

# Plot proportions of traits recovered from the given list of traits
method_lab <- method_labels
names(method_lab) <- method_names

prop_given_histplots <- ggplot(compare_merged_df, aes(x = prop_given_in_actual)) +
  geom_histogram(binwidth = 0.05, fill = "#ffffff", color = "#000000", boundary = 0) +
  geom_vline(data = ddply(compare_merged_df, "method", summarize, med_prop = median(prop_given_in_actual, na.rm = TRUE)),
             aes(xintercept = med_prop), linetype = "dashed") +
  facet_wrap(~ method, ncol = 1, labeller = labeller(method = method_lab), scales = "free_y") +
  scale_x_continuous(breaks = seq(0, 1, by = 0.1)) +
  labs(
    x = "Proportion of given characteristics\nthat were actually included in the JSON output",
    y = "Count",
    title = "Proportion of listed characteristics recovered"
  ) +
  theme_bw()
prop_given_histplots
ggsave(here::here("figures/langchain_test/wcharlist_chars_recovered_subset.png"), prop_given_histplots, width = 5, height = 6)

# Plot proportions of output traits that were in the provided trait list

prop_actual_histplots <- ggplot(compare_merged_df, aes(x = prop_actual_in_given)) +
  geom_histogram(binwidth = 0.05, fill = "#ffffff", color = "#000000", boundary = 0) +
  geom_vline(data = ddply(compare_merged_df, "method", summarize, med_prop = median(prop_actual_in_given, na.rm = TRUE)),
             aes(xintercept = med_prop), linetype = "dashed") +
  facet_wrap(~ method, ncol = 1, labeller = labeller(method = method_lab), scales = "free_y") +
  scale_x_continuous(breaks = seq(0, 1, by = 0.1)) +
  labs(
    x = "Proportion of characteristics in the output JSON\nthat were originally given in the character list",
    y = "Count",
    title = "Proportion of extracted characteristics\nin the original list"
  ) +
  theme_bw()
prop_actual_histplots
ggsave(here::here("figures/langchain_test/wcharlist_chars_actual_subset.png"), prop_actual_histplots, width = 5, height = 6)
