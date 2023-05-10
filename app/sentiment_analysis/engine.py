from collections import Counter
import re
import string
import numpy as np
import pandas as pd
from wordcloud import WordCloud
from string import punctuation
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from fastapi import UploadFile
from io import BytesIO
from database.database import DB_CATEGORY_CODES
from sentiment_analysis.pickles.pickles import model_overall, cv, model_fit, tfidf_fit, model_color, cv_color, model_quality, tfidf_quality
from sentiment_analysis.pickles.pickles import fit_words, color_words, quality_words

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

stopwords_list = set(stopwords.words('english') + list(punctuation))
lemma = WordNetLemmatizer()

def clean_review(review):
  """
    Applies the preprocessing to the reviews
  """
  review = re.sub("[^a-zA-Z]", " ", review)
  review = review.translate(str.maketrans("", "", string.punctuation))
  review = review.lower()
  review = word_tokenize(review)
  review = [w for w in review if w not in stopwords_list]
  review = [lemma.lemmatize(w) for w in review]
  review = [w for w in review if len(w) > 1]
  return ' '.join(review)

def classify_review(review):
  """
    Classifies the reviews into 3 categories: fit, color or quality
  """
  words = set(review.split())
  categories = []

  if any(word in words for word in fit_words):
      categories.append(DB_CATEGORY_CODES['FIT']) 
  if any(word in words for word in color_words):
      categories.append(DB_CATEGORY_CODES['COLOR'])
  if any(word in words for word in quality_words):
      categories.append(DB_CATEGORY_CODES['QUALITY'])
  if len(categories) == 0:
      categories.append(DB_CATEGORY_CODES['OTHER'])
  return categories

def generate_score(df_original, df_specific, model, vectorizer, prediction_type):
  """
    Predicts the sentiment of each review and stores them in a new column of the Dataframe
  """
  
  X = vectorizer.transform(df_specific['reviewTextPreprocessed'])
  y_pred = model.predict(X)
  df_specific[prediction_type] = y_pred
  score = np.mean(y_pred)
  df_original.loc[:, prediction_type] = df_specific.loc[:, prediction_type]
  return score

def generate_word_count(df: pd.DataFrame):
  text = ' '.join(df['reviewTextPreprocessed'])
  word_count = Counter(text.split())
  word_count = word_count.most_common(50)
  word_count = {word: {'count': count} for word, count in word_count}
  return word_count

def generate_category_word_count(df: pd.DataFrame, filter_list_1, filter_list_2):
  text = ' '.join(df['reviewTextPreprocessed'])
  word_count = Counter(text.split())
  
  word_count = word_count.most_common(30)
  word_count = {word: {'count': count} for word, count in word_count}
  return word_count

def generate_wordcloud(df: pd.DataFrame):
  """
    Generates the wordcloud
  """
  text = ' '.join(df['reviewTextPreprocessed'])

  wordcloud = WordCloud(background_color='white', width=800, height=400, max_words=200, stopwords=stopwords_list, colormap='inferno').generate(text)
  plt.imshow(wordcloud, interpolation='bilinear')
  plt.axis('off')
  image_file = BytesIO()
  plt.savefig(image_file, format='png')
  image_file.seek(0)
  image_data = image_file.read()
  return image_data
    
def predict(file: UploadFile):
  df = pd.read_csv(file.file)
  df.rename(columns={0: 'reviewText'})
  df['reviewText'] = df['reviewText'].fillna('')
  df['reviewTextPreprocessed'] = df['reviewText'].apply(clean_review)
  df['category'] = df['reviewTextPreprocessed'].apply(classify_review)
  df = df.reset_index(drop=False)
  df = df.rename(columns={'index': 'reviewNumber'})

  fit_df = df[df['category'].apply(lambda x: DB_CATEGORY_CODES['FIT'] in x)].copy()
  color_df = df[df['category'].apply(lambda x: DB_CATEGORY_CODES['COLOR'] in x)].copy()
  quality_df = df[df['category'].apply(lambda x: DB_CATEGORY_CODES['QUALITY'] in x)].copy()

  df['reviewTextPreprocessed'] = df['reviewTextPreprocessed'].fillna('')
  df['category'] = df['category'].fillna('')

  wordcloud = generate_wordcloud(df)

  overall_score = generate_score(df, df, model_overall, cv, 'overall')
  fit_score = generate_score(df, fit_df, model_fit, tfidf_fit, 'fit')
  color_score = generate_score(df, color_df, model_color, cv_color, 'color')
  quality_score = generate_score(df, quality_df, model_quality, tfidf_quality, 'quality')

  word_count = generate_word_count(df)
  
  predictions = {
    "scores": {
      "overall_score": overall_score,
      "fit_score": fit_score,
      "color_score": color_score,
      "quality_score": quality_score
    },
    "number_of_reviews": {
      "total_reviews": df.shape[0],
      "fit_reviews": fit_df.shape[0],
      "color_reviews": color_df.shape[0],
      "quality_reviews": quality_df.shape[0],
    }
  }

  report_metadata = {
    "dataset_title": file.filename
  }

  df = df.fillna(value=-1)
  reviews_list = df.to_dict(orient='records')

  return predictions, report_metadata, reviews_list, word_count, wordcloud