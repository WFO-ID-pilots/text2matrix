# Install package manager if not installed already
# install.packages("pacman")

# Load necessary packages
pacman::p_load("tidyverse", "here", "jsonlite", "ggVennDiagram", "plotly", "ggwordcloud", "scales")

# Load json
# Data from desc2matrix_accum.py, which populates the initial character
# list by asking the prompt from desc2matrix.py with the first species description
accum_dat <- read_json(here::here("../json_outputs/accum_out_800sp.json"))
# Data from desc2matrix_accum_tab.py, which populates the initial character
# list by asking the LLM to tabulate the characteristics from the first three species descriptions
accum_tab_dat <- read_json(here::here("../json_outputs/accum_tab_out_800sp.json"))
# Data from desc2matrix_accum_followup.py, which is built upon desc2matrix_accum_tab.py
# but asks a 'follow-up question' including words that were omitted from the original description
# to increase trait coverage
accum_f_dat <- read_json(here::here("../json_outputs/accum_followup_out_800sp.json"))

# ===== Generate accumulation curve =====

# Get charlist length histories
accum_charlens <- list(
  c(NA, accum_dat$charlist_len_history), # Insert NA because accum_charlen lacks the 'initial' charlist from tabulation
  accum_tab_dat$charlist_len_history,
  accum_f_dat$charlist_len_history
)

# Get incidences of failures

accum_failures <- sapply(seq_along(accum_dat$data), function(spdat_id) {
  spdat <- accum_dat$data[[spdat_id]]
  if(spdat$status == "success") { NA }
  else { spdat_id + 1 } # + 1 to account for NA
})
accum_tab_failures <- sapply(seq_along(accum_tab_dat$data), function(spdat_id) {
  spdat <- accum_tab_dat$data[[spdat_id]]
  if(spdat$status == "success") { NA }
  else { spdat_id }
})
accum_f_failures <- sapply(seq_along(accum_f_dat$data), function(spdat_id) {
  spdat <- accum_f_dat$data[[spdat_id]]
  if(spdat$status == "success") { NA }
  else { spdat_id }
})
fail_df <- tibble(
  sp_id = c(NA, accum_failures, NA, accum_tab_failures, NA, accum_f_failures), # First is NA, corresponding to the missing initial tabulation
  charlen = do.call(c, unlist(accum_charlens, recursive=FALSE))
)

# Method names
method_names <- c("accum", "accum_tab", "accum_f")
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
    "accum" = "Without initial tabulation",
    "accum_tab" = "With initial tabulation",
    "accum_f" = "With initial tabulation and followup question"),
    breaks = c("accum", "accum_tab", "accum_f")) +
  theme_bw() +
  theme(legend.position = "bottom") +
  guides(color = guide_legend(nrow = 3, byrow = FALSE))
accum_plt
ggsave(here::here("figures/accum_curve_800.png"), accum_plt, width = 5, height = 4)

# ===== Inspect final trait list for the runs =====

# ===== Venn diagram of characteristics =====

# Gather charlist histories
accum_charhist <- list(
  accum_dat$charlist_history,
  accum_tab_dat$charlist_history,
  accum_f_dat$charlist_history
)

# Extract final charlists
final_chars <- lapply(accum_charhist, function(charhist) {
  final_charlist <- unlist(charhist[[length(charhist)]])
  unname(sapply(final_charlist, function(char) { sub("color", "colour", char, ignore.case = TRUE) })) # Make spelling variants uniform
})
names(final_chars) <- c("accum", "accum_tab", "accum_f")

# paste(final_chars[["accum"]], collapse = ", ")
# paste(final_chars[["accum_tab"]], collapse = ", ")
# paste(final_chars[["accum_f"]], collapse = ", ")

# Draw Venn diagram of characteristics
char_venn <- ggVennDiagram(final_chars,
              category.names = c("A", "AT", "AF")) +
  scale_fill_gradient(low = "#ffffff", high = "#333333") +
  labs(
    title = "Venn diagram of final characteristics,\nwith merged spelling variants",
    fill = "Count"
  )
char_venn
ggsave(here::here("figures/characters_venn.png"), char_venn, width = 5, height = 4, bg = "white")

# ===== Venn diagram of words =====

# Decompose to individual words and find shared words
final_chars_words <- lapply(final_chars, function(charlist) {
  words <- unlist(lapply(charlist, function(char) { strsplit(char, " ") }))
})

# Draw Venn diagram of words
char_word_venn <- ggVennDiagram(final_chars_words,
                           category.names = c("A", "AT", "AF")) +
  scale_fill_gradient(low = "#ffffff", high = "#333333") +
  labs(
    title = "Venn diagram of words in the final characteristics,\nwith merged spelling variants",
    fill = "Count"
  )
char_word_venn
ggsave(here::here("figures/characters_words_venn.png"), char_word_venn, width = 5, height = 4, bg = "white")

# ===== Word clouds =====

# Extract word blobs from the trait histories of the runs
char_blobs <- list(
  accum = unlist(accum_dat$charlist_history),
  accum_tab = unlist(accum_tab_dat$charlist_history),
  accum_f = unlist(accum_f_dat$charlist_history)
)

# Separate into words
word_blobs <- lapply(char_blobs, function(char_blob) {
  unlist(lapply(char_blob, function(char) { str_split(char, " ") }))
})

# Count words
word_dfs <- lapply(names(word_blobs), function(blob_name) {
  blob <- word_blobs[[blob_name]]
  word_tab <- sort(table(blob))
  words <- names(word_tab)
  counts <- unlist(word_tab, use.names = FALSE)
  order <- seq(0, length(words) - 1)
  tibble(
    method = factor(rep(blob_name, length(words)), levels = c("accum", "accum_tab", "accum_f")),
    word = words,
    word_count = as.numeric(counts),
    freq_category = as.factor((order / length(words)) %/% (1/3))
  )
})

word_df <- bind_rows(word_dfs)

word_df

# Plot word clouds

facet_labeller <- c("Without tabulation", "With tabulation", "With tabulation & followup")
names(facet_labeller) <- c("accum", "accum_tab", "accum_f")

set.seed(1)
word_cloud <- ggplot(word_df, aes(label = word, size = sqrt(word_count + 50), y = freq_category)) +
  geom_text_wordcloud() +
  scale_size_area(max_size = 7) +
  theme_minimal() +
  facet_wrap(~ method, labeller = labeller(method = facet_labeller)) +
  theme(
    strip.text.x = element_text(size = 8),
    axis.title.y = element_blank(),
    axis.text.y = element_blank(),
    axis.ticks.y = element_blank(),
    panel.grid.major=element_blank(),
    panel.grid.minor=element_blank()
  )
word_cloud
ggsave(here::here("figures/word_clouds.png"), word_cloud, width = 8, height = 8, bg = "white")
