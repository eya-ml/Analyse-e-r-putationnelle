import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import nltk
from nltk.corpus import stopwords
from transformers import pipeline
from wordcloud import WordCloud
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Télécharger les ressources nécessaires
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Charger les données
data_path = 'review.csv'
Data = pd.read_csv(data_path, encoding='utf-8')

# Titre de l'application
st.title("Analyse e-réputationnelle de Tim Hortons")

# Convertir la colonne 'Rating' en numérique, en gérant les erreurs
Data['Rating'] = pd.to_numeric(Data['Rating'].str.replace('etoile', '').str.replace('étoiles', '').str.strip(), errors='coerce')
Data['Rating'] = Data['Rating'].astype('Int64', errors='ignore')

# Initialiser le pipeline d'analyse des sentiments
sentiment_pipeline = pipeline("sentiment-analysis")

def get_sentiment_advanced(review):
    if isinstance(review, str):
        result = sentiment_pipeline(review[:512])  # Limiter à 512 tokens
        sentiment = result[0]['label']
        if sentiment == 'POSITIVE':
            return 'Positive'
        elif sentiment == 'NEGATIVE':
            return 'Negative'
        else:
            return 'Neutral'
    else:
        return 'Neutral'

# S'assurer que 'Review_english' est une chaîne avant d'appliquer l'analyse des sentiments
Data['Review_english'] = Data['Review_english'].astype(str)
Data['Sentiment'] = Data['Review_english'].apply(get_sentiment_advanced)

# Calculer les pourcentages des sentiments
sentiment_counts = Data['Sentiment'].value_counts(normalize=True) * 100
st.write("Sentiment Analysis Results:")
st.write(sentiment_counts)

# Calculer les pourcentages des sentiments
positive_count = (Data['Sentiment'] == 'Positive').sum()
negative_count = (Data['Sentiment'] == 'Negative').sum()
neutral_count = (Data['Sentiment'] == 'Neutral').sum()
total_reviews = len(Data)
positive_percentage = (positive_count / total_reviews) * 100
negative_percentage = (negative_count / total_reviews) * 100
neutral_percentage = (neutral_count / total_reviews) * 100

st.write(f"Positive: {positive_percentage:.2f}%")
st.write(f"Negative: {negative_percentage:.2f}%")
st.write(f"Neutral: {neutral_percentage:.2f}%")

# Gérer les valeurs non-string potentielles dans la colonne 'Review_english'
all_reviews = ' '.join([str(review) for review in Data['Review_english']])

# Tokeniser les mots
words = all_reviews.split()

# Définir les stopwords en anglais
stop_words = set(stopwords.words('english'))

# Filtrer les mots pour enlever les stopwords
filtered_words = [word for word in words if word.lower() not in stop_words]

# Compter la fréquence des mots
word_counts = Counter(filtered_words)

# Afficher les 10 mots les plus fréquents
st.write("Top 10 most frequent words:")
st.write(word_counts.most_common(10))

# Générer le nuage de mots
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(filtered_words))

# Afficher le nuage de mots
fig, ax = plt.subplots(figsize=(10, 5))
ax.imshow(wordcloud, interpolation='bilinear')
ax.axis('off')
st.pyplot(fig)

# Options de personnalisation dans la barre latérale
st.sidebar.title("Options de personnalisation")
st.sidebar.write("Personnalisez vos graphiques ici!")
color = st.sidebar.color_picker('Choisissez une couleur', '#00f900')

# Créer un diagramme à barres pour les fréquences des évaluations
fig, ax = plt.subplots(figsize=(10, 6))
rating_counts = Data['Rating'].value_counts().sort_index()
ax.bar(rating_counts.index.astype(int), rating_counts.values, color=color)
ax.set_xlabel('Rating')
ax.set_ylabel('Frequency')
ax.set_title('Frequency of Each Rating Value')
ax.set_xticks(rating_counts.index.astype(int))
ax.grid(axis='y')
st.pyplot(fig)

# Créer un diagramme à barres pour la distribution des sentiments
fig, ax = plt.subplots(figsize=(10, 6))
sentiment_counts.plot(kind='bar', color=color, ax=ax)
ax.set_xlabel('Sentiment')
ax.set_ylabel('Percentage')
ax.set_title('Distribution of Sentiments')
ax.grid(axis='y')
st.pyplot(fig)

