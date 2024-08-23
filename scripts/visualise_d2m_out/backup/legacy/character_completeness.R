# Load necessary packages
pacman::p_load("tidyverse", "here", "plyr", "jsonlite")

# Load json
# Data from desc2matrix_accum.py, which populates the initial character
# list by asking the prompt from desc2matrix.py with the first species description
accum_dat <- read_json(here::here("../json_outputs/accum_out_800sp.json"))
# Data from desc2matrix_accum_tab.py, which populates the initial character
# list by asking the LLM to tabulate the characteristics from the first three species descriptions
accum_tab_dat <- read_json(here::here("../json_outputs/accum_tab_out_800sp.json"))
# Data from desc2matrix_accum_followup.py, which is built upon desc2matrix_accum_tab.py
# but asks a 'follow-up question' including words that were omitted from the original description
# to increase trait coverage
accum_f_dat <- read_json(here::here("../json_outputs/accum_followup_out_800sp.json"))

# ===== Generate figures to determine whether the extracted characteristics conform to the given list =====

# Extract character lists
charlists_given <- list(
  accum = accum_dat$charlist_history,
  accum_tab = accum_tab_dat$charlist_history[-1],
  accum_f = accum_f_dat$charlist_history[-1]
)

# Extract the lists of characters actually returned by the model
data2charlist <- function(char_data) {
  if(!is.null(char_data$char_json)) { # If the species description was successfully parsed
    lapply(char_data$char_json, function(trait) {
      trait$characteristic
    })
  } else {
    NULL
  }
}

charlists_actual <- list(
  accum = lapply(accum_dat$data, data2charlist),
  accum_tab = lapply(accum_tab_dat$data, data2charlist),
  accum_f = lapply(accum_f_dat$data, data2charlist)
)

# Build collated list of lists
charlists_pair <- mapply(function(given_charlists, actual_charlists) {
  mapply(function(given_charlist, actual_charlist) {
    list(given = given_charlist, actual = actual_charlist)
  }, given_charlists, actual_charlists, SIMPLIFY = FALSE)
}, charlists_given, charlists_actual, SIMPLIFY = FALSE)

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
  run_name <- c("accum", "accum_tab", "accum_f")[run_i]
  bind_rows(lapply(run, function(comp_row) {
    df_row <- comp_row
    df_row[-1] <- lapply(df_row[-1], function(charlist) { ifelse(is.null(charlist), NA, length(charlist)) })
    df_row$prop_given_in_actual <- df_row$common / df_row$given
    df_row$prop_actual_in_given <- df_row$common / df_row$actual
    df_row$method <- run_name
    df_row
  }))
})

# Merge data into single df
compare_merged_df <- bind_rows(compare_dfs)
# Reorder methods
compare_merged_df$method <- factor(compare_merged_df$method, levels = c("accum", "accum_tab", "accum_f"))

# Plot proportions of traits recovered from the given list of traits
method_lab <- c("Accumulation without tabulation", "Accumulation with tabulation", "Accumulation with tabulation and followup")
names(method_lab) <- c("accum", "accum_tab", "accum_f")

prop_given_histplots <- ggplot(compare_merged_df, aes(x = prop_given_in_actual)) +
  geom_histogram(binwidth = 0.05, fill = "#ffffff", color = "#000000", boundary = 0) +
  geom_vline(data = ddply(compare_merged_df, "method", summarize, med_prop = median(prop_given_in_actual, na.rm = TRUE)),
             aes(xintercept = med_prop), linetype = "dashed") +
  facet_wrap(~ method, ncol = 1, labeller = labeller(method = method_lab)) +
  scale_x_continuous(breaks = seq(0, 1, by = 0.1)) +
  labs(
    x = "Proportion of given characteristics\nthat were actually included in the JSON output",
    y = "Count"
  ) +
  theme_bw()
prop_given_histplots
ggsave(here::here("figures/prop_chars_recovered.png"), prop_given_histplots, width = 5, height = 6)

# Plot proportions of output traits that were in the provided trait list

prop_actual_histplots <- ggplot(compare_merged_df, aes(x = prop_actual_in_given)) +
  geom_histogram(binwidth = 0.05, fill = "#ffffff", color = "#000000", boundary = 0) +
  geom_vline(data = ddply(compare_merged_df, "method", summarize, med_prop = median(prop_actual_in_given, na.rm = TRUE)),
             aes(xintercept = med_prop), linetype = "dashed") +
  facet_wrap(~ method, ncol = 1, labeller = labeller(method = method_lab)) +
  scale_x_continuous(breaks = seq(0, 1, by = 0.1)) +
  labs(
    x = "Proportion of characteristics in the output JSON\nthat were originally given in the character list",
    y = "Count"
  ) +
  theme_bw()
prop_actual_histplots
ggsave(here::here("figures/prop_chars_actual.png"), prop_actual_histplots, width = 5, height = 6)
