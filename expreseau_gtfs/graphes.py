

import pandas as pd
from pyproj import Proj, transform
from expreseau_gtfs.feed import gtfs_feed 
import networkx as nx
import numpy as np
import heapq
# from tqdm import tqdm
from shapely import Point, MultiPoint, Polygon
import geopandas as gpd
import requests
from sklearn.neighbors import KDTree
from shapely.ops import cascaded_union

class graphes:
    def __init__(self, Feed,
                 distance = 500,
                 vitesse_marche = 4.0,
                 facteur_distance = 1.5):
        
        self._Feed = Feed
        self._distance = distance
        self._vitesse_marche = vitesse_marche
        self._facteur_distance = facteur_distance

    @property
    def distance(self):
        """
        int
            La valeur par défaut est 500. C'est la distance à vol
            d'oiseau atteignable à pied (en mètres) pour la connexion des arrêts..

        """
        return self._distance
    @distance.setter
    def distance(self, value):
        self._distance = value
        
    @property
    def facteur_distance(self):
        """
        float
            Facteur correcteur de la distance à vol d'oiseau. La valeur par défaut est 1.5.

        """
        return self._facteur_distance
    @facteur_distance.setter
    def facteur_distance(self, value):
        self._facteur_distance = value
        
    @property
    def vitesse_marche(self):
        """
        float
            La valeur par défaut est 4.0. Vitesse de marche
            suposée entre deux arrêts, destination ou origine.

        """
        return self._vitesse_marche
    @vitesse_marche.setter
    def vitesse_marche(self, value):
        self._vitesse_marche = value
        

    def gtfs_to_nx(self, MALUS = 3, verbose = True):
        """
        Renvoit un graphe networkx simple directionnel routable et utilisable 
        avec la librairie networkx.

        Parameters
        ----------
        MALUS : int, optional
            La valeur par défaut est 3. Coefficient multiplicateur
           pour éviter les correspondances anarchiques entre deux lignes suivant
           les mêmes corridors.
        verbose : bool, optional
            La valeur par défaut est False. Affichage des
            commentaires lors de la création du graphe.

        Returns
        -------
        cg : networkx.DiGraph()
            Graohe du réseau, utilisable avec les méthodes de la librairie networkx.
        """

        distance = self._distance
        vitesse_marche = self._vitesse_marche
        facteur_distance = self._facteur_distance

        if verbose: print("création du graphe directionnel")
        cg = nx.DiGraph()
        
        # charge les arrets uniques :
        if verbose: print("chargement des arrêts uniques")
        stops = self._get_table_noeuds()
        # parcours et ajout des noeuds :
        if verbose: print("ajout des noeuds au graphes")
            
        for _, stop in stops.iterrows():
            cg.add_node(stop.stop_id,
                       stop_name = stop.stop_name,
                       x = stop.x,
                       y = stop.y,
                       route_short_name = stop.route_short_name,
                       headway = stop.headway) 
        
        # chargement des segments
        if verbose: print("chargement des segments")
        segments = self._get_table_segments()
        
        for _, edge in segments.iterrows():
            cg.add_edge(edge.start_stop_id, edge.end_stop_id,
                      route=edge.route_short_name,
                      cost=edge.temps)
        
        nx.set_edge_attributes(cg, 'transit', 'mode')
        if verbose: print("ajout des connexions piétonnes")        
        cg = self._connexions_pietonnes(cg,stops,distance,
                                  vitesse_marche,
                                  facteur_distance,
                                  MALUS)
        return cg
        
        
    def table_noeuds(self):
        """
        Table des noeuds qui servent à construire le graphe.

        Returns
        -------
        pandas.DataFrame()

        """
        return self._get_table_noeuds()
    
    def table_segments(self):
        """
        Table des arêtes qui servent à constuire le graphe.

        Returns
        -------
        pandas.DataFrame().

        """

        return self._get_table_segments()
    
    def dijkstra_min_transfers(self, graph, source, target, max_transfers):
        """
        Calcule le chemin le plus court (temps) en minimisant les correspondances.
        Adaptation de l'algorithme Dijkstra.

        Parameters
        ----------
        graph : networkx.DiGraph()
            Graphe du réseau de transport issue de la méthode gtfs_to_nx().
        source : str
            rret (stop_id) tel que définit dans le df graphes.table_noeuds().
        target : str
            Arret (stop_id) tel que définit dans le df graphes.table_noeuds().
        max_transfers : int
            Maximum de correspondances.

        Returns
        -------
        Coût : float
            Temps de transport du trajet. Issu des tables horaires.
        Nombre de correspondances : intYPE
            Correspondances du trajet proposé.
        path : python list()
            Liste des arrêts empruntés par le trajet le plus court.
        """
        return self._get_dijkstra_min_transfers(graph, source, target, max_transfers)
        
    
    def betweenness_centrality(self, graph):
        """
        Calcule la betweenness centrality en minimisant le temps de parcours les correspondances.       

        Parameters
        ----------
        graph : networkx.DiGraph()
            Graphe du réseau de transport issue de la méthode gtfs_to_nx().

        Returns
        -------
        dict
            Betweenness centrality pour chaque arrêt.

        """
        return self._get_betweenness_centrality(graph)
    
    def closeness_centrality(self, graph):
        """
        Calcule la closeness centrality en minimisant le temps de parcours les correspondances.

        Parameters
        ----------
        graph : networkx.DiGraph()
            Graphe du réseau de transport issue de la méthode gtfs_to_nx().

        Returns
        -------
        dict
            Closeness centrality pour chaque arrêt.

        """
        return self._get_closeness_centrality(graph)
    
    def isochrones(self, graph, source, temps_secondes = [300,900,1800],
                   labels = ['5min', '15min', '30min'], crs = "epsg:2154", speed = 4, geoservice=False, mode="pedestrian"):
        """
        Créé des isochrones de couplage marche à pied/voiture + transports en commun à 
        partir d'un arrêt choisi.       

        Parameters
        ----------
        graph : networkx.DiGraph()
            Graphe du réseau de transport issue de la méthode gtfs_to_nx().
        source : str
            rret (stop_id) tel que définit dans le df graphes.table_noeuds().
        temps_secondes : python list(), optional
            Liste des intervalles de temps souhaités en secondes. Les valeurs par défaut : [300,900,1800].
        labels : python list(), optional
            Liste des labels des intervalles de temps souhaités. Les valeurs par défaut : ['5min', '15min', '30min'].
        crs : str, optional
            Projection par défaut : "epsg:2154".
        speed : int, optional
            Vitesse de déplacement. Valeur par défaut : 4.
        geoservice : bool, optional
            La valeur True permet de faire appel à l'API Geoservices de l'IGN pour le calcul des temps de parcours. Par défaut, la valeur est False.
        mode : str, optional
            Utilisée dans le cas où geoservice=True. Il permet de choisir entre "car" et "pedestrian". La valeur par défaut est "pedestrian".

        Returns
        -------
        geopandas.GeoDataFrame()
            Multipolygones des isochrones.

        """
        return self._get_isochrones_2(graph, source, temps_secondes, labels, crs, speed, geoservice, mode)
 
    def _get_table_segments(self):

        # 0. Chargement et nettoyage de la table d'arrets uniques :
        table_arret = self._get_table_arrets().drop_duplicates()
