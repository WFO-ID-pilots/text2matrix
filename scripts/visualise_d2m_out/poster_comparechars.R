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
  "wcharlist_f"
)
names(run_names) <- run_names

# Run labels
run_labels <- c(
  "No follow-up Q",
  "With follow-up Q"
)

# File paths
tsv_paths <- lapply(run_names, function(run_name) {
  paste0("../../script_output/process_d2m_out/compare_d2m_key_chars/", run_name, "_comp_2nd.tsv")
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
ggsave(here::here("../../script_output/visualise_d2m_out/status_key.png"), status_barplot, width = 3.5, height = 4)

# ===== Common characteristics proportion plots =====

# Colourblind-friendly palette
cbp1 <- c("#E69F00", "#56B4E9", "#009E73",
          "#F0E442", "#0072B2", "#D55E00", "#CC79A7")

runs_df <- runs_df %>%
  mutate(prop_chars_recovered = nchars_common / nchars_key)

ext_prop_plt <- ggplot(runs_df, aes(x = run_name, y = prop_chars_recovered, fill = run_name)) +
  geom_boxplot() +
  scale_fill_manual(
    values = cbp1
  ) +
  scale_x_discrete(
    labels = run_labels
  ) +
  scale_y_continuous(breaks = seq(0, 1, by = 0.1)) +
  labs(
    x = "Method",
    y = "Proportion of traits extracted"
  ) +
  theme_classic() +
  theme(
    panel.grid.major.y = element_line(color = "lightgrey", linewidth = 0.25)
  ) +
  guides(fill = "none")

ext_prop_plt
ggsave(here::here("../../script_output/visualise_d2m_out/extracted_chars_key.png"), ext_prop_plt, width = 2.7, height = 2.7)
