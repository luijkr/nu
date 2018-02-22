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

# number of observations per class
df %>%
  group_by(category) %>%
  summarize(n = n()) %>%
  ggplot(aes(x = category, y = n)) +
  geom_bar(stat = 'identity') +
  theme_bw()

# article structure
words <- sapply(df$text, function(x) unlist(strsplit(x, split = ' ')))
df$nwords <- sapply(words, length)
df$nwords_unique <- sapply(words, function(x) length(unique(x)) / length(x))
df$nchars <- sapply(df$text, str_length)
df$nchars_word <- df$nchars / df$nwords
df$quotes <- str_count(df$text, pattern = '"')
df$quotes_word <- df$quotes / df$nwords

# number of words
ggplot(df, aes(x = category, y = nwords)) +
  geom_boxplot() +
  scale_y_log10() +
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
