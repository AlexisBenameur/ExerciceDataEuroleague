# Analyse offensive et défensive des équipes d'Euroleague

Projet réalisé par Alexis Benameur

## Table des matières

1. Définitions
2. Objectifs
3. Source des données et bibliothèques python
4. Présentation du dépôt
5. Comment lancer les programmes

---

### 1. Définitions

**Le comeback :**
Gagner un match alors qu'on perdait de 10 points ou plus à la fin du troisième quart temps.

**3 point field goal attempt rate :**
Pourcentage des tirs à 3 points parmi l'ensemble des tirs pris par une équipe durant un match.

---

### 2. Objectifs

Ce projet est divisé en 2 parties : une se concentrant sur les comebacks et donc sur les stratégies offensives, l'autre seulement sur la défense par zone de chaque équipe.

Pour la première partie l'objectif était de regarder la probabilité de gagner un match selon la différence de points à chaque quart temps. Ensuite je me concentrais sur un aspect offensif, permettant de faire un comeback, qui était le tir à 3 points. Je voulais donc récupérer le poucentage à 3 points et le 3 point attempt rate pour chaque quart temps.

Pour la seconde partie je voulais m'intéresser aux endroits où une équipe défendait le mieux. Pour représenter cela j'ai pensé à une heatmap avec des couleurs selon la défense dans cette zone. Il fallait donc d'abord récupérer les pourcentages de chaque équipe dans chaque zone sur une saison. Puis pour une équipe, déterminer quel pourcentage de réussite avaient les autres équipes contre elle dans cette zone. 

---

### 3. Source des données et bibliothèques python

Pour les données je n'ai utilisé qu'une source :

* **L'API de l'Euroleague :** Résultats des matchs, statistiques play by play, statistiques des joueurs et des équipes etc...

Pour les bibliothèques python, j'ai utilisé : 

* **Plotly :** Faire des graphiques.
* **Pandas :** Faire des data frames compatibles avec plotly.
* **Requests :** Récupérer les données contenues dans l'API.
* **Streamlit :** Faire les dashboards en créeant des serveurs locaux.

---

### 4. Présentation du dépôt

Le projet est structuré en deux dossier :

1. **Dossier 1 : ExerciceDataEuroleague** Notebook analyse_euroleague.ipynb (avec toutes les fonctions et une explication) et fichier app.py (avec toutes les fonctions à la suite et les commandes streamlit pour visualiser les dasboards).
2. **Dossier 2 : heatmap** Notebook heatmap_defensive.ipynb (avec toutes les fonctions et une explication), fichier app_heatmap.py (avec toutes les fonctions à la suite et les commandes streamlit pour visualiser les dasboards) et fichier terrain_euroleague.png (photo d'un demi terrain pour la heatmap)


---

### 5. Comment lancer les programmes

Pour lancer le premier code il faut ouvrir app.py puis rajouter les identifiants dans credentials (au début du code) et exécuter streamlit run app.py dans le terminal. Si jamais un message d'erreur s'affiche il faut mettre pip install streamlit requests pandas plotly dans le terminal avant si ces modules n'ont pas encore été installés. 

Pour lancer le deuxième code il faut récupérer l'image nommée terrain_euroleague.png sur le git puis taper dans le terminal streamlit run app_heatmap.py. Si jamais un message d'erreur s'affiche il faut mettre pip install streamlit requests pandas plotly dans le terminal avant si ces modules n'ont pas encore été installés.
