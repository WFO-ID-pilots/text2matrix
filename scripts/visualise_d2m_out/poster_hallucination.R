# Run names
run_names <- c(
  "wcharlist",
  "wcharlist_f",
  "wcharlist_sgenlist",
  "wcharlist_f_sgenlist"
)
names(run_names) <- run_names

# Run labels
run_labels <- c(
  "No follow-up Q,\nkey trait",
  "With follow-up Q,\nkey trait",
  "No follow-up Q,\naccum. trait",
  "With follow-up Q,\naccum. trait"
)

# File paths
tsv_paths <- lapply(run_names, function(run_name) {
  paste0("../../script_output/process_d2m_out/compare_d2m_desc/", run_name, "_subset_qc.tsv")
})

# Import files
run_dfs <- lapply(seq_along(tsv_paths), function(i) {
  tsv_path <- tsv_paths[[i]]
  run_name <- names(tsv_paths)[[i]]
  read_tsv(here::here(tsv_path)) %>%
    select(-1) %>% # Remove first column
    mutate(
      run_name = run_name, # Append column indicating run name
      status = factor(status, levels = c("success", "invalid_json", "invalid_json_followup"))
    ) 
})

# Bind into single dataframe
runs_df <- bind_rows(run_dfs) %>%
  mutate(
    run_name = factor(run_name, levels = run_names)
  )


runs_df

# Generate box plot for words in extracted values not found in the original description
# Colourblind-friendly palette
cbp1 <- c("#E69F00", "#56B4E9", "#E69F00", "#56B4E9")

runs_df <- runs_df %>%
  mutate(prop_chars_created = nwords_created_val / nwords_val)

hall_prop_plt <- ggplot(runs_df, aes(y = run_name, x = prop_chars_created, fill = run_name)) +
  geom_boxplot() +
  scale_fill_manual(
    values = cbp1
  ) +
  scale_y_discrete(
    labels = rev(run_labels),
    limits = rev
  ) +
  scale_x_continuous(breaks = seq(0, 1, by = 0.2), limits = c(0, 1)) +
  labs(
    x = "Proportion of created words"
  ) +
  theme_classic() +
  theme(
    # axis.text.y = element_text(angle = 45, vjust = 0.5, hjust=1),
    panel.grid.major.x = element_line(color = "lightgrey", linewidth = 0.25),
    axis.title.y = element_blank()
  ) +
  guides(fill = "none")

hall_prop_plt


ggsave(here::here("../../script_output/visualise_d2m_out/created_words.png"), hall_prop_plt, width = 3, height = 2.2)


quantile(runs_df$prop_chars_created, probs = seq(0, 1, 0.05), na.rm = TRUE)
length(runs_df$prop_chars_created[runs_df$prop_chars_created < 0.1])
nrow(runs_df)
1932 / 2184 * 100
