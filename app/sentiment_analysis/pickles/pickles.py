import pickle
import os

file_path = os.path.abspath("sentiment_analysis/pickles/models/general_model.pkl")
with open(file_path, 'rb') as file:
  model_overall, cv = pickle.load(file)

file_path = os.path.abspath("sentiment_analysis/pickles/models/fit_models.pkl")
with open(file_path, 'rb') as file:
  model_fit, tfidf_fit = pickle.load(file)

file_path = os.path.abspath("sentiment_analysis/pickles/models/color_models.pkl")
with open(file_path, 'rb') as file:
  model_color, cv_color = pickle.load(file)

file_path = os.path.abspath("sentiment_analysis/pickles/models/quality_models.pkl")
with open(file_path, 'rb') as file:
  model_quality, tfidf_quality = pickle.load(file)

file_path = os.path.abspath("sentiment_analysis/pickles/keywords/fit_words.pkl")
with open(file_path, 'rb') as file:
  fit_words = pickle.load(file)

file_path = os.path.abspath("sentiment_analysis/pickles/keywords/color_words.pkl")
with open(file_path, 'rb') as file:
  color_words = pickle.load(file)

file_path = os.path.abspath("sentiment_analysis/pickles/keywords/quality_words.pkl")
with open(file_path, 'rb') as file:
  quality_words = pickle.load(file)