import pandas as pd
import numpy as np
import os
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template, send_file, request
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer

app = Flask(__name__)

class ThematicWordCloudGenerator:
    def __init__(self, data_file='data.csv'):
        
        self.df = pd.read_csv(data_file) #loads data saved in csv file
        
        # Preprocess clean content
        self.df['clean_content'] = self.df['clean_content'].fillna('').astype(str)
        
        # Prepare TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            stop_words='english', 
            max_features=1000
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df['clean_content'])
        
        #feature names
        self.feature_names = self.vectorizer.get_feature_names_out()
    
    def generate_thematic_wordcloud(self, theme):
       
        theme_words = self._extract_theme_related_words(theme) #loads name related to theme
        
        #WORD CLOUD GENERATION
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white', 
            max_words=100, 
            colormap='viridis'
        ).generate(" ".join(theme_words))
        
        #saves word cloud
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig('static/wordcloud.png')
        plt.close()
    
    def _extract_theme_related_words(self, theme):
        
        theme_docs = self.df[self.df['clean_content'].str.contains(theme, case=False)]
        
        
        if theme_docs.empty:
            theme_docs = self.df
        
        #vctorizes theme-related documents
        theme_tfidf = self.vectorizer.transform(theme_docs['clean_content'])
        
        #top TF-IDF words
        theme_words = []
        for doc in theme_tfidf:
            #top words for this document
            sorted_indices = doc.toarray()[0].argsort()[::-1]
            top_words = [self.feature_names[i] for i in sorted_indices[:50]]
            theme_words.extend(top_words)
        
        return theme_words

#initialize generator
thematic_generator = ThematicWordCloudGenerator()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/wordcloud', methods=['POST'])
def generate_wordcloud():
    theme = request.form.get('query', '').lower()
    
    try:
        
        thematic_generator.generate_thematic_wordcloud(theme)           #generates thematic word cloud
        return send_file('static/wordcloud.png', mimetype='image/png')
    except Exception as e:
        print(f"Error generating word cloud: {e}")
        return "An error occurred", 500

#ensures directories exist
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)

#create templates
with open('templates/index.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Thematic Word Cloud Generator</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        #wordcloud { max-width: 100%; margin-top: 20px; }
        #search-container { display: flex; margin-bottom: 20px; }
        #search-input { flex-grow: 1; padding: 10px; }
        #search-btn { padding: 10px 20px; }
    </style>
</head>
<body>
    <h1>Thematic Word Cloud Generator</h1>
    
    <div id="search-container">
        <input type="text" id="search-input" placeholder="Enter a theme">
        <button id="search-btn">Generate Word Cloud</button>
    </div>
    
    <div id="wordcloud-container">
        <img id="wordcloud" src="" alt="Word Cloud">
    </div>

    <script>
    $(document).ready(function() {
        $('#search-btn').click(function() {
            var query = $('#search-input').val();
            
            $.ajax({
                url: '/wordcloud',
                method: 'POST',
                data: {query: query},
                success: function(response) {
                    $('#wordcloud').attr('src', '/static/wordcloud.png?' + new Date().getTime());
                },
                error: function() {
                    alert('Error generating word cloud for: ' + query);
                }
            });
        });
    });
    </script>
</body>
</html>
''')

if __name__ == "__main__":
    app.run(debug=True)