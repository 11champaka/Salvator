# Salvator
analysis_and_web.py : 
Salenium extracts/scrapes data from chrome search engine on "EU_GRANTS" topic, every 5hours with a scheduler.
NLP techniques are applied for cleaning, tokenization the extracted raw data.
Stores data in data.csv
word_cloud_app.py :
Extracts clean data.
Cleaned data is embedded for representing in higher dimension, on this NLP techniques like topic-modelling, TD-IDF are applied to find relevant words.
Word cloud is created using flask, where end user can fetch a unique word cloud based on search.