# =============================================================================
#       I. Création des segments entre arrêts :
# =============================================================================
        # 1. creation colone "end_stop_id", l'arret spécifiant la fin du segment :
        table_arret['end_stop_id'] = table_arret.groupby(["trip_id"])[['stop_id']].shift(-1)
        # 2. tri par trips, stop_sequence
        table_arret = table_arret.sort_values(by = ['trip_id', 'stop_sequence'])
        # 3. on supprime les segments qui auraient le même noeud de départ et d'arrivée :
        table_arret = table_arret[table_arret['stop_id'] != table_arret['end_stop_id']]
        
# =============================================================================
#       II. Création de la table de segments :
# =============================================================================
        # 1. nettoyage et renommage :
        segments = table_arret.rename(columns={"stop_id":"start_stop_id"}).reset_index(drop=True)
        # 2. calcul du temps moyen de parcours :
        segments['temps'] = segments['arrival_time'].shift(-1) - segments['arrival_time']
        # on supprime les temps nuls :
        segments.dropna(subset = 'temps', inplace = True) 
        segments = segments[segments.temps >= 0].reset_index(drop=True) # on supprime les temps négatifs
        # je suppose que les temps nuls ne le sont pas vraiment : j'ajoute 30sec
        segments.temps = segments.temps.replace(0, 30)
        segments = segments[['start_stop_id','end_stop_id', "route_short_name","temps"]]\
        .groupby(['start_stop_id','end_stop_id', "route_short_name"]).mean().reset_index()

        return segments

    def _get_table_noeuds(self):
        """
        définition d'une table de noeuds à partir de la table d'arrets. Ajout 
        des temps moyens d'attente.'
        """
        
        table_noeuds = self._get_table_arrets()
