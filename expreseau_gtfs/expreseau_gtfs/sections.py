# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 16:19:53 2024

@author: Lucas Fages
"""

import networkx as nx
import pandas as pd
import numpy as np
# import expreseau_gtfs
from shapely import Point, LineString, MultiLineString
import geopandas as gpd
import logging


# logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

logger = logging.getLogger()

# print(logger)


class sections:
    
    def __init__(self,
                  df : pd.DataFrame() = None,
                  list_section: list() = None,
                  noeud_separation: list() = None,
                  arrivees: list() = None,
                  graph: nx.DiGraph() = None,
                  departs: list() = None#,
                  # verbose: str = "info"
                  ):
        self._df = df
        self._graph = graph
        self._list_section = list_section
        self._arrivees = arrivees
        self._departs = departs
        self._noeud_separation = noeud_separation
        
        # self._verbose = verbose
        
        # if self._verbose == "info":
        #     logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
        # if self._verbose == "debug":
        #     logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')

        # logger = logging.getLogger() il faut que ça soit écrit comme une fonction

        
        
    @property
    def graph(self):
        self._graph = self._get_graph()
        return self._graph
    
    @property
    def list_section(self, departs_ = None, arrivees_ = None):
        if (departs_ != None) & (arrivees_ != None):
            self._list_section = self._get_list_section(departs_, 
                                                        arrivees_)
        else:
            self._list_section = self._get_list_section(self.departs, 
                                                        self.arrivees)
        return self._list_section
    
    @list_section.setter 
    def append_list_section(self, value):
        self._list_section.append(value)
    
    @property
    def departs(self):
        self._departs = self._get_departs(G = self._get_graph())
        return self._departs
    
    @departs.setter
    def departs(self, value):
        self._departs = value
    
    @property
    def arrivees(self):
        self._arrivees = self._get_arrivees(G = self._get_graph())
        return self._arrivees
    
    @arrivees.setter
    def arrivees(self, value):
        self._arrivees = value
    
    @property
    def noeud_separation(self):
        self._noeud_separation = self._get_noeud_separation(G = self._get_graph()) 
        return self._noeud_separation
    
    @noeud_separation.setter
    def noeud_separation(self, value):
        self._noeud_separation = value
        
    def decoupe_auto(self, stops=pd.DataFrame(), temps = 60, coef = 1.3):
        """
        algo de découpage automatique d'une ligne en plusieurs tronçons :
            -selon les jonctions/séparations
            -selon la variation brutale de l'offre de service (permet 
            de distinguer les renforcements de candence sur certains tronçons
            d'une ligne en heure de pointe)

        Returns GeoDataFrame
        -------

        """
        return self._get_list_section_vfreq(stops, temps, coef)
    
    def _get_graph(self):
        df = self._df
        # test si df.segment existe:
        try: df.segment
        # si la colone n'existe pas, on renvoit l'erreur KeyError et on retourne une liste vide
        except KeyError as k: print(k.args); return []
        
        # 0 . on créé les relations :
        relations = df.segment.to_list()
        # distances = np.array(df.distance)
        G = nx.DiGraph() # on créé un graphe simple directionnel
        # Ajout des arêtes au graphe en fonction des relations
        for relation in relations:# parcours les entités de relations
            nodes = relation.split(' - ') # on lit chaque noeud du segment
            G.add_edge(nodes[0], nodes[1]) # on créé un edge et on le stocke dans G
        return G
    

    def _get_noeud_separation(self, G):
        noeud_separation = self._noeud_separation
        # G = self._graph/
        if noeud_separation == None: # si aucun noeud de separation n'est specifie
            noeud_separation = list() # instancie une liste vide
            for noeud in G.nodes(): # parcours tous les noeuds
                if len(list(G.predecessors(noeud))) > 1:
                    # Si un nœud a plus d'un prédécesseur, il est le point de séparation
                    noeud_separation.append(noeud)
                if len(list(G.successors(noeud))) > 1:
                    # Si un nœud a plus d'un successeur, il est le point de séparation
                    noeud_separation.append(noeud)
        return noeud_separation
    
    def _get_departs(self, G):
        departs = self._departs
        if G == None: G = self._get_graph()
        if departs == None:
            departs = [node for node, in_degree in G.in_degree() if in_degree == 0]
        return departs

    def _get_arrivees(self, G):
        arrivees = self._arrivees
        if G == None: G = self._get_graph()
        if arrivees ==  None:
            arrivees = [node for node, out_degree in G.out_degree() if out_degree == 0]
        return arrivees
        
    def _get_list_section(self, departs, arrivees):
        
        list_troncons = self._list_section
        if list_troncons == None:
            G = self._get_graph()
            if self._noeud_separation == None:
                noeud_separation = self._get_noeud_separation(G)
            else:
                noeud_separation = self._noeud_separation
            # logger.debug("noeuds de déparation : {}".format(noeud_separation))
            if len(noeud_separation) == 0: return []
            #3. on fait le tri selon la configuration :
            list_troncons = list() # on instancie une liste vide
            # cas d'un tronçon central avec une seule ramification avant l'arrivée (2 arrivées) :
            if (len(noeud_separation) == 1) & (len(arrivees)==2):
                logger.debug("tronçon central - 2 arrivées")
                try:
                    sep = noeud_separation[0] # séparation de la ligne 
                    [list_troncons.append(self._line_partition(G, sep, a)) for a in arrivees]
                except nx.NetworkXNoPath as e:print(e.args)
            # cas d'un tronçon central avec une seule ramification apres le depart (2 departs) :
            elif (len(noeud_separation) == 1)&(len(departs)==2):
                logger.debug("tronçon central - 2 départs")
                try:
                    sep = noeud_separation[0] # séparation de la ligne 
                    [list_troncons.append(self._line_partition(G, d, sep)) for d in departs]
                except nx.NetworkXNoPath as e:print(e.args)        
            # cas d'un tronçon central avec deux ramifications aux extrémités (2 arrivees 2 departs) :
            elif (len(noeud_separation)>1)&(len(departs)==2)&(len(arrivees)==2):
                logger.debug("tronçon central - 2 départs - 2 arrivées - attention au sens !!!")
                try:
                    sep = noeud_separation[0] # première séparation
                    [list_troncons.append(self._line_partition(G, d, sep)) for d in departs]
                    sep = noeud_separation[1] # seconde séparation
                    [list_troncons.append(self._line_partition(G,sep, a)) for a in arrivees]
                except nx.NetworkXNoPath as e: print(e.args)
            elif len(noeud_separation)==0:
                logger.debug('tronçon central - pas de séparation')
            # cas autres on fait un croisement sur toutes les entités
            # on boucle sur tous les noeuds de séparation, arrivées, départs
            # on couvre le cas le plus large
            else:
                logger.debug("autre configuration")
                # on récupère la liste des tronçons définis entre deux points de séparation/jonction
                # on récupère les arguments suivants : noeuds de séparation, noeuds d'arrivées, noeuds de départ
                # on les affiche
                logger.debug("departs : {}\narrivees : {}\nseparations : {}"\
                      .format(departs,arrivees,noeud_separation))
                # instancie listes
                dep_a_tester = list()
                # liste_troncons = list()
                # # on calcule le chemin entre le 1er et le 2nd noeud de séparation : 
                logger.debug("calcul du chemin entre le 1er et le 2nd noeud de séparation")
                if len(noeud_separation) > 1:
                    if nx.has_path(G, source = noeud_separation[0], target = noeud_separation[1]) == False: # test chemin
                        logger.debug("pas de chemin, on permutte la liste ... ")
                        # on permutte dans ce cas :
                        noeud_separation = [noeud_separation[1], noeud_separation[0]]
                        logger.debug('nouvel ordonancement de liste : {}'.format(noeud_separation))
                        # si false est renvoyé, c'est que les noeuds de séparation ne sont pas dans le bon ordre:
                        logger.debug("test pour : {} - {} : {}".format(noeud_separation[1],noeud_separation[0],
                              nx.has_path(G, source = noeud_separation[0],
                                         target = noeud_separation[1])))
                # on calcule ensuite les trajets entre les noeuds de déart et le premier noeud de séparation
                # si ces trajets n'existent pas, cela signifie que les autres départs vont rejoindre la ligne 
                # aux prochains noeuds de séparation
                logger.debug("calcul des trajets des noeuds de départ jusqu'au noeuds de séparation ...")    
                for nd in departs:
                    for ns in noeud_separation[:1]:
                        is_before = nx.has_path(G, source = nd, target=ns)
                        if is_before == True:
                            logger.debug('trajet trouvé ... :')
                            logger.debug("{} - {} : {}".format(nd, ns, is_before)) # on a récupéré les départs jusqu'au premier noeud de séparation
                            list_troncons.append(self._line_partition(G, nd, ns))
                        else: # on stocke les noeuds départs qui n'ont pas de chemin vers le 1er ns :
                            logger.debug("{} - {} : pas de trajet trouvé, on stocke les noeuds de départ \
                restants pour les tester avec le prochain de noeud de séparation".format(nd, ns))
                            dep_a_tester.append(nd)
                
                if len(noeud_separation) > 1:
                    logger.debug("plus d'un noeud de séparation ... ")
                    logger.debug("parcours des noeuds de séparation suivants ... :")
                    for ns in noeud_separation[1:]:
                    #     est-ce que le noeud a un ou des successeurs 
                        logger.debug("test de succession du noeud ... {}".format(ns))
                        if len(list(G.successors(ns))) == 1:
                            logger.debug("un seul successeur")
                            # noeud success devient noeuds source
                            for a in arrivees:
                                test = nx.has_path(G, source = ns, target=a)
                                logger.debug("test pour : {} - {} : {}".format(ns, a, test))
                                if test == True:
                                    logger.debug("calcul chemin {} - {}".format(ns, a))
                                    list_troncons.append(self._line_partition(G, ns, a))
                        else: # s'il y a plus d'un successeur 
                            logger.debug("plus d'un successeur ... {}".format(list(G.successors(ns))))
                            for a in arrivees:
                                test = nx.has_path(G, source = ns, target=a)
                                logger.debug("test pour : {} - {} : {}".format(a, ns, test))
                                if (test == True): # & (src!=a):
                                    list_troncons.append(self._line_partition(G, ns, a))
                    if dep_a_tester != []:
                        logger.debug("noeuds de départs restants : {}".format(dep_a_tester))
                        for nd in dep_a_tester:
                            for ns in noeud_separation[1:]:
                                test = nx.has_path(G, source = nd, target=a)
                                logger.debug("test pour : {} - {} : {}".format(nd, ns, test))
                                if (test == True):
                                    logger.debug("calcul chemin {} - {}".format(nd, ns))
                                    list_troncons.append(self._line_partition(G, nd, ns))
        return list_troncons


    def _get_trc_par_frequence(self, seg, coef = 1.3):
        """
        définit une série de tronçons selon la variation de la fréquence
        returns : liste de tronçons (segments), liste du nombre de trajets moyen
        """

        # instancier des listes à compléter :
        list_seg = list()
        list_trc = list()
        list_nb_trips = list()
        list_nbt_mean = list()
        
        list_seg.append(seg.segment.iloc[0])
        list_nb_trips.append(seg[seg.segment == seg.segment.iloc[0]].nbtrips.values[0])
        
        for n, m in zip(seg.segment[:-1],
                        seg.segment[1:]):
            t1 = seg[seg.segment == n].nbtrips.values[0]
            t2 = seg[seg.segment == m].nbtrips.values[0]
    
            if (t2 >= coef*t1) | (t1 >= coef*t2):
                list_trc.append(list_seg)
                list_nbt_mean.append(round(np.mean(list_nb_trips),1))
                # réinitialise les listes
                list_seg = []
                list_nb_trips = []
    
            list_nb_trips.append(t2)
            list_seg.append(m)
    
        list_trc.append(list_seg)
        list_nbt_mean.append(round(np.mean(list_nb_trips),1))
    
        return list_trc, list_nbt_mean

    def _get_list_section_vfreq(self, stops, temps, coef):
        
        segments = self._df
        departs = self._get_departs(G=self._graph)
        arrivees = self._get_arrivees(G=self._graph)
        # 
        try:
            ltri = []
            for x in list(nx.topological_sort(nx.line_graph(self._get_graph()))):
                ltri.append("{} - {}".format(x[0], x[1]))
                
            segments['segment'] = pd.Categorical(values = segments['segment'], categories=ltri, ordered=True)
            segments = segments.sort_values(by = 'segment')
            self._df = segments
        except nx.NetworkXUnfeasible as e:
            print(e.args)
        
        sections_ = self._get_list_section(departs, arrivees)
        resultat = [element for sous_liste in sections_ for element in sous_liste]
        
        # on créé une liste vide pour contenir des dataframes des chaque section :
        seg = list()
        # on commence par celle non répertoriée par l'algo separation/jonction
        seg.append(segments[~segments.segment.isin(resultat)])
        # on complète avec la liste des sections :
        for idx in range(len(sections_)):
            seg.append(segments[segments.segment.isin(sections_[idx])])
        # on instancie 2 nouvelles listes
        list_trc = list() 
        list_nbt_mean = list()
        # on réucpère la direction pour pouvoir récupérer les noms d'arrêts plus tard :
        direction = segments.iloc[0].direction_id
        # on parcours tous les tronçons pour les redécouper selon leurs variation de fréquence
        for s in seg:
            if s.is_empty.all() == False:
                tmp = self._get_trc_par_frequence(s, coef)
                list_trc.append(tmp[0])
                list_nbt_mean.append(np.array(tmp[1]))# / (temps / 60))
        # on convertit les listes de listes en listes simples : 
        list_nbt_mean = [element for sous_liste in list_nbt_mean for element in sous_liste]
        list_trc = [element for sous_liste in list_trc for element in sous_liste]
        
        listtrc = list()
        # segments_coords_stops = self._get_segment_coords()
        for trc in list_trc:
            listls = list()
            for segment in trc:
                try: # si jamais les coordonnées n'ont pas été demandées dans les fréquences par segment :
                    lat1 = segments[segments.segment == segment].stop_lat_dep
                    lon1 = segments[segments.segment == segment].stop_lon_dep
                    lat2 = segments[segments.segment == segment].stop_lat_arr
                    lon2 = segments[segments.segment == segment].stop_lon_arr
                    listls.append(LineString([Point([lon1, lat1]), 
                               Point([lon2, lat2])]))
                except AttributeError as e:
                    print(e.args)
                    print("Pensez à choisir la valeur True pour l'attribut coords de la méthode gtfs_feed().frequence par_segment")
                    return gpd.GeoDataFrame([]) # exit
                
            listtrc.append(MultiLineString(listls))
        
        gdf =  gpd.GeoDataFrame(list_nbt_mean, columns=['nb_trips'],
                geometry = gpd.GeoSeries(listtrc).set_crs("epsg:4326"))

        if stops.empty == False:        
                premiers = []; derniers = []
                
                logger.debug("liste de tronçons : {}".format(list_trc))
                logger.debug("direction choisie : {}".format(direction))
                if direction == 0:
                    [premiers.append(t[0].split(' - ')[0]) for t in list_trc]
                    [derniers.append(t[-1].split(' - ')[1]) for t in list_trc]
                if direction == 1:
                    [derniers.append(t[0].split(' - ')[0]) for t in list_trc]
                    [premiers.append(t[-1].split(' - ')[1]) for t in list_trc] 
                
                logger.debug("premiers arrêts : {}".format(premiers))
                logger.debug("derniers arrêts : {}".format(derniers))
                
                
                tmp = pd.DataFrame((premiers, derniers)).T
                tmp.columns =  ['dep', "arr"]
                tmp = tmp.merge(stops[['stop_id', 'stop_name']],
                         left_on = 'dep', right_on='stop_id')
                tmp = tmp.merge(stops[['stop_id', 'stop_name']],
                         left_on = 'arr', right_on='stop_id',
                               suffixes=('_dep', '_arr'))
                tmp = tmp[['stop_name_dep', 'stop_id_dep', 'stop_name_arr', 'stop_id_arr']]
                gdf = gdf.merge(tmp, right_index = True, left_index = True)      

        gdf["part d'offre"] = gdf.nb_trips.apply(lambda x: round(x / max(gdf.nb_trips.values) * 100,2))
        
        gdf['frequence horaire moyenne (min)'] = gdf.nb_trips.apply(lambda x: round(temps / x,2))

        return gdf 
        


    def _line_partition(self, G, noeud_depart, noeud_arrivee):
        """
        subdivise un graphe en sous graphe à partir de deux noeuds
        calcul du plus court chemin entre les 2 noeuds selon le plus court chemin
        return : liste de edges faisant le plus court chemin
        """
        # on créé un sous-graphe qui calcule le plus court chemin entre les deux noeuds :
        sous_graphe = nx.subgraph(G, nx.shortest_path(G, source=noeud_depart, target=noeud_arrivee))
        # on instancie une liste :
        list_sg = list()
        for k in list(sous_graphe.edges):
            list_sg.append("{} - {}".format(k[0], k[1]))
        return list_sg # on retourne la liste de segments