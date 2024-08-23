# Install package manager if not installed already
# install.packages("pacman")

# Load necessary packages
pacman::p_load("tidyverse", "here", "jsonlite", "plyr")

# Load jsons
wcharlist_sg_dat <- read_json(here::here("../outputs/wcharlist_output/wcharlist_sgenlist_subset.json"))
wcharlist_f_sg_dat <- read_json(here::here("../outputs/wcharlist_output/wcharlist_f_sgenlist_subset.json"))
wcharlist_lg_dat <- read_json(here::here("../outputs/wcharlist_output/wcharlist_lgenlist_subset.json"))
wcharlist_f_lg_dat <- read_json(here::here("../outputs/wcharlist_output/wcharlist_f_lgenlist_subset.json"))

# List containing the data
wcharlist_dats <- list(
  wcharlist_sg = wcharlist_sg_dat,
  wcharlist_f_sg = wcharlist_f_sg_dat,
  wcharlist_lg = wcharlist_lg_dat,
  wcharlist_f_lg = wcharlist_f_lg_dat 
)

# ===== Plot histogram of the number of characteristics recovered in the output =====

# Get output character list length histories
wcharlist_charlens <- lapply(wcharlist_dats, function(wcharlist_d) {
  lapply(wcharlist_d$data, function(species) {
    if(is.null(species$char_json)) { NA }
    else { as.numeric(length(species$char_json)) }
  })
})

# Method names
method_names <- c("wcharlist_sg", "wcharlist_f_sg", "wcharlist_lg", "wcharlist_f_lg")
method_lab <- c("Shorter trait list, without follow-up", "Shorter trait list, with follow-up", "Longer trait list, without follow-up", "Longer trait list, with follow-up")
names(method_lab) <- method_names
method_list <- lapply(seq_along(wcharlist_charlens), function(i) { rep(method_names[i], length(wcharlist_charlens[[i]])) })

# Dataframe containing the length of the character list provided for each run
org_charlistlen <- tibble(
  method = names(method_lab),
  org_len = c(49, 49, 84, 84)
)

# Relevel factors
org_charlistlen$method = factor(org_charlistlen$method, levels = method_names)

# Species IDs
id_list <- lapply(wcharlist_charlens, function(charlens) { seq(1, length.out = length(charlens)) })
sp_ids <- unlist(id_list)

# Build tibble
wcharlist_df <- tibble(
  sp_id = sp_ids, # Number of species processed
  charlen = unlist(wcharlist_charlens), # Number of characteristics retrieved from the runs
  method = unlist(method_list)
)

# Relevel methods
wcharlist_df$method <- factor(wcharlist_df$method, levels = method_names)

# Plot histogram of the distribution of the length of characteristic list obtained

wcharlist_plt <- ggplot() +
  geom_histogram(data = wcharlist_df, aes(x = charlen),
                 binwidth = 5, fill = "#ffffff", color = "#000000", boundary = 0) +
  geom_vline(data = org_charlistlen, aes(xintercept = org_len), color = "red") +
  geom_vline(data = ddply(wcharlist_df, "method", summarize, med_n = median(charlen, na.rm = TRUE)),
             aes(xintercept = med_n), linetype = "dashed", color = "blue") +
  labs(
    title = "The number of characteristics in the output across successful runs",
    x = "Number of output characteristics",
    y = "Count"
  ) +
  facet_wrap(~ method, ncol = 1, labeller = labeller(method = method_lab), scales = "free_y") +
  theme_bw() +
  theme(legend.position = "bottom")
wcharlist_plt
ggsave(here::here("figures/subset_test/charcount_wc_gen_subset.png"), wcharlist_plt, width = 6, height = 5)

# ===== Plot the proportions of failed parses in each of the runs =====

# List containing the counts of each of the status in the runs
status_list <- lapply(seq_along(wcharlist_dats), function(run_id) {
  run <- wcharlist_dats[[run_id]]
  run_method <- names(wcharlist_dats)[run_id]
  char_data <- run$data
  statuses <- lapply(char_data, function(sp) { sp$status }) # Retrieve the status codes
  stat_df <- as.data.frame(table(unlist(statuses))) # Count up unique status codes
  stat_df <- tibble(stat_df) %>% # Convert to tibble
    dplyr::rename( # Rename columns
      status = 1,
      count = 2
    ) %>%
    mutate(
      method = run_method
    )
  return(stat_df) # Return df
})
# Bind the counts into a single df
status_df <- bind_rows(status_list) %>%
  mutate(
    status = factor(status, levels = c("success", "invalid_json", "invalid_json_followup"))
  )

status_df

# Plot barplot to show the distribution of statuses
status_plt <- ggplot(status_df, aes(x = count, y = method, fill = status)) +
  geom_bar(position="stack", stat="identity", width = .5) +
  scale_y_discrete(
    labels = method_lab
  ) +
  scale_fill_manual(
    labels = c("Success", "Invalid JSON output in initial prompt", "Invalid JSON output in follow-up prompt"),
    values = c("#abf2a7", "#facc16", "#ed1c09"),
    breaks = c("success", "invalid_json", "invalid_json_followup")
  ) +
  labs(
    title = "Proportion of each run status\nin runs with accumulated traits",
    y = "Run",
    x = "Count",
    fill = "Status"
  ) +
  theme_bw() +
  theme(legend.position = "bottom") +
  guides(fill = guide_legend(ncol=1,byrow=TRUE))
  
status_plt
ggsave(here::here("figures/subset_test/subsetstatus_wc_gen_subset.png"), status_plt, width = 6.5, height = 5)