# =============================================================================
#       I. Ajout des temps moyen d'attente à chaque arrêt :
# =============================================================================
        # 1. on supprime les doublons
        table_noeuds = table_noeuds.drop_duplicates().reset_index(drop=True)
        
        # 2. on ajoute les temps d'attente moyens à chaque arrêt  unique entre 2 trips :
        stp_wt = table_noeuds.copy()
        stp_wt = stp_wt.sort_values(['stop_id', 'arrival_time']).drop_duplicates()
        stp_wt['headway'] = (stp_wt.groupby('stop_id')['arrival_time'].shift(-1) - stp_wt.arrival_time) / 60
        stp_wt = stp_wt[["stop_id", "headway"]].groupby('stop_id').mean().reset_index()
        
        # 3. on merge avec la table stp_wt pour récupérer le temps d'attente moyen :
        table_noeuds = table_noeuds.merge(stp_wt, on = "stop_id")
        # table_noeuds = table_noeuds[table_noeuds.headway>0] # on filtre les temps négatifs
        # on supprime les headway nuls :
        table_noeuds = table_noeuds.fillna(np.inf)
        # table_noeuds = table_noeuds.dropna(subset = 'headway')#_unique
        # table_noeuds = table_noeuds[table_noeuds.route_short_name != "scolaire"]
        
        # 4. calcul des temps et des coorddonnées moyennes des arrêts :
        table_noeuds = table_noeuds[["stop_name","stop_id","route_short_name","x","y","headway"]]\
        .groupby(["stop_name","stop_id","route_short_name", "x", "y"]).mean().reset_index()

        
        return table_noeuds

    
    
    def _get_table_arrets(self):
        """
        creation d'une table d'arrêts uniques avec une récupération de leurs passages et tables horaires
        sur la période souhaitée
        """       
        
# =============================================================================
#      I. On cherche à avoir les trips_id qui circulent le jour demandé 
#               sur la plage horaire demandée
# =============================================================================
        # 1. extraction de la table horaire :
        table_cible = self._Feed.table_horaire()

        # 2. on réordonne la table par trips et par ordre croissant de stop_sequence
        table_cible = table_cible.sort_values(by=['trip_id', 'stop_sequence'])
        table_cible = table_cible.reset_index(drop=True)
        liste_trips = table_cible.trip_id.unique()
        
# =============================================================================
#       II. Pour éviter d'avoir des trips "coupés" à cause de la plage horaire,
#          on recharge une nouvelle table horaire sur une plage étendue que l'on
#          va filtrer par la liste des trips circulants sur la plage horaire demandée
# =============================================================================
        # 1. on recharge une nouvelle table avec un plg_hor étendue :
        # on charge un objet feed temporaire :
        plage_horaire = [self._Feed.plage_horaire[0] - 1, 
                        self._Feed.plage_horaire[1] + 1]
        feed_tmp = gtfs_feed(self._Feed.gtfs_path,
                             self._Feed.date,
                             plage_horaire=plage_horaire)
        
        table = feed_tmp.table_horaire()
        
        # 2. on filtre avec les trips_id définis plus haut
        table = table[table.trip_id.isin(liste_trips)]
        # 3. on réordonne la table par trips et par ordre croissant de stop_sequence
        table = table.sort_values(by=['trip_id', 'stop_sequence'])
        table = table.reset_index(drop=True)
        