def extract_nouns(review):
    if isinstance(review, str):
        blob = TextBlob(review)
        pos_tags = blob.tags
        nouns = [word for word, pos in pos_tags if pos in ['NN', 'NNS']]
        return ' '.join(nouns)
    else:
        return ''

def correct_spelling(text):
    if isinstance(text, str):
        blob = TextBlob(text)
        return str(blob.correct())
    else:
        return ''

Data['Review_english'] = Data['Review_english'].apply(correct_spelling)
Data['Nouns'] = Data['Review_english'].apply(extract_nouns)

# Obtenir les fréquences des mots pour chaque mot dans la colonne Nouns
word_counts = pd.Series(' '.join(Data['Nouns']).split()).value_counts()
word_counts = word_counts[word_counts > 1]
sorted_word_counts = word_counts.sort_values(ascending=False)

# Afficher les fréquences des mots sous forme de diagramme à barres
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(sorted_word_counts.index, sorted_word_counts.values, color=color)
ax.set_xlabel('Word')
ax.set_ylabel('Frequency')
ax.set_title('Frequency of Words')
st.pyplot(fig)

# Initialiser l'analyseur de sentiment VADER
analyzer = SentimentIntensityAnalyzer()

# Définir les mots-clés pour chaque catégorie
keywords = {
    'staff': ['staff', 'cashier', 'employees', 'employee', 'workers', 'service', 'attitude'],
    'cuisine': ['food', 'portions', 'cappuccino', 'chocolate', 'cuisine', 'repas', 'plat', 'coffee', 'drinks', 'breakfast', 'lunch', 'meal', 'milk', 'dinner', 'tea', 'cinnamon', 'sandwich', 'express', 'vanilla', 'menu', 'taste'],
    'cleanliness': ['clean', 'bathroom', 'machine', 'cockroaches', 'propreté', 'propre', 'sale', 'hygienic', 'dirty', 'cleaning', 'toilet'],
}

def get_sentiment_vader(text):
    if isinstance(text, str):
        vs = analyzer.polarity_scores(text)
        if vs['compound'] >= 0.05:
            return 'Positive'
        elif vs['compound'] <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'
    else:
        return 'Neutral'

def filter_reviews_by_keywords(review, keywords):
    words = review.split()
    filtered_review = ' '.join([word for word in words if word.lower() in keywords])
    return filtered_review

def analyze_sentiment_by_category(data, keywords):
    for category, words in keywords.items():
        data[category + '_filtered'] = data['Review_english'].apply(lambda review: filter_reviews_by_keywords(review, words))
        data[category + '_sentiment'] = data[category + '_filtered'].apply(get_sentiment_vader)
    return data

# Appliquer l'analyse des sentiments par catégorie
Data = analyze_sentiment_by_category(Data, keywords)

# Afficher les résultats
st.write("Sentiment Analysis by Category Results:")
st.write(Data.head())

# Enregistrer les résultats dans un nouveau fichier CSV
output_file_path = 'review_with_sentiment_by_category.csv'
Data.to_csv(output_file_path, index=False)

def analyze_word_sentiment(word):
    result = sentiment_pipeline(word)
    sentiment = result[0]['label']
    if sentiment == 'POSITIVE':
        return 'Positive'
    elif sentiment == 'NEGATIVE':
        return 'Negative'
    else:
        return 'Neutral'

def generate_color(word, font_size, position, orientation, random_state=None, **kwargs):
    sentiment = analyze_word_sentiment(word)
    if sentiment == 'Positive':
        return 'green'
    elif sentiment == 'Negative':
        return 'red'
    else:
        return 'gray'

def generate_wordcloud(text, title):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud.recolor(color_func=generate_color), interpolation='bilinear')
    ax.set_title(title)
    ax.axis('off')
    st.pyplot(fig)

# Filtrer les avis par catégorie et générer des nuages de mots
for category, words in keywords.items():
    Data[category + '_filtered'] = Data['Review_english'].apply(lambda review: filter_reviews_by_keywords(review, words))
    category_text = ' '.join(Data[category + '_filtered'])
    generate_wordcloud(category_text, f'Nuage de Mots pour {category.capitalize()}')

import re
from datetime import datetime, timedelta

