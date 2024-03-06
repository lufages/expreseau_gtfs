# expreseau_gtfs
**EXP**loration des **RESEAU**x de transports en commun avec **GTFS**\
Outils pour la manipulation et l'exploration des données gtfs pour l'analyse de la performance des réseaux de transports en commun.
### Classe gtfs_feed()
Le fichier analyses.py contient la classe gtfs_feed. L'objet gtfs_feed(fichiers *.zip gtfs) contient une séries de fonctions pour analyser la performances de lignes selon plusieurs indicateurs d'offres.
### Classe sections()
Le fichier sections contient la classe sections. L'objet sections() permet de découper les lignes de manière automatisée en fonction de leur variations d'offres.
La fonction sections.decoupe_auto() permet également de détecter les séparations et jonctions de lignes.


# Documentation

### Charger un fichier gtfs au format *.zip
On créé un objet gtfs_feed() à partir du fichier gtfs zippé :

```python
from expreseau_gtfs.analyses import gtfs_feed
fic = r"~\gtfs_data.zip"
gf = gtfs_feed(fic)
```
Ainsi, on peut avoir accès, d'une part à tous les fichiers *.txt contenus dans le répertoire zippé, par exemple les *routes* :

  index |          route_id |        agency_id |route_short_name   | route_long_name  |      route_desc | route_type | route_url |route_color |           route_text_color
---   |---					|   ---           |       ---         |   ---            |      ---        |   ---      |    ---    |   ---      |   ---
0  | 11821953316814882 | 6192453782601729 |               3   |         Ligne 3 	|	Ligne Ligne 3   |        3   |     NaN   |   ed6e00   |			FFFFFF
1  | 11821953316814883 | 6192453782601729 |              31   |        Ligne 31		|	Ligne Ligne 31  |         3  |      NaN  |    9c8cc9		|	FFFFFF  

et d'autre part un ensemble de méthodes qui permettent de calculer des indicateurs de performances du réseau.

### Obtenir la fréquence par ligne du jour demandé

### Obtenir la table horaire du jour demandé

### Obtenir l'amplitude par ligne

### Obtenir les services exceptés

### Obtenir la fréquence par segments 

### Obtenir le tracés des lignes

### Obtenir la fréquence par *shape*

### Tracer l'évolution journalière de l'offre, heure par heure

