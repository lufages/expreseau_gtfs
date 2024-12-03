# Quickstart
## Table des matières
[Pour un usage basique](#usabasique)
  1. [Charger un fichier gtfs au format *.zip](#chargergtfs)\
      a. [Tracer l'évolution journalière de l'offre](#plotevol)\
      b. [Obtenir les services exceptés](#servex)\
      c. [Obtenir la table horaire du jour demandé](#tabhor)
  2. [Calculer des indicateurs de performances du réseau]\
      a. [Obtenir la fréquence par ligne du jour demandé](#frligne)\
      b. [Obtenir l'amplitude par ligne au jour demandé](#ampligne)\
      c. [Obtenir la fréquence par segments](#frseg)\
      d. [Obtenir le tracés des lignes](#trclignes)\
      e. [Obtenir la fréquence par *shape*](#frshp)

     
[Pour un usage avancé](#usaavance)
  1.  [Découpage automatique d'une ligne en tronçons](#decoupauto)\
      a.  [Créer un objet *sections()*](#objsections)

[Exemples]

## Pour un usage basique <a id="usabasique"></a>
### Créer un objet *gtfs_feed()* et charger des fichiers gtfs au format *.zip <a id="chargergtfs"></a>
Dans l'objet *gtfs_feed()* il est nécessaire de renseigner une date ("yyyymmdd") et une plage horaire ([7,9] par exemple)
```python
from expreseau_gtfs.feed import gtfs_feed
fic = r"~\gtfs_data.zip"
date = "20240305"
plage_horaire = [7,9]
Feed = gtfs_feed(fic, date = date, plage_horaire = plage_horaire)
```
Ainsi, on peut avoir accès, d'une part à tous les fichiers *.txt contenus dans le répertoire zippé, par exemple les *routes* :

```python
Feed.routes
```
  index |          route_id |        agency_id |route_short_name   | route_long_name  |      route_desc | route_type | route_url |route_color |           route_text_color
---   |---					|   ---           |       ---         |   ---            |      ---        |   ---      |    ---    |   ---      |   ---
0  | 11821953316814882 | 6192453782601729 |               3   |         Ligne 3 	|	Ligne Ligne 3   |        3   |     NaN   |   ed6e00   |			FFFFFF
1  | 11821953316814883 | 6192453782601729 |              31   |        Ligne 31		|	Ligne Ligne 31  |         3  |      NaN  |    9c8cc9		|	FFFFFF  

**Les fichiers sont triés par les services circulants le jour et l'heure spécifiés.** Il est possible de charger des dataframes des fichiers bruts avec la méthode *gtfs_feed.data()* : 
```python
Feed.data("trips") # renvoit le fichier brut des trips du répertoire GTFS zippé sous forme de dataframe
``` 

#### Obtenir la table horaire du jour demandé et de l'heure demandée<a id="tabhor"></a>

```python
Feed.table_horaire()
```
Renvoit la table horaire (passages aux arrêts) des services circulant le jour et l'heure spécifiés.

#### Obtenir les services exceptés <a id="servex"></a>

```python
gf.services_exceptes()
```
Renvoit la liste des services exceptés issus du fichier *calendar_dates*.\

#### Tracer l'évolution journalière de l'offre, heure par heure <a id="plotevol"></a>

```python
Feed.plot_evol_journaliere()
```
Renvoit un graphique matplotlib avec l'évolution de l'offre d'une part sur l'ensemble du réseau et d'autre part, si spécifié, l'évolution de l'offre sur certaines lignes.\

Arguments facultatifs :
   - liste_lignes_a_tracer : *list()*. Liste des lignes que l'on souhaite observer.
   - y_axe_2 : *string*. Nom du second axe y (à droite).
   - y_axe_1 : *string*. Nom du premier axe y (à gauche). C'est l'évolution de l'ensemble des lignes, mais l'argument n'a pas de valeur pas défaut.
   - titre : *string*. Titre du graphique.
   - x_axe : *string* . Nom de l'axe des x.\
Résultats:\
![Sans titre](https://github.com/lufages/expreseau_gtfs/assets/113050391/6adf0159-db0b-4d9b-b289-35f0101806f6)


et d'autre part un ensemble de méthodes qui permettent de calculer des indicateurs de performances du réseau.

### Calculer des indicateurs de performances du réseau avec l'objet *performances()*

Les opérations qui suivent sont basées sur l'objet *gtfs_feed* définit en amont ainsi les indicateurs seront calculés pour l'heure et le jour spécifiés dans *gtfs_feed*.

On commence par créer un objet performances :
```python
from expreseau_gtfs.performances import performances

gperf = performances(Feed)
```

#### Obtenir la fréquence par ligne du jour demandé <a id="frligne"></a>
```python
gperf.frequence_par_ligne() # rappels : date_demandee="20240305" et plage_horaire=[7,9]
```
Ce qui donne :

route_short_name|  direction_id|  nbtrips|  mean_headway
---		  |     ---        |    ---    |---
10     |      0.0        |    6        |  10.000000
12     |      0.0        |    4       |  15.000000
13     |      0.0        |    4       |  15.000000
20     |      0.0        |    7       |   8.571429

**Remarques :** *nbtrips* et *mean_headway* sont respectivement le nombre de voyages moyens sur la période et la fréquence moyenne.

### Obtenir la fréquence par segments <a id="frseg"></a>
```python
gperf.frequence_par_segment(coords=False)
```
Renvoit un geodataframe des segments (arrêt à arrêt) avec leur fréquence moyenne et nombre de passages sur la plage horaire spécifiée.\

Arguments facultatifs :
   - coords : *bool*. Par défaut *False*. Utile uniquement lorsqu'on souhaite utiliser les fonctions de découpage automatique des lignes de la classe sections()

Résultats :
segment |	route_short_name |	direction_id 	| nbtrips 	|geometry
:---:	|        :---:     |       :---:   |      :---:    | :---:
3377704015495197 - 3377704015496264 	|7 	|1 |	1 	| LINESTRING (3.08435 45.79290, 3.08545 45.79590)
3377704015495198 - 3377704015495857 	|7 	|0 |	2 	| LINESTRING (3.08430 45.79300, 3.08425 45.78970)
3377704015495200 - 3377704015495637 	|20 	|1 |	7 	| LINESTRING (3.16119 45.79180, 3.14478 45.79260)
etc ... | ... |...|...|...


#### Obtenir l'amplitude par ligne au jour demandé <a id="ampligne"></a>
Renvoit un dataframe avec l'amplitude (1er départ - dernière arrivée) horaire par ligne : 
```python
gperf.amplitude_par_ligne()
```

### Obtenir le tracés des lignes <a id="trclignes"></a>

```python
gperf.traces_des_lignes()
```
Renvoit un geodataframe avec pour chaque trip_id une géométrie associée. **La géométrie n'a pas de CRS.**

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
geo_lignes = gperf.traces_des_lignes().set_crs("epsg:4326")
# on charge les trips et routes pour récupérer le nom des lignes :
trips = Feed.trips
routes = Feed.routes
# on fusionne les fichiers pour obtenir une table des correspondances entre trip_id et route_short_name :
trips_routes = trips[['trip_id', 'route_id']].merge(routes[["route_id", "route_short_name", "route_color"]], on = 'route_id')
# on fusionne avec le gdf des lignes :
geo_lignes = geo_lignes.merge(trips_routes[["trip_id", "route_short_name", "route_color"]], on = "trip_id")
geo_lignes.plot()
```
![Sans titre](https://github.com/lufages/expreseau_gtfs/assets/113050391/1aeb9cba-8793-477e-8e47-e40273134348)


### Obtenir la fréquence par *shape* <a id="frshp"></a>

```python
gperf.frequence_par_shapes(stop_sequence = 1)
```
Renvoit un geodataframe avec pour chaque trip_id une géométrie associée. **La géométrie n'a pas de CRS.**\
Arguments obligatoires :
   -  date_demandee : *string* au format 'yyyymmdd'
   -  plage_horaire : liste de *int* spécifiant un intervalle fermé des heures définissant la plage.\
Arguments facultatifs :
   - stop_sequence : *int*. Par défaut on calcule la fréquence à partir de la fréquence de passage à l'arrêt numéroté 1. Attention cette méthode n'est pas idéale dans le cas où la fréquence varie selon le tronçon de ligne concerné. Le cas échéant, il sera nécessaire d'utiliser les méthodes de la classe sections().
```python
# on charge la fréquence par shape : 
fsh = gperf.frequence_par_shapes()
# on fusionne avec le gdf des shapes créé en amont :
geo_lignes_fsh = geo_lignes.merge(fsh, on = "shape_id")
```
On trace la fréquence moyenne par shape :
```python
geo_lignes_fsh.sort_values(by='mean_headway', ascending=False).\
plot(column = "mean_headway", cmap = "viridis", legend = True, scheme = "natural_breaks")
```
![Sans titre](https://github.com/lufages/expreseau_gtfs/assets/113050391/48f3a6d2-6371-400c-8a95-1fdf4a354826)





## Pour un usage avancé <a id="usaavance"></a>

### Découpage de ligne par tronçons <a id="decoupauto"></a>

Le calcul d'indicateurs de fréquences ou de services peut s'avérer aberrant lorsque sur une ligne de transports on trouve des différences d'offre de service selon l'arrêt, l'heure ou les deux. 
C'est souvent le cas sur certaines lignes de tramways, où, passé un certain arrêt, l'offre diminue. On trouve ces configurations lorsque le tramway arrive en périphérie.

#### Créer un objet sections() <a id="objsections"></a>

L'objet *sections()* a besoin d'une table des fréquences par segments en attribut (voir *performances().frequences_par_segments()*).

```python
from expreseau_gtfs.sections import sections
gf = sections
```
```python
frsegln = frseg[(frseg.route_short_name == "13") & (frseg.direction_id == 0)]

gs = sections(df=frsegln)

sst = gf.stops
sst.stop_id = sst.stop_id.astype(str)
gda = gs.decoupe_auto(stops=sst, temps = 120, coef = 1.6)
gda

```
nb_trips 	|geometry 	|stop_name_dep 	|stop_id_dep 	|stop_name_arr 	|stop_id_arr |	part d'offre| 	frequence horaire moyenne (min)
---| ---|---|---|---|---|---|---| 
5.9 	|MULTILINESTRING ((3.05318 45.78220, 3.05052 45... 	|Hauts de Chamalières 	|3377704015495701 	|Margeride 	|3377704015495862 	|100.00 	|20.34
1.0 	|MULTILINESTRING ((3.12024 45.76110, 3.12578 45... |	Margeride 	|3377704015495862 	|La Pardieu Gare 	|3377850044383332| 	16.95 	|120.00
2.8 	|MULTILINESTRING ((3.12024 45.76110, 3.12812 45... 	|Margeride 	|3377704015495862 	|PERIGNAT Les Horts |	3377704015495786 	|47.46 	|42.86


```python
gda.plot(column = "frequence horaire moyenne (min)", linewidth=5, legend=True, scheme = "natural_breaks")
```

![Sans titre](https://github.com/lufages/expreseau_gtfs/assets/113050391/5c46d865-d99c-44d2-8de0-c155e5c9c29f)