# =============================================================================
#        III. Chargement des coordonnées des arrets
# =============================================================================
        # 1. Chargemet des arrêts et de leurs position
        stp = self._Feed.stops[['stop_id','stop_name', 'stop_lon', 'stop_lat']]
        # stp.stop_id = stp.stop_id.astype(str)
        stp.columns = ['stop_id',"stop_name", 'x', 'y']
        # 2. changer de projection wgs84 -> lambert93 
        # Définir les systèmes de coordonnées pour WGS84 et Lambert 93
        wgs84 = Proj(init='epsg:4326')  # WGS84
        lambert93 = Proj(init='epsg:2154')  # Lambert 93
            # Coordonnées en WGS84 (latitude, longitude)
        longitude, latitude = stp.x.values, stp.y.values
            # Convertir de WGS84 à Lambert 93
        x, y = transform(wgs84, lambert93, longitude, latitude)
        stp['x'] = x; stp['y'] = y
        # 3. fusion :
        # homogéneisation des types avant fusion
        table.stop_id = table.stop_id.astype(str)
        stp.stop_id = stp.stop_id.astype(str)
        table = table.merge(stp, on = "stop_id")
        
# =============================================================================
#       IV.Creation d'un id unique par arret pour chaque ligne le traversant
# =============================================================================
        # 1. on créé un identifiant 
        table['stop_id'] = table.stop_id.astype(str) + '_' + table.route_short_name.astype(str)
        # 2. nettoyage  des colonnes :
        table.drop(columns=['route_id',  'service_id'], inplace = True)
        # 3. on créé ensuite un dataframe dans lequel on trouve les segments 
        # ainsi que leurs taille (distance d'arrêt à arrêt en mètres)
        table_arret = table.sort_values(by=['trip_id', 'stop_sequence'])
        table_arret = table_arret.reset_index(drop=True)
        
        return table_arret
    
    def _connexions_pietonnes(self, cg, stops, distance, vitesse_marche,
                              facteur_distance, MALUS):
        """
        Returns
        -------
        cg_ : TYPE
            DESCRIPTION.
    
        """
        cg_ = cg.copy()
        stops_location = stops[['x', 'y']].to_numpy()
    
        # recherche des noeuds les plus proche dans un rayon de 300m, avec un modèle kdtree
        max_distance = distance
        btree = KDTree(stops_location)
        indices, distance = btree.query_radius(stops_location, r=max_distance, return_distance=True)
    
        # table des indices et des distances séparant les arrets :
        prox = pd.DataFrame(distance, indices,).reset_index().reset_index()
        prox.columns = ['indice', 'cibles', "distance"]
    
        walk_speed_kmph = float(vitesse_marche) # vitesse de marche
    
    
        for _, idx in prox.iterrows():
    
            ori = idx.indice
            dests = idx.cibles
            lengths = idx.distance
    
            for dest, length in zip(dests, lengths):
    
                walk_dis = length * facteur_distance
                walk_h = walk_dis / 1000 / walk_speed_kmph
                walk_sec = walk_h * 60 * 60
    
                # ids des arrêts source et cible :
                source = stops[stops.index == ori].stop_id.iloc[0]
                target = stops[stops.index == dest].stop_id.iloc[0]
    
                # on vérifie que les deux arrêts sont dans le graphe :
                if (source in cg.nodes) or (target in cg.nodes):
                    name_tar = cg.nodes[target]['stop_name']
                    name_src = cg.nodes[source]['stop_name']
    
    
                    # si les arrets sont différents:cg.nodes[target]['stop_name']
                    if source != target:
                        # si aucun chemin n'existe entre les deux arrêts :
                        if not cg.has_edge(source, target):
    
