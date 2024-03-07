# Découpage de ligne par tronçons

Le calcul d'indicateurs de fréquences ou de services peut s'avérer aberrant lorsque sur une ligne de transports on trouve des différences d'offre de service selon l'arrêt, l'heure ou les deux. 
C'est souvent le cas sur certaines lignes de tramways, où, passé un certain arrêt, l'offre diminue. On trouve ces configurations lorsque le tramway arrive en périphérie.

### Créer un objet sections()

L'objet *sections()* a besoin d'une table des fréquences par segments en attribut (voir *gtfs_feed().frequences_par_segments()*).\

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
