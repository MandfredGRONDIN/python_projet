# Projet WiFi Dashboard

Ce projet est une application Web Flask qui permet de visualiser des données sur les bornes WiFi et les clients connectés à ces bornes.

### Installation

    Cloner le dépôt : git clone https://github.com/MandfredGRONDIN/python_projet.git

### Installer les dépendances :

    bash pip install -r requirements.txt

### Utilisation

    Exécuter le serveur : python app.py

### Initialisation de la bdd :

Vérifier que le fichier "log_wifi_red_hot.csv" soit bien dans le dossier files

    http://localhost:5005/init_db

Cette opération peut nécessiter un certain temps pour s'exécuter complètement

### Accéder au tableau de bord WiFi dans le navigateur :

    http://localhost:5005

### Fonctionnalités

    Affichage du nombre total de bornes WiFi.
    Affichage du nombre total de clients connectés.
    Affichage du volume total de données échangées.