# =============================================================================
### CONFIG. 1 : les arrets n'ont pas le même nom, la corresp. est "naturelle"
# =============================================================================
    
        #                   temps de transfert = temps de marche + temps moyen d 'attente divisé par 2. Suppositions.
                            if name_tar != name_src:
                                transfer_time = (cg.nodes[target]['headway'] / 2  + walk_sec) 
                                # alors on insère l'edge dans le graphe avec le mode "walk"
                                cg_.add_edge(source, target, cost=transfer_time, dist=length, mode='walk', route ="") 
                            
    
# =============================================================================
### CONFIG. 2 : les arrêts ont le même nom
# =============================================================================
    
                            if name_tar == name_src:
                                # On force la création de l'edge dans le cas 
                                # où la source ou la cible n'ont pas de successeurs
                                # (fin de ligne)
                                if list(cg_.successors(target)) == []: st = ["1"]
                                else: st = cg_.nodes[list(cg_.successors(target))[0]]['stop_name']
                                    
                                if list(cg_.successors(source)) == []: ss = ["0"]
                                else: ss = cg_.nodes[list(cg_.successors(source))[0]]['stop_name']

                                # si les arrets successeurs ne sont pas les même:
                                if st != ss:
                                    transfer_time = (cg.nodes[target]['headway'] / 2  + walk_sec) * MALUS
                                    cg_.add_edge(source, target, cost=transfer_time, dist=length, mode='walk')

        return cg_
    
    def _get_isochrones(self, graph, source, temps_secondes, labels, crs, buffer):
        
        iso_l = []
        
        coords = self._get_table_noeuds()
        
        for m in temps_secondes:
            res = self._single_source_dijkstra_max_time(graph, source, m)
            keys = list(res.keys())
            values = list(res.values())
            points = [(time, k) for time, k in zip(values, keys) if (time != np.inf)&(time != 0)]
            points_l = []
            points_l = [Point([coords[coords.stop_id == point[1]].x, coords[coords.stop_id == point[1]].y]) for point in points]
            iso_l.append(MultiPoint(points_l).buffer(buffer))
            
        gdf = gpd.GeoDataFrame(data = pd.DataFrame(labels, columns=['isochrone']),
                                             geometry = gpd.GeoSeries(iso_l).set_crs(crs))
        
        return gdf
    
    def _get_isochrones_2(self, graph, source, temps_secondes, labels, crs, speed,
                          geoservice, mode):
        
        iso_l = []
        gdf = gpd.GeoDataFrame()
        # iso_times = []
        coords = self._get_table_noeuds()
        
        for m, l in zip(temps_secondes, labels):
            res = self._single_source_dijkstra_max_time(graph, source, m)
            keys = list(res.keys())
            values = list(res.values())
            points = [(time, k) for time, k in zip(values, keys) if (time != np.inf)&(time != 0)]
            points_l = []
            # times_l = [] # on recupère les temps
            
            
            if geoservice == True:
                for point in points:
                    time = m - point[0] # temps restant en secondes
                    
                    try:
                        points_l.append(self._get_geoservices_isochrones(point, time, mode))
                    except:
                        print("erreur")
                        print(point, time)
            else:
                for point in points:
                    
                    time = m - point[0] # temps restant en secondes
                    distance = time * (speed/3.6) #m/s
                    
                    points_l.append(Point([coords[coords.stop_id == point[1]].x,
                                           coords[coords.stop_id == point[1]].y]).buffer(distance))
            
            # tmp = gpd.GeoDataFrame(data = pd.DataFrame([l], columns=['isochrone']),
            #                                      geometry = gpd.GeoSeries(points_l).set_crs(crs)).dissolve()
            
            # gdf = pd.concat([tmp, gdf])
                    
            # print(points_l)
            iso_l.append(cascaded_union(points_l)) #
            # iso_times.append(times_l)
            
            gdf = gpd.GeoDataFrame(data = pd.DataFrame(labels, columns=['isochrone']),
                                                  geometry = gpd.GeoSeries(iso_l).set_crs(crs))
            
        return gdf 
    
    def _get_geoservices_isochrones(self, point, time, mode):
        coords = self._get_table_noeuds()
        X = coords[coords.stop_id == point[1]].x.values[0]
        Y = coords[coords.stop_id == point[1]].y.values[0]
        # URL GEOSERVICES
        url = f"https://data.geopf.fr/navigation/isochrone?point={X}%2C{Y}&resource=bdtopo-valhalla&costValue={time}&costType=time&profile={mode}&direction=departure&constraints=%7B%22constraintType%22%3A%22banned%22%2C%22key%22%3A%22wayType%22%2C%22operator%22%3A%22%3D%22%2C%22value%22%3A%22autoroute%22%7D&distanceUnit=meter&timeUnit=second&crs=EPSG%3A2154"
        
        resq = requests.get(url)
        
        if resq.status_code == 200:
            # je recupère les coordonnées des points de l'itinéraire:
            coordinates = resq.json()['geometry']["coordinates"]
            # je transforme en points
            points = [Point([u[0], u[1]]) for u in coordinates[0]]
        else:
            print(resq.reason, X, Y)


        # return points
        return Polygon(points)

    
    
    
    
    def _get_dijkstra_min_transfers(self, graph, source, target, max_transfers):
        dist = {}  # Dictionnaire pour stocker les distances les plus courtes
        prev = {}  # Dictionnaire pour stocker les nœuds précédents sur le chemin le plus court
        transfers = {}  # Dictionnaire pour stocker le nombre de correspondances
        pq = []    # File de priorité pour le traitement des nœuds
    
        # Initialisation des distances à l'infini pour tous les nœuds
        for node in graph.nodes():
            dist[node] = float('inf')
            transfers[node] = float('inf')
            prev[node] = None
    
        # Distance de la source à elle-même est 0
        dist[source] = 0
        transfers[source] = 0
    
        # Ajout de la source dans la file de priorité
        heapq.heappush(pq, (dist[source], source))
    
        # Algorithme de Dijkstra
        while pq:
            d, node = heapq.heappop(pq)
    
            if node == target:
                break
    
            for neighbor, weight in graph[node].items():
                alt = dist[node] + weight.get('cost', 1)  # Poids de l'arête (1 par défaut si non spécifié)
                transfer_count = transfers[node] + (graph.nodes[node]['route_short_name'] != graph.nodes[neighbor]['route_short_name'])
                if alt < dist[neighbor] or (alt == dist[neighbor] and transfer_count < transfers[neighbor]):
                    dist[neighbor] = alt
                    prev[neighbor] = node
                    transfers[neighbor] = transfer_count
                    # Ajout de la condition sur le nombre maximum de correspondances
                    if transfers[neighbor] <= max_transfers:
                        heapq.heappush(pq, (dist[neighbor], neighbor))
    
        # Reconstruction du chemin le plus court
        path = []
        current = target
        while current is not None:
            path.insert(0, current)
            current = prev[current]
    
        return dist[target], transfers[target], path
    
    
    def _single_source_dijkstra_min_transfers_all(self, graph, source, max_transfers):
