# This script visualises the tsv output from process_d2m_out/quality_control/compare_chars.py,
# which compares the characteristics and value output from desc2matrix scripts against their
# counterpart in a structured key of Solanum species, found here:
# https://url.uk.m.mimecastprotect.com/s/YP9XCWQRPfDXo1NIKijuVb2y7

# Load necessary packages
pacman::p_load("tidyverse", "here", "plyr")

# ===== Load tsvs =====

# Run names
run_names <- c(
  "wcharlist",
  "wcharlist_sgenlist",
  "wcharlist_lgenlist",
  "wcharlist_f",
  "wcharlist_f_sgenlist",
  "wcharlist_f_lgenlist"
)
names(run_names) <- run_names

# Run labels
run_labels <- c(
  "K",
  "GS",
  "GL",
  "K, F",
  "GS, F",
  "GL, F"
)

# File paths
tsv_paths <- lapply(run_names, function(run_name) {
  paste0("../../script_output/process_d2m_out/quality_control/compare_chars/", run_name, "_comp.tsv")
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

# ===== Run status plots =====

status_barplot <- ggplot(runs_df, aes(x = run_name, fill = status)) +
  geom_bar(width = .5) +
  scale_x_discrete(
    labels = rev(run_labels),
    limits = rev
  ) +
  scale_y_continuous(
    breaks = seq(0, 500, 100)
  ) +
  scale_fill_manual(
    labels = c("Success", "Invalid JSON output in initial prompt", "Invalid JSON output in follow-up prompt"),
    values = c("#abf2a7", "#facc16", "#ed1c09"),
    breaks = c("success", "invalid_json", "invalid_json_followup")
  ) +
  labs(
    y = "Count",
    x = "Run",
    fill = "Status"
  ) +
  theme_classic() +
  theme(
    legend.position = "bottom",
    panel.grid.major.y = element_line(color = "lightgrey", linewidth = 0.25)
  ) +
  guides(fill = "none")
  # guides(fill = guide_legend(ncol=1,byrow=TRUE))

status_barplot
ggsave(here::here("../../script_output/visualise_d2m_out/poster/status.png"), status_barplot, width = 3.5, height = 4)

runs_df

# ===== Common characteristics proportion plots =====

runs_df <- runs_df %>%
  mutate(prop_chars_recovered = nchars_common / nchars_key)

ext_prop_plt <- ggplot(runs_df, aes(x = run_name, y = prop_chars_recovered)) +
  geom_boxplot() +
  scale_x_discrete(
    labels = run_labels
  ) +
  scale_y_continuous(breaks = seq(0, 1, by = 0.1)) +
  labs(
    x = "Run mode",
    y = "Proportion of common trait names between output and key"
  ) +
  theme_classic() +
  theme(
    panel.grid.major.y = element_line(color = "lightgrey", linewidth = 0.25)
  )

ext_prop_plt
ggsave(here::here("../../script_output/visualise_d2m_out/poster/extracted_chars.png"), ext_prop_plt, width = 3.5, height = 4)
