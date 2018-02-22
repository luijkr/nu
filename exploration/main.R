setwd('/home/rluijk/Documents/gitrepos/nu/')
options('stringsAsFactors' = FALSE)
library(ggplot2)
library(dplyr)
library(stringr)
library(readr)
library(rjson)

# list file paths
paths <- list.files('articles', full.names = TRUE)

# read files
articles <- lapply(paths, function(fname) try(fromJSON(file = fname), silent = TRUE))
articles <- articles[!sapply(articles, is, 'try-error')]

# create data frame
df <- data.frame(
  url = sapply(articles, function(x) x$article_url),
  category = sapply(articles, function(x) x$article_category),
  text = sapply(articles, function(x) x$article_text),
  title = sapply(articles, function(x) x$article_title)
)

# filter out articles without text
df <- subset(df, text != '')

# filter duplicates
df <- subset(df, !duplicated(url))

# number of observations per class
df %>%
  group_by(category) %>%
  summarize(n = n()) %>%
  ggplot(aes(x = category, y = n)) +
  geom_bar(stat = 'identity') +
  theme_bw()

# article structure
words <- sapply(df$text, function(x) unlist(strsplit(x, split = ' ')))
sentences <- sapply(df$text, function(x) unlist(strsplit(x, split = '.', fixed = TRUE)))
df$nsentences <- sapply(sentences, length)
df$nwords <- sapply(words, length)
df$nwords_sentence = df$nwords / df$nsentences
df$nwords_unique <- sapply(words, function(x) length(unique(x)) / length(x))
df$nchars <- sapply(df$text, str_length)
df$nchars_word <- df$nchars / df$nwords
df$quotes <- str_count(df$text, pattern = '"')
df$quotes_word <- df$quotes / df$nwords

# filter on at least 4 sentences, otherwise it probably is an overview
df <- subset(df, nsentences >= 4)

# number of words
ggplot(df, aes(x = category, y = nwords)) +
  geom_boxplot() +
  scale_y_log10() +
  theme_bw()

# number of sentences
ggplot(df, aes(x = category, y = nsentences)) +
  geom_boxplot() +
  # scale_y_log10() +
  theme_bw()

# number of words per sentence
ggplot(df, aes(x = category, y = nwords_sentence)) +
  geom_boxplot() +
  theme_bw()

# number of unique words / total number of words
ggplot(df, aes(x = category, y = nwords_unique)) +
  geom_boxplot() +
  theme_bw()

# number of characters
ggplot(df, aes(x = category, y = nchars)) +
  geom_boxplot() +
  theme_bw()

# number of characters per word
ggplot(df, aes(x = category, y = nchars_word)) +
  geom_boxplot() +
  # scale_y_log10() +
  theme_bw()

# number of quotations per article
ggplot(df, aes(x = category, y = quotes)) +
  geom_boxplot() +
  theme_bw()

# number of quotations per word
ggplot(df, aes(x = category, y = quotes_word)) +
  geom_boxplot() +
  theme_bw()

# any quotes in article
df %>%
  group_by(category) %>%
  summarize(p = mean(quotes_word > 0))
