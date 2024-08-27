# Install package manager if not installed already
# install.packages("pacman")

# Load necessary packages
pacman::p_load("tidyverse", "here", "plyr")

# Load QC tsvs
# QC tsv from desc2matrix_wcharlist.py
wcharlist_qc <- read_tsv(here::here("../outputs/qc_output/wcharlist/wcharlist_800sp_qc.tsv")) %>%
  dplyr::rename(id = 1) %>% # Rename first column as index
  mutate(mode = "wcharlist") # Specify run mode

# QC tsv from desc2matrix_wcharlist_followup.py
wcharlist_f_qc <- read_tsv(here::here("../outputs/qc_output/wcharlist/wcharlist_f_800sp_qc.tsv")) %>%
  dplyr::rename(id = 1) %>% # Rename first column as index
  mutate(mode = "wcharlist_f")

# QC tsv from desc2matrix_wcharlist.py with a shorter character list
wcharlist_s_qc <- read_tsv(here::here("../outputs/qc_output/wcharlist/wcharlist_s_800sp_qc.tsv")) %>%
  dplyr::rename(id = 1) %>% # Rename first column as index
  mutate(mode = "wcharlist_s")

# QC tsv from desc2matrix_wcharlist_followup.py with a shorter character list
wcharlist_sf_qc <- read_tsv(here::here("../outputs/qc_output/wcharlist/wcharlist_sf_800sp_qc.tsv")) %>%
  dplyr::rename(id = 1) %>% # Rename first column as index
  mutate(mode = "wcharlist_sf")

# Merge dataframes
qc_df <- rbind(wcharlist_qc, wcharlist_f_qc, wcharlist_s_qc, wcharlist_sf_qc) %>%
  filter(status == "success") %>% # Filter only succeeded runs
  mutate(prop_created = nwords_created / nwords_result) # Create column for the proportion of recovered words that were 'created'

# ===== Generate QC plots =====

# Labeller for the run mode
mode_lab <- c("Long trait list", "Long trait list w/ follow-up", "Short trait list", "Short trait list w/ follow-up")
names(mode_lab) <- c("wcharlist", "wcharlist_f", "wcharlist_s", "wcharlist_sf")

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
ggsave(here::here("figures/wcharlist_prop_recovered_histogram.png"), qc_hist, width = 5, height = 6)


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
ggsave(here::here("figures/wcharlist_prop_created_histogram.png"), qc_created_hist, width = 5, height = 6)

