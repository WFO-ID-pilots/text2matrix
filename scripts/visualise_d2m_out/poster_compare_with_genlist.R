# Load necessary packages
pacman::p_load("tidyverse", "here", "plyr", "jsonlite")

# Run names
run_names <- c(
  "wcharlist_sgenlist",
  "wcharlist_f_sgenlist"
)
names(run_names) <- run_names

run_labels <- c("No follow-up Q", "With follow-up Q")

# JSON File paths
json_paths <- lapply(run_names, function(run_name) {
  paste0("../../script_output/desc2matrix/wcharlist/", run_name, "_subset.json")
})

# Read data
run_dat <- lapply(json_paths, function(json_path) {
  read_json(here::here(json_path))
})

# ===== Generate figures to determine whether the extracted characteristics conform to the given list =====


# Extract given character lists
charlists_given <- lapply(run_dat, function(run_d) { run_d$metadata$charlist })

charlists_given

# Extract the lists of characters actually returned by the model
data2charlist <- function(char_data) {
  if(!is.null(char_data$char_json)) { # If the species description was successfully parsed
    char_list <- lapply(char_data$char_json, function(trait) {
      ifelse(trait$value != "NA", trait$characteristic, NA) # Flag NA
    })
    char_list[!sapply(char_list, is.na)] # Remove characteristics with NA value
  } else {
    NULL
  }
}

# Collate actual lists of characteristics returned by the model across the runs
charlists_actual <- lapply(run_dat, function(run_d) {
  lapply(run_d$data, data2charlist)
})

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
  run_name <- run_names[run_i]
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
compare_merged_df$method <- factor(compare_merged_df$method, levels = run_names)
compare_merged_df

# Colourblind-friendly palette
cbp1 <- c("#E69F00", "#56B4E9", "#009E73",
          "#F0E442", "#0072B2", "#D55E00", "#CC79A7")

# Plot proportions of traits recovered from the given list of traits
method_lab <- run_labels
names(method_lab) <- run_names

prop_given_boxplots <- ggplot(compare_merged_df, aes(x = prop_given_in_actual, y = method, fill = method)) +
  geom_boxplot() +
  scale_x_continuous(breaks = seq(0, 1, by = 0.2), limits = c(0, 1)) +
  scale_y_discrete(
    labels = rev(run_labels),
    limits = rev
  ) +
  labs(
    x = "Proportion of traits extracted"
  ) +
  scale_fill_manual(
    values = cbp1
  ) +
  theme_classic() +
  theme(
    axis.text.y = element_text(angle = 45, vjust = 0.5, hjust=1),
    panel.grid.major.x = element_line(color = "lightgrey", linewidth = 0.25),
    axis.title.y = element_blank()
  ) +
  guides(fill = "none")
prop_given_boxplots
ggsave(here::here("../../script_output/visualise_d2m_out/extracted_chars_sgenlist.png"), prop_given_boxplots, width = 3, height = 1.7)

# Calculate medians for each group
compare_merged_df %>%
  group_by(method) %>%
  dplyr::summarize(
    med = median(prop_given_in_actual, na.rm = TRUE)
  )


# Plot proportions of output traits that were in the provided trait list

# prop_actual_histplots <- ggplot(compare_merged_df, aes(x = prop_actual_in_given)) +
#   geom_histogram(binwidth = 0.05, fill = "#ffffff", color = "#000000", boundary = 0) +
#   geom_vline(data = ddply(compare_merged_df, "method", summarize, med_prop = median(prop_actual_in_given, na.rm = TRUE)),
#              aes(xintercept = med_prop), linetype = "dashed") +
#   facet_wrap(~ method, ncol = 1, labeller = labeller(method = method_lab), scales = "free_y") +
#   scale_x_continuous(breaks = seq(0, 1, by = 0.1)) +
#   labs(
#     x = "Proportion of characteristics in the output JSON\nthat were originally given in the character list",
#     y = "Count",
#     title = "Proportion of extracted characteristics\nin the original list"
#   ) +
#   theme_bw()
# prop_actual_histplots
# ggsave(here::here("figures/subset_test/wcharlist_chars_actual_subset.png"), prop_actual_histplots, width = 5, height = 6)