# Fonction pour convertir les dates en jours
def convert_to_days(date_str):
    date_str = date_str.replace('un', '1').replace('une', '1')

    today = datetime.now()

    match = re.search(r'(\d+)\s*(jour|jours|mois|an|année|années)', date_str)
    if match:
        num = int(match.group(1))
        unit = match.group(2)

        if 'jour' in unit:
            return num
        elif 'mois' in unit:
            past_date = today - pd.DateOffset(months=num)
            return (today - past_date).days
        elif 'an' in unit or 'année' in unit ou 'années' in unit:
            return num * 365
    return None

Data['Date_in_days'] = Data['Date'].apply(convert_to_days)

# Vérifier le type de données de la colonne 'Date_in_days'
st.write(Data['Date_in_days'])

# Classifier les avis par jour
reviews_by_date_sorted = Data.groupby('Date_in_days').apply(lambda x: x['Sentiment'].value_counts()).unstack().fillna(0).sort_index()
st.write(reviews_by_date_sorted)

# Enregistrer les résultats dans un nouveau fichier CSV
output_file_path = 'reviews_by_date.csv'
reviews_by_date_sorted.to_csv(output_file_path)

st.write('Les avis ont été classés par date et enregistrés dans le fichier reviews_by_date.csv')

# Afficher les données sous forme de graphique
fig, ax = plt.subplots(figsize=(12, 6))
reviews_by_date_sorted.plot(kind='bar', stacked=True, ax=ax)
ax.set_title('Sentiment Analysis of Reviews Over Time')
ax.set_xlabel('Date')
ax.set_ylabel('Number of Reviews')
ax.set_xticks(reviews_by_date_sorted.index)
ax.set_xticklabels(reviews_by_date_sorted.index, rotation=45)
ax.legend(title='Sentiment')
ax.grid(True)
st.pyplot(fig)

# Afficher l'évolution des sentiments au fil du temps
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(reviews_by_date_sorted.index, reviews_by_date_sorted['Positive'], label='Positive', color='green')
ax.plot(reviews_by_date_sorted.index, reviews_by_date_sorted['Negative'], label='Negative', color='red')
ax.set_xlabel('Date')
ax.set_ylabel('Number of Reviews')
ax.set_title('Sentiment Analysis of Reviews Over Time')
ax.legend()
ax.grid(True)
ax.set_xticklabels(reviews_by_date_sorted.index, rotation=45)
st.pyplot(fig)

# Charger les données des franchises
data_franchise1 = pd.read_csv('review.csv')
data_franchise2 = pd.read_csv('review_peel.csv')

# Analyser les sentiments pour chaque franchise
data_franchise1['Sentiment'] = data_franchise1['Review_english'].apply(get_sentiment)
data_franchise2['Sentiment'] = data_franchise2['Review_english'].apply(get_sentiment)

# Comparer les sentiments
sentiments_franchise1 = data_franchise1['Sentiment'].value_counts(normalize=True)
sentiments_franchise2 = data_franchise2['Sentiment'].value_counts(normalize=True)

# Visualiser la comparaison
sentiments = pd.DataFrame({
    'Franchise 1': sentiments_franchise1,
    'Franchise 2': sentiments_franchise2
}).fillna(0)

fig, ax = plt.subplots(figsize=(10, 6))
sentiments.plot(kind='bar', ax=ax)
ax.set_title('Comparaison des Sentiments des Avis entre deux Franchises')
ax.set_ylabel('Proportion des Avis')
st.pyplot(fig)

data_franchise1['Date_in_days'] = data_franchise1['Date'].apply(convert_to_days)
data_franchise2['Date_in_days'] = data_franchise2['Date'].apply(convert_to_days)

data_franchise1['Category'] = data_franchise1['Review'].apply(get_sentiment_vader)
data_franchise2['Category'] = data_franchise2['Review'].apply(get_sentiment_vader)

# Supprimer les lignes avec des dates non valides
data_franchise1.dropna(subset=['Date_in_days'], inplace=True)
data_franchise2.dropna(subset=['Date_in_days'], inplace=True)

# Classifier les avis par jour et par catégorie
reviews_by_category_date1 = data_franchise1.groupby(['Date_in_days', 'Category']).apply(lambda x: x['Sentiment'].value_counts()).unstack().fillna(0)
reviews_by_category_date2 = data_franchise2.groupby(['Date_in_days', 'Category']).apply(lambda x: x['Sentiment'].value_counts()).unstack().fillna(0)

