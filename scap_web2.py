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
driver.get('https://www.google.com/maps/place/Tim+Hortons/@45.5069683,-73.5686557,17z/data=!4m8!3m7!1s0x4cc91a4f471ed545:0x283afc2991de7194!8m2!3d45.5069683!4d-73.5686557!9m1!1b1!16s%2Fg%2F11b5wn9szd?authuser=0&hl=fr&entry=ttu')

# Attendez que la page se charge et que les avis soient visibles
time.sleep(10)

# Trouvez l'élément contenant les avis
scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div.m6QErb.DxyBCb')

# Défilez vers le bas pour charger plus d'avis
last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)

while True:
    driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", scrollable_div)
    time.sleep(2)
    new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
    if new_height == last_height:
        break
    last_height = new_height

# Trouvez les éléments contenant les avis
reviews = driver.find_elements(By.CSS_SELECTOR, 'div.jftiEf.fontBodyMedium')

# Liste pour stocker les avis
reviews_list = []

for review in reviews:
    try:
        reviewer_name = review.find_element(By.CSS_SELECTOR, 'button > div.d4r55').text
        review_text = review.find_element(By.CSS_SELECTOR, 'span.wiI7pd').text
        review_rating = review.find_element(By.CSS_SELECTOR, 'span.kvMYJc').get_attribute('aria-label')
        review_date = review.find_element(By.CSS_SELECTOR, 'span.rsqaWe').text
        reviews_list.append([reviewer_name, review_rating, review_text, review_date])
    except Exception as e:
        print(f"Erreur lors de l'extraction d'un avis : {e}")

# Fermez le driver
driver.quit()

# Créez un DataFrame pandas
df = pd.DataFrame(reviews_list, columns=['Reviewer Name', 'Rating', 'Review', 'Date'])

# Enregistrez le DataFrame dans un fichier CSV
df.to_csv('reviews_peel.csv', index=False, encoding='utf-8')

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