# =============================================================================
#   calcul des chemins les plus courts d'un noeud vers l'ensemble du réseau
# =============================================================================
        dist = {}  # Dictionnaire pour stocker les distances les plus courtes
        prev = {}  # Dictionnaire pour stocker les nœuds précédents sur le chemin le plus court
        transfers = {}  # Dictionnaire pour stocker le nombre de correspondances
        pq = []    # File de priorité pour le traitement des nœuds
    
        # Initialisation des distances à l'infini pour tous les nœuds sauf la source
        for node in graph.nodes():
            if node == source:
                dist[node] = 0
                transfers[node] = 0
            else:
                dist[node] = float('inf')
                transfers[node] = float('inf')
            prev[node] = None
    
        # Ajout de la source dans la file de priorité
        heapq.heappush(pq, (dist[source], source))
    
        # Algorithme de Dijkstra
        while pq:
            d, node = heapq.heappop(pq)
    
            for neighbor, weight in graph[node].items():
                alt = dist[node] + weight.get('cost', 1)  # Poids de l'arête (1 par défaut si non spécifié)
                transfer_count = transfers[node] + (graph.nodes[node]['route_short_name'] !=\
                                                    graph.nodes[neighbor]['route_short_name'])
                
                if alt < dist[neighbor] or (alt == dist[neighbor] and transfer_count < transfers[neighbor]):
                    dist[neighbor] = alt
                    prev[neighbor] = node
                    transfers[neighbor] = transfer_count
                    # Ajout de la condition sur le nombre maximum de correspondances
                    if transfers[neighbor] <= max_transfers:
                        heapq.heappush(pq, (dist[neighbor], neighbor))
    
        # Reconstruction des chemins les plus courts
        shortest_paths = {}
        temps = {}
        for target in graph.nodes():
            if target != source:
                path = []
                current = target
                while current is not None:
                    path.insert(0, current)
                    current = prev[current]
                shortest_paths[target] = path
                temps[target] = dist[target]#, transfers[target] #(dist[target], transfers[target], path)
    
        return shortest_paths, temps
    
    def _get_betweenness_centrality(self, graph):
