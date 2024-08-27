# Install package manager if not installed already
# install.packages("pacman")

# Load necessary packages
pacman::p_load("tidyverse", "here", "jsonlite", "readr", "ggVennDiagram")

# List containing the data
accum_dats <- list(
  subset = read_json(here::here("../../script_output/desc2matrix/accum/accum_subset_2nd.json")),
  subset_f = read_json(here::here("../../script_output/desc2matrix/accum/accum_f_subset_2nd.json"))
)

method_names <- names(accum_dats)
method_labels <- c(
  "No follow-up Q",
  "With follow-up Q"
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
    # Insert NA to match the length of the charlens history
    c(rep(NA, length(accum_charlens[[run_id]]) - length(accum_fail_ids)), accum_fail_ids)
  })),
  charlen = do.call(c, unlist(accum_charlens, recursive=FALSE))
)

# Method names
method_list <- lapply(seq_along(accum_charlens), function(i) { rep(method_names[i], length(accum_charlens[[i]])) })

# Species sequential IDs
id_list <- lapply(accum_charlens, function(charlens) { seq(ifelse(is.na(charlens[[1]]), 0, 1), length.out = length(charlens)) })
sp_ids <- unlist(id_list)

# Build tibble
accum_df <- tibble(
  sp_id = sp_ids, # Number of species processed
  charlen = unlist(accum_charlens), # Number of characteristics retrieved from the runs
  method = unlist(method_list)
)

# Colourblind-friendly palette
cbp1 <- c("#E69F00", "#56B4E9", "#009E73",
          "#F0E442", "#0072B2", "#D55E00", "#CC79A7")

# Plot accumulation curve
accum_plt <- ggplot() +
  geom_line(data = accum_df, aes(x = sp_id, y = charlen, color = method)) +
  geom_point(data = fail_df, aes(x = sp_id, y = charlen), shape = 4) +
  labs(
    x = "Number of species processed",
    y = "Number of trait names",
    color = "Method"
  ) +
  scale_color_manual(values = cbp1, labels = method_labels, breaks = method_names) +
  theme_bw() +
  theme(
    legend.position = "bottom",
    legend.margin = margin(t = 0, unit = "cm")
  ) +
  guides(color = guide_legend(nrow = 2))
accum_plt
ggsave(here::here("../../script_output/visualise_d2m_out/accum.png"), accum_plt, width = 2.7, height = 3)

# ===== Trait comparison with traits in key =====

# Get list of traits in the key
key_trait_list <- unlist(strsplit(read_file("../../script_output/process_xper/sdd2charlist/solanum_charlist.txt"), "; "))
key_trait_list

# Extract final list of traits
final_charlists <- lapply(accum_dats, function(dat) {
  # Return the last elements in the charlist history
  unlist(dat$charlist_history[[length(dat$charlist_history)]])
})
final_charlists

# Insert key trait list
final_charlists$key <- key_trait_list
final_charlists

setdiff(intersect(final_charlists$subset, final_charlists$subset_f), final_charlists$key)

# Extract traits found in the key trait list
final_chars_inkey <- lapply(final_charlists, function(charlist) {
  charlist[charlist %in% key_trait_list]
})
final_chars_inkey

# Draw Venn diagram of characteristics
char_venn <- ggVennDiagram(final_charlists) +
  scale_fill_gradient(low = "#ffffff", high = "#333333") +
  labs(
    title = "Venn diagram of final characteristics",
    fill = "Count"
  )
char_venn
ggsave(here::here("../../script_output/visualise_d2m_out/accum_venn.png"), char_venn, width = 5, height = 4, bg = "white")

