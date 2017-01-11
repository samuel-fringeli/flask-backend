# Système de réservation CSUD

## Installation

### Démarrage du projet

Pour démarrer le projet, il faut commencer par créer un environnement virtuel Python. Sous Cloud9, il faut faire

```{bash}
sudo pip3 install virtualenv
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

### ERAlchemy

Pour pouvoir générer les diagrammes entité-associations du modèle SQLAlchemy, il est nécessaire d'installer GraphViz de la manière suivante :

```{bash}
$ sudo apt-get install graphviz
$ sudo apt-get install libgraphviz-dev
$ pip install eralchemy
```