# Enregistrer les résultats dans de nouveaux fichiers CSV
reviews_by_category_date1.to_csv('reviews_by_category_date1.csv')
reviews_by_category_date2.to_csv('reviews_by_category_date2.csv')

# Visualisation des résultats
categories = keywords.keys()
for category in categories:
    if category in reviews_by_category_date1.index.get_level_values('Category'):
        fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(15, 14), sharex=True)

        # Franchise 1
        category_data1 = reviews_by_category_date1.xs(category, level='Category', drop_level=False)
        category_data1.plot(kind='bar', stacked=True, ax=axes[0], title=f"Sentiments over time for {category} (Franchise 1)")
        axes[0].set_ylabel('Number of Reviews')
        axes[0].set_xlabel('Date in Days')

        # Franchise 2
        category_data2 = reviews_by_category_date2.xs(category, level='Category', drop_level=False)
        category_data2.plot(kind='bar', stacked=True, ax=axes[1], title=f"Sentiments over time for {category} (Franchise 2)")
        axes[1].set_ylabel('Number of Reviews')
        axes[1].set_xlabel('Date in Days')

        st.pyplot(fig)

# Extraire les avis négatifs pour analyse
negative_reviews = data_franchise1[data_franchise1['Sentiment'] == 'Negative']['Review_english']

# Analyser les thèmes récurrents dans les avis négatifs
vectorizer = CountVectorizer(stop_words='english')
X = vectorizer.fit_transform(negative_reviews)
word_counts = Counter(vectorizer.get_feature_names_out())

# Afficher les 10 mots les plus fréquents dans les avis négatifs
common_words = word_counts.most_common(10)
st.write("Mots les plus fréquents dans les avis négatifs:")
st.write(common_words)

# Proposer des actions concrètes (exemple simple)
recommendations = {
    "service": "Former le personnel pour améliorer l'interaction avec les clients.",
    "qualité": "Assurer un contrôle de qualité plus rigoureux des produits.",
    "attente": "Optimiser les processus pour réduire le temps d'attente des clients.",
}

# Prioriser les recommandations
priority = {
    "service": 1,   # Impact élevé, faisabilité moyenne
    "qualité": 2,   # Impact moyen, faisabilité élevée
    "attente": 3    # Impact élevé, faisabilité basse
}

# Créer un DataFrame pour les recommandations
df_recommendations = pd.DataFrame(list(recommendations.items()), columns=['Problème', 'Recommandation'])
df_recommendations['Priorité'] = df_recommendations['Problème'].map(priority)

# Trier les recommandations par priorité
df_recommendations.sort_values(by='Priorité', inplace=True)

# Afficher les recommandations
st.write(df_recommendations)

# Enregistrer les recommandations dans un fichier CSV
df_recommendations.to_csv('recommendations.csv', index=False, encoding='utf-8')
st.write("Les recommandations ont été enregistrées dans le fichier recommendations.csv")

# Explication du choix des bibliothèques :
# - streamlit : Streamlit permet de créer des applications web interactives pour la visualisation de données. Il est utilisé ici pour créer une interface utilisateur interactive.
# - pandas : Pandas est une bibliothèque puissante pour la manipulation et l'analyse de données. Elle est utilisée pour charger, nettoyer, et analyser les avis.
# - numpy : Numpy est une bibliothèque pour le calcul scientifique. Elle est utilisée pour effectuer des opérations numériques sur les données.
# - matplotlib : Matplotlib est une bibliothèque de visualisation de données. Elle est utilisée pour créer des graphiques et des diagrammes.
# - collections.Counter : Counter est utilisé pour compter la fréquence des mots après le nettoyage des avis.
# - nltk : NLTK (Natural Language Toolkit) est une bibliothèque pour le traitement du langage naturel. Elle est utilisée ici pour télécharger et utiliser les stopwords en anglais afin de filtrer les mots fréquents.
# - transformers : Transformers est utilisé pour le pipeline d'analyse des sentiments. Il permet de classifier les sentiments des avis.
# - wordcloud : WordCloud est utilisé pour générer des nuages de mots à partir des avis nettoyés.
# - textblob : TextBlob est utilisé pour le traitement du texte, y compris la correction orthographique et l'extraction de noms.
# - vaderSentiment : VADER Sentiment est un outil de traitement de langage naturel qui permet de déterminer le sentiment des textes en utilisant une méthode basée sur les règles.