# =============================================================================
# Calcul de la betweenness centrality avec un algo dijsktra tenant compte des
# correspondances maximales voulues.
# =============================================================================
        # on instancie un dictionnaire nul :
        betweenness_centrality = {node: 0.0 for node in graph.nodes()}
        
        # on parcourt tous les noeuds du graphe en leur faisant prendre la valeur "source"
        # for source, t in zip(graph.nodes(), tqdm(graph.nodes)):
        for source in graph.nodes():
            # on calcule les chemins les plus courts vers l'ensemble du réseau depuis "source"
            shortest_paths = self._single_source_dijkstra_min_transfers_all(graph, source, 2)[0]
            # on parcourt tous les noeuds du réseau en leur faisant prendre la valeur "target"
            for target in graph.nodes():
                if target != source:
                    # on parcourt chaque noeud du chemin le plus court entre source et target
                    for node in shortest_paths[target]:
                        # si le noeud n'est ni le départ ni l'arrivée du chemin le plus court courant :
                        if node != source and node != target:
                            betweenness_centrality[node] += 1  # on compte le nombre de passage par le noeud courant
        # on calcule le nombre de paires de noeuds possible dans le graphe :
        total_pairs = (len(graph.nodes()) - 1) * (len(graph.nodes()) - 2)
        
        # on reparcourt le dictionnaire pour terminer le calcul de la betweenness centrality :
        for node in graph.nodes():
            betweenness_centrality[node] /= total_pairs
    
        return betweenness_centrality
    
    def _get_closeness_centrality(self, graph):
        closeness_centrality = {}
        # for node, t in zip(graph.nodes(), tqdm(graph.nodes())):
        for node in graph.nodes():
            spl = self._single_source_dijkstra_min_transfers_all(graph, node, 2)[1]
            spl = np.array(list(spl.values()))
            spl[spl == np.inf] = 5e4
            total_distance = sum(spl) #  if not math.isinf(x)
    #         total_distance = sum(shortest_paths_lengths.values())
            closeness_centrality[node] = 1 / total_distance if total_distance != 0 else 0
    
        return closeness_centrality
    
    
    def _single_source_dijkstra_max_time(self, graph, source, max_time=None):
        # Initialisation des ensembles S et D
        S = set()
        D = {node: float('inf') for node in graph.nodes()}
        D[source] = 0
    
        while len(S) < len(graph.nodes()):
            # Sélection du nœud non visité avec la plus petite distance dans D
            v = min((node for node in graph.nodes() if node not in S), key=lambda node: D[node])
            S.add(v)
            
            # Mise à jour des distances pour les nœuds adjacents à v
            for neighbor in graph.neighbors(v):
                if neighbor not in S:
                    edge_weight = graph[v][neighbor]['cost']
                    distance_to_neighbor = D[v] + edge_weight
                    if max_time is None or distance_to_neighbor <= max_time:
                        if distance_to_neighbor < D[neighbor]:
                            D[neighbor] = distance_to_neighbor
    
        return D

    