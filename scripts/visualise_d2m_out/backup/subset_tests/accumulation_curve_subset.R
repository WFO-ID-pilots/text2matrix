# Install package manager if not installed already
# install.packages("pacman")

# Load necessary packages
pacman::p_load("tidyverse", "here", "jsonlite")

# Load json outputs from running desc2matrix scripts on the select species of Solanum
# Data from desctmatrix_accum.py
subset_dat <- read_json(here::here("../outputs/accum_output/accum_subset.json"))
# Data from desc2matrix_accum_tab.py
subset_tab_dat <- read_json(here::here("../outputs/accum_output/accum_tab_subset.json"))
# Data from desc2matrix_accum_followup.py
subset_f_dat <- read_json(here::here("../outputs/accum_output/accum_f_subset.json"))

# List containing the data
accum_dats <- list(
  subset = subset_dat,
  subset_tab = subset_tab_dat,
  subset_f = subset_f_dat
)

method_names <- c("subset", "subset_tab", "subset_f")
method_labels <- c(
  "Initial trait list obtained from one species",
  "Initial trait list obtained by tabulating the characteristics of three species",
  "Initial trait list obtained by tabulation,\nand follow-up questions asked during accumulation"
)
names(method_labels) <- method_names

# ===== Generate accumulation curve =====

# Get charlist length histories
accum_charlens <- lapply(accum_dats, function(accum_d) { accum_d$charlist_len_history })

# Get incidences of failures
accum_failures <- lapply(accum_dats, function(accum_d) {
  sapply(seq_along(accum_d$data), function(spdat_id) {
    spdat <- accum_d$data[[spdat_id]]
    if(spdat$status == "success") { NA }
    else { spdat_id }
  })
})

fail_df <- tibble(
  sp_id = do.call(c, lapply(seq_along(accum_failures), function(run_id) {
    accum_fail_ids <- accum_failures[[run_id]]
    if(run_id == 1) { # If the run is without tabulation
      accum_fail_ids # Return without inserting NA at the start since there was no initial tabulation
    } else { # Otherwise
      c(NA, accum_fail_ids) # Return with initial NA to account for initial tabulation
    }
  })),
  charlen = do.call(c, unlist(accum_charlens, recursive=FALSE))
)

# Method names
method_list <- lapply(seq_along(accum_charlens), function(i) { rep(method_names[i], length(accum_charlens[[i]])) })

# Species IDs
id_list <- lapply(accum_charlens, function(charlens) { seq(ifelse(is.na(charlens[[1]]), 0, 1), length.out = length(charlens)) })
sp_ids <- unlist(id_list)

# Build tibble
accum_df <- tibble(
  sp_id = sp_ids, # Number of species processed
  charlen = unlist(accum_charlens), # Number of characteristics retrieved from the runs
  method = unlist(method_list)
)

# Plot accumulation curve
accum_plt <- ggplot() +
  geom_line(data = accum_df, aes(x = sp_id, y = charlen, color = method)) +
  geom_point(data = fail_df, aes(x = sp_id, y = charlen), shape = 4) +
  labs(
    x = "Number of species processed",
    y = "Number of characteristics",
    color = "Method",
    title = "Trait accumulation tests on the subsetted data"
  ) +
  scale_color_brewer(palette = "Dark2", labels = method_labels,
  breaks = method_names) +
  theme_bw() +
  theme(legend.position = "bottom") +
  guides(color = guide_legend(nrow = 3, byrow = FALSE))
accum_plt
ggsave(here::here("figures/subset_accum.png"), accum_plt, width = 6, height = 5.5)
