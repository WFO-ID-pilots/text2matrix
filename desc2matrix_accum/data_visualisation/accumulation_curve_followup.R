# Install package manager if not installed already
# install.packages("pacman")

# Load necessary packages
pacman::p_load("tidyverse", "here", "jsonlite", "ggVennDiagram", "plotly", "ggwordcloud", "scales")

# Load json
# Data from desc2matrix_accum_followup.py with default settings
accum_dat <- read_json(here::here("../json_outputs/accum_followup_out_800sp.json"))
# Data from the same script with larger context window size (see file for metadata)
accum_lc_dat <- read_json(here::here("../json_outputs/accum_f_out_largerctx_800sp.json"))
# Data from the same script with character list provided in the follow-up question
accum_lf_dat <- read_json(here::here("../json_outputs/accum_f_out_listinfollowup_800sp.json"))
# Data from the same script with both treatments
accum_lclf_dat <- read_json(here::here("../json_outputs/accum_f_out_largerctx_and_listinfollowup_800sp.json"))

# List containing the data
accum_dats <- list(
  accum = accum_dat,
  accum_lc = accum_lc_dat,
  accum_lf = accum_lf_dat,
  accum_lclf = accum_lclf_dat
)

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
  sp_id = do.call(c, lapply(accum_failures, function(accum_fail_ids) { c(NA, accum_fail_ids) })), # First is NA, corresponding to the missing initial tabulation
  charlen = do.call(c, unlist(accum_charlens, recursive=FALSE))
)

# Method names
method_names <- c("accum", "accum_lc", "accum_lf", "accum_lclf")
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
  ) +
  scale_color_brewer(palette = "Dark2", labels = c(
    "accum" = "Follow-up",
    "accum_lc" = "Larger context",
    "accum_lf" = "With list in the follow-up question",
    "accum_lclf" = "Larger context and with list in the follow-up question"
    ),
    breaks = c("accum", "accum_lc", "accum_lf", "accum_lclf")) +
  theme_bw() +
  theme(legend.position = "bottom") +
  guides(color = guide_legend(nrow = 2, byrow = FALSE))
accum_plt
ggsave(here::here("figures/accum_curve_800_followup.png"), accum_plt, width = 5, height = 4)