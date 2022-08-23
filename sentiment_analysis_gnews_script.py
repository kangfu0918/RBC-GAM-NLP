# -*- coding: utf-8 -*-
"""Sentiment analysis Gnews.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1DEAyduJY4XeRBN4Dsfi95eVrYojKyeTZ
"""

# Google news api library install
!pip install gnews

# Import required library
from gnews import GNews
import pandas as pd
import datetime
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
sid = SentimentIntensityAnalyzer()
import re
import string
import unicodedata
!pip install unidecode
import unidecode

# Google news setting and search for "Microsoft" news
google_news = GNews(language='en', country='US')
news = google_news.get_news('Microsoft')
# Length of news set
len(news)

# Loop to store all news information into four lists: title, text, date, and author
news_title=[]
news_text=[]
news_date=[]
news_author=[]
for i in range(len(news)):
    article = google_news.get_full_article(
    news[i]['url'])
    if article != None: 
        news_title.append(article.title)
        news_text.append(article.text)
        news_author.append(article.authors)
        news_date.append(news[i]['published date'])

# Create a DataFrame for all the microsoft news
news_df=pd.DataFrame(list(zip(news_title,news_date,news_author,news_text)),columns=['title','publish date', 'author','text'])
# Display the news dataframe
news_df

# Turn publish date into python date type named as datetime 
news_df['datetime']=news_df['publish date'].apply(lambda x: datetime.datetime.strptime(x, '%a, %d %b %Y %H:%M:%S %Z'))

# Drop the publish date
news_df=news_df.drop(columns=['publish date'])
news_df

# Create a new column date and sorted by the date value
news_df['date']=news_df['datetime'].apply(lambda x: x.date())
news_df=news_df.sort_values('date', ascending=False).drop(columns=['datetime'])
news_df

# Define a text preprocessing function called preprocess
def preprocess(text):
  text=text.lower()
  text=re.sub(r'[^\w\s]', '', text)
  text=unidecode.unidecode(text)
  text=re.sub(r'\d+', '', text)
  return text

# Calculate the polarity scores using Vader
news_df['text']=news_df['text'].apply(lambda x: preprocess(x))
news_df['polarity scores']=news_df['text'].apply(lambda x: sid.polarity_scores(x))
news_df['compound scores']=news_df['polarity scores'].apply(lambda x: x['compound'])

# Print the scores dataframe
news_df

# Estimate the average Vader polarity scores group by date
news_df_grouped=news_df.groupby('date')
mean_df=news_df_grouped.mean()
print(mean_df.head(10))

# Reset the index of mean polarity score dataframe and display it
mean_df=mean_df.reset_index()
mean_df

# Install and import Yahoo Finance api library
!pip install yfinance
import yfinance as yf

# Extract Microsoft stock information from the Yahoo Fiance API
stocks = ['MSFT']
start_date = '2022-05-23'
stop_date = '2022-08-08'
stock_list = " ".join(stocks)
table = yf.download(stock_list, start=start_date, end=stop_date)['Adj Close']

# Construct stock dataframe 
df_stock=pd.DataFrame(table)

# Data Cleaning
df_stock=df_stock.reset_index().rename(columns={'Adj Close':'Close Price'})
df_stock['date']=df_stock['Date'].apply(lambda x:x.date())
df_stock.drop(columns=['Date'])

# Sort stock dataframe by date in descending order
df_stock=df_stock.sort_values('date', ascending=False).drop(columns=['Date'])
df_stock

# Print news dataframe information
news_df.info()

# Merge stock and news dataframe 
df_final=pd.merge(mean_df,df_stock,how='left',on='date').dropna()
df_final

# Calculate daily percentage change of stock price  
df_final['Close Price Last Day']=df_final['Close Price'].shift(1)
df_final['Return']=(df_final['Close Price']-df_final['Close Price Last Day'])/df_final['Close Price Last Day']
df_final=df_final.dropna()
df_final

# Measure the volatility of stock and news (standard deviation of changes)
volatility_stock=df_final['Return'].std()
print(volatility_stock)
volatility_polarity=df_final['compound scores'].std()
print(volatility_polarity)

# Estimate the correlations betwen stock return and polarity scores 
import scipy.stats as stats
r = stats.pearsonr(df_final['compound scores'], df_final['Return'])
print("Pearson Correlation coefficient:"+str(r[0]))