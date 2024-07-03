import csv
import pandas as pd
from deep_translator import GoogleTranslator
from collections import Counter
import re
import nltk
from nltk.corpus import stopwords

# Télécharger les stopwords de NLTK
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Charger les données des avis depuis un fichier CSV
df = pd.read_csv('reviews.csv')

# Initialiser le traducteur
translator = GoogleTranslator(source='auto', target='en')

# Fonction de nettoyage et de traduction
def clean_and_translate(text):
    # Nettoyer le texte
    text = re.sub(r'[^\w\s]', '', text)  # Enlever la ponctuation
    text = text.lower()  # Mettre en minuscule

    try:
        # Traduire en anglais
        translated = translator.translate(text)
    except Exception as e:
        print(f"Erreur de traduction : {e}")
        translated = text  # Si la traduction échoue, conserver le texte original
    return translated

# Nettoyer et traduire les avis
df['Review_english'] = df['Review'].apply(lambda x: clean_and_translate(x) if pd.notnull(x) else '')

# Fusionner tous les avis en une seule chaîne
all_reviews = ' '.join(df['Review_english'])

# Enregistrer les avis traduits dans un fichier CSV
df.to_csv('reviews_translated.csv', index=False)

# Tokeniser les mots
words = all_reviews.split()

# Filtrer les mots pour enlever les stopwords
filtered_words = [word for word in words if word not in stop_words]

# Compter la fréquence des mots
word_counts = Counter(filtered_words)

# Afficher les 10 mots les plus fréquents
print(word_counts.most_common(10))

# Enregistrer les résultats dans un fichier CSV
word_counts_df = pd.DataFrame(word_counts.items(), columns=['Word', 'Frequency'])
word_counts_df.to_csv('word_frequencies.csv', index=False, encoding='utf-8')

print('L\'analyse de contenu a été enregistrée dans le fichier word_frequencies.csv')

# Explication du choix des librairies :
# - csv : La bibliothèque csv permet de manipuler facilement les fichiers CSV pour la lecture et l'écriture.
# - pandas : Pandas est une bibliothèque puissante pour la manipulation et l'analyse de données. Elle est utilisée pour charger les avis depuis un fichier CSV, les nettoyer, les traduire, et stocker les résultats.
# - deep_translator : Cette bibliothèque permet d'utiliser divers services de traduction. Ici, elle est utilisée pour traduire les avis en anglais.
# - collections.Counter : Counter est utilisé pour compter la fréquence des mots après le nettoyage et la traduction des avis.
# - re : La bibliothèque re (expressions régulières) est utilisée pour nettoyer les textes en enlevant la ponctuation.
# - nltk : NLTK (Natural Language Toolkit) est une bibliothèque pour le traitement du langage naturel. Elle est utilisée ici pour télécharger et utiliser les stopwords en anglais afin de filtrer les mots fréquents.
