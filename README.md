# expreseau_gtfs
**EXP**loration des **RESEAU**x de transports en commun avec **GTFS**\
Outils pour la manipulation et l'exploration des données gtfs pour l'analyse de la performance des réseaux de transports en commun.
### Classe gtfs_feed()
Le fichier analyses.py contient la classe gtfs_feed. L'objet gtfs_feed(fichiers *.zip gtfs) contient une séries de fonctions pour analyser la performances de lignes selon plusieurs indicateurs d'offres.
### Classe sections()
Le fichier sections contient la classe sections. L'objet sections() permet de découper les lignes de manière automatisée en fonction de leur variations d'offres.
La fonction sections.decoupe_auto() permet également de détecter les séparations et jonctions de lignes.


# Quickstart

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
```python
gf.frequence_par_ligne(date_demandee="20240305", plage_horaire=[7,8])
```
Arguments obligatoires :
   -  date_demandee : *string* au format 'yyyymmdd'
   -  plage_horaire : liste de *int* spécifiant un intervalle fermé des heures définissant la plage.
Ce qui donne :

route_short_name|  direction_id|  nbtrips|  mean_headway
---		  |     ---        |    ---    |---
10     |      0.0        |    6        |  10.000000
12     |      0.0        |    4       |  15.000000
13     |      0.0        |    4       |  15.000000
20     |      0.0        |    7       |   8.571429

**Remarques :** *nbtrips* et *mean_headway* sont respectivement le nombre de voyages moyens sur la période et la fréquence moyenne.

### Obtenir la table horaire du jour demandé

```python
gf.table_horaire_jour_demande(date_demandee="20240305", plage_horaire=[7,8])
```
Renvoit la table horaire (passages aux arrêts) des services circulant le jour et l'heure spécifiés.
Arguments obligatoires :
   -  date_demandee : *string* au format 'yyyymmdd'
   -  plage_horaire : liste de *int* spécifiant un intervalle fermé des heures définissant la plage.

### Obtenir l'amplitude par ligne
Renvoit un dataframe avec l'amplitude (1er départ - dernière arrivée) horaire par ligne : 
```python
gf.amplitude_par_ligne(date_demandee="20240305")
```
Arguments obligatoires :
   -  date_demandee : *string* au format 'yyyymmdd'


### Obtenir les services exceptés

### Obtenir la fréquence par segments 

### Obtenir le tracés des lignes

```python
gf.traces_des_lignes(date_demandee='20240305', plage_horaire=[7,9])
```
Renvoit un geodataframe avec pour chaque trip_id une géométrie associée. **La géométrie n'a pas de CRS.**
Arguments obligatoires :
   -  date_demandee : *string* au format 'yyyymmdd'
   -  plage_horaire : liste de *int* spécifiant un intervalle fermé des heures définissant la plage.

Résultats :
trip_id            |                               geometry
:---:			      |                   :---:
4503749951498677 | LINESTRING (3.05248 45.79740, 3.05255 45.79760...
4503749951498678 | LINESTRING (3.04176 45.76570, 3.04203 45.76560...
4503749951498679 | LINESTRING (3.05650 45.76730, 3.05677 45.76730...
etc ... | ...

#### Tracer les lignes avec *matplotlib* et *geopandas* :
```python
# on enregistre le gdf dans une variable et on précise le crs avec .set_crs() (ici WGS84)
geo_lignes = gf.traces_des_lignes(date_demandee='20240305', plage_horaire=[7,9]).set_crs("epsg:4326")
# on charge les trips et routes pour récupérer le nom des lignes :
trips = gf.trips
routes = gf.routes
# on fusionne les fichiers pour obtenir une table des correspondances entre trip_id et route_short_name :
trips_routes = trips[['trip_id', 'route_id']].merge(routes[["route_id", "route_short_name", "route_color"]], on = 'route_id')
# on fusionne avec le gdf des lignes :
geo_lignes = geo_lignes.merge(trips_routes[["trip_id", "route_short_name", "route_color"]], on = "trip_id")
geo_lignes.plot()
```
![Sans titre](https://github.com/lufages/expreseau_gtfs/assets/113050391/1aeb9cba-8793-477e-8e47-e40273134348)


### Obtenir la fréquence par *shape*

```python
gf.frequence_par_shapes(date_demandee='20240305', plage_horaire=[7,9], stop_sequence = 1)
```
Renvoit un geodataframe avec pour chaque trip_id une géométrie associée. **La géométrie n'a pas de CRS.**
Arguments obligatoires :
   -  date_demandee : *string* au format 'yyyymmdd'
   -  plage_horaire : liste de *int* spécifiant un intervalle fermé des heures définissant la plage.
Arguments facultatifs :
   - stop_sequence : *int*. Par défaut on calcule la fréquence à partir de la fréquence de passage à l'arrêt numéroté 1. Attention cette méthode n'est pas idéale dans le cas où la fréquence varie selon le tronçon de ligne concerné. Le cas échéant, il sera nécessaire d'utiliser les méthodes de la classe sections().
```python
# on charge la fréquence par shape : 
fsh = gf.frequence_par_shapes(date_demandee='20240305', plage_horaire=[7,9])
# on fusionne avec le gdf des shapes créé en amont :
geo_lignes.merge(fsh, on = "shape_id").sort_values(by='mean_headway', ascending=False).\
plot(column = "mean_headway", cmap = "viridis", legend = True, scheme = "natural_breaks")
```
On trace la fréquence moyenne par shape :\
![Sans titre](https://github.com/lufages/expreseau_gtfs/assets/113050391/48f3a6d2-6371-400c-8a95-1fdf4a354826)


### Tracer l'évolution journalière de l'offre, heure par heure

