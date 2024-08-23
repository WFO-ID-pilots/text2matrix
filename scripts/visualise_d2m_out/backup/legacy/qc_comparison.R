# Install package manager if not installed already
# install.packages("pacman")

# Load necessary packages
pacman::p_load("tidyverse", "here", "plyr")

# Load QC tsvs
# QC tsv from desc2matrix_accum.py, which populates the initial character
# list by asking the prompt from desc2matrix.py with the first species description
accum_qc <- read_tsv(here::here("../json_outputs/accum_800sp_qc.tsv")) %>%
  dplyr::rename(id = 1) %>% # Rename first column as index
  mutate(mode = "accum") # Specify run mode

# QC tsv from desc2matrix_accum_tab.py, which populates the initial character
# list by asking the LLM to tabulate the characteristics from the first three species descriptions
accum_tab_qc <- read_tsv(here::here("../json_outputs/accum_tab_800sp_qc.tsv")) %>%
  dplyr::rename(id = 1) %>% # Rename first column as index
  mutate(mode = "accum_tab")

# QC tsv from desc2matrix_accum_followup.py, which populates the initial character
# list by asking the LLM to tabulate the characteristics from the first three species descriptions
accum_f_qc <- read_tsv(here::here("../json_outputs/accum_followup_800sp_qc.tsv")) %>%
  dplyr::rename(id = 1) %>% # Rename first column as index
  mutate(mode = "accum_f")

# Merge dataframes
qc_df <- rbind(accum_qc, accum_tab_qc, accum_f_qc) %>%
  filter(status == "success") %>% # Filter only succeeded runs
  mutate(prop_created = nwords_created / nwords_result) # Create column for the proportion of recovered words that were 'created'

# ===== Generate QC plots =====

# Labeller for the run mode
mode_lab <- c("Accumulation without tabulation", "Accumulation with tabulation", "Accumulation with tabulation and followup")
names(mode_lab) <- c("accum", "accum_tab", "accum_f")

# Histogram of word coverage
qc_hist <- ggplot(qc_df, aes(x = prop_recovered)) +
  geom_histogram(binwidth = 0.05, fill = "#ffffff", color = "#000000", boundary = 0) +
  geom_vline(data = ddply(qc_df, "mode", summarize, med_prop = median(prop_recovered)),
             aes(xintercept = med_prop), linetype = "dashed") +
  facet_wrap(~mode, ncol = 1, labeller = labeller(mode = mode_lab)) +
  scale_x_continuous(breaks = seq(0, 1, by = 0.1)) +
  labs(
    x = "Proportion of non-stop words recovered",
    y = "Count"
  ) +
  theme_bw()
qc_hist
ggsave(here::here("figures/prop_recovered_histogram.png"), qc_hist, width = 5, height = 4)

# ===== Generate plots for the proportion of words 'created' =====

# Histogram of word coverage
qc_created_hist <- ggplot(qc_df, aes(x = prop_created)) +
  geom_histogram(binwidth = 0.05, fill = "#ffffff", color = "#000000", boundary = 0) +
  geom_vline(data = ddply(qc_df, "mode", summarize, med_prop = median(prop_created)),
             aes(xintercept = med_prop), linetype = "dashed") +
  facet_wrap(~mode, ncol = 1, labeller = labeller(mode = mode_lab)) +
  scale_x_continuous(breaks = seq(0, 1, by = 0.1)) +
  labs(
    x = "Proportion of recovered words not in the original description",
    y = "Count"
  ) +
  theme_bw()
qc_created_hist
ggsave(here::here("figures/prop_created_histogram.png"), qc_created_hist, width = 5, height = 4)
