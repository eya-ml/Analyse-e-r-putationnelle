from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Configurez le driver Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Ouvrez la page des avis Google Maps
driver.get('https://www.google.com/maps/place/Tim+Hortons/@45.5090828,-73.5674847,17z/data=!3m1!5s0x4cc91a4e60beb311:0xd0d56d497ef47572!4m8!3m7!1s0x4cc91a4e5c5dbd1b:0x9fbe6d174fb79383!8m2!3d45.5090828!4d-73.5649098!9m1!1b1!16s%2Fg%2F11cn0skr_8?entry=ttu')

# Attendez que la page se charge et que les avis soient visibles
driver.implicitly_wait(10)

# Défilez vers le bas pour charger plus d'avis
last_height = driver.execute_script("return document.querySelector('div.m6QErb.DxyBCb').scrollHeight")

while True:
    # Faites défiler vers le bas pour charger plus d'avis
    driver.execute_script("document.querySelector('div.m6QErb.DxyBCb').scrollTo(0, document.querySelector('div.m6QErb.DxyBCb').scrollHeight);")
    time.sleep(2)  # Attendez 2 secondes pour permettre le chargement des avis
    new_height = driver.execute_script("return document.querySelector('div.m6QErb.DxyBCb').scrollHeight")
    if new_height == last_height:  # Si la hauteur n'a pas changé, cela signifie que tous les avis sont chargés
        break
    last_height = new_height

# Trouvez les éléments contenant les avis
reviews = driver.find_elements(By.CSS_SELECTOR, 'div.jftiEf.fontBodyMedium')

# Liste pour stocker les avis
reviews_list = []

for review in reviews:
    try:
        # Extraire le nom de l'auteur de l'avis
        reviewer_name = review.find_element(By.CSS_SELECTOR, 'button > div.d4r55').text
        # Extraire le texte de l'avis
        review_text = review.find_element(By.CSS_SELECTOR, 'span.wiI7pd').text
        # Extraire la note de l'avis
        review_rating = review.find_element(By.CSS_SELECTOR, 'span.kvMYJc').get_attribute('aria-label')
        # Ajouter les détails de l'avis à la liste
        reviews_list.append([reviewer_name, review_rating, review_text])
    except Exception as e:
        print(f"Erreur lors de l'extraction d'un avis : {e}")

# Fermez le driver
driver.quit()

# Créez un DataFrame pandas
df = pd.DataFrame(reviews_list, columns=['Reviewer Name', 'Rating', 'Review'])

# Enregistrez le DataFrame dans un fichier CSV
df.to_csv('reviews.csv', index=False, encoding='utf-8')

print('Les avis ont été enregistrés dans le fichier reviews.csv')

# Explication du choix des librairies :
# - Selenium : Selenium est une bibliothèque populaire pour l'automatisation des navigateurs web.
#              Elle permet de contrôler le navigateur et d'interagir avec les éléments de la page
#              comme si vous le faisiez manuellement.
# - webdriver_manager : Cette bibliothèque simplifie la gestion des drivers de navigateur.
#                       Ici, elle installe automatiquement le driver Chrome nécessaire pour Selenium.
# - pandas : Pandas est une bibliothèque puissante pour la manipulation et l'analyse de données.
#            Elle est utilisée pour créer un DataFrame à partir des avis extraits et pour enregistrer
#            ces données dans un fichier CSV.
# - time : La bibliothèque time est utilisée pour introduire des pauses (delays) afin de permettre au contenu
#          de se charger correctement.
