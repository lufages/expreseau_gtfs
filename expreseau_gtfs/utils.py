import pandas as pd
from datetime import datetime
import datetime as dtm
from geopandas import GeoDataFrame, GeoSeries
from shapely import Point

def nxbetweenness_to_df(nbc, col):
    
    """
    nxbetweenness_to_df(nbc, col)
        
    Fonctionne avec les méthodes betweenness_centrality, closenness_centrality
    et degree_centrality de networkx.
    Récupère le dictionnaire (résultat des méthodes) et le transforme en dataframe.
    --------
    Args :
        - nbc : dict. Renvoi des méthodes networkx.
        - col: str. Nom de la colone à donner au dataframe.
    --------
    Returns :
        - pandas dataframe()    
    """
    
    df = pd.DataFrame()
    
    df['stop_id'] = [n for n in nbc]
    df[col] = [nbc[n] for n in nbc]
    
    return df

def nbc_to_gdf(nbc, table_noeuds, col, crs = "epsg:2154"):
    
    """
    nbc_to_gdf(nbc, table_noeuds, col)
    
    Met en relation un indicateur de centralité (voir nxbetweenness_to_df()) et
    les coordonnées des arrêts dans un geopandas geodataframe.
    --------
    Args :
        - nbc : pandas dataframe issus de nxbetweenness_to_df()
        - table_noeuds: voir méthode graphe.table_noeuds()
        - col: str. Nom de la colone à donner au geodataframe.
    --------
    Returns :
        - geopandas geodataframe()
    """
    # homogénéisation des variables à fusionner :
    table_noeuds.stop_id = table_noeuds.stop_id.astype(str)
    nbc.stop_id = nbc.stop_id.astype(str)
    # fusion :
    nbc_ = nbc.merge(table_noeuds, on = "stop_id")
    res = nbc_[['stop_name', 'x', 'y']].groupby(['stop_name']).mean().reset_index()
    nbc_vals = nbc_[['stop_name', col]].groupby('stop_name').sum().reset_index()
    
    
    
    res = res.merge(nbc_vals, on = "stop_name")
    
    geom = GeoDataFrame(data = res,
           geometry = GeoSeries([Point([tmp.x, tmp.y]) for _, tmp in res.iterrows()]).set_crs(crs))

    return geom


def trouver_intervalle(date_demandee, df):
    
    """
    
    trouver_intervalle(date_demandee, df)
    
    Trouve l'intervalle contenant une date donnée dans des fichiers GTFS.
    --------
    Args :
        - date_demandee : str, "yyyymmdd"
        - dataframe du fichier "calendar"
    --------
    Returns :
        - pandas dataframe du fichier calendar des services circulant à la date
        demandée et les intervalles de circulation (start_date, end_date)
    
    """
    
    date_demandee = datetime.strptime(date_demandee, "%Y%m%d")
    masque = df.apply(lambda row: row['start_date'] <= date_demandee <= row['end_date'], axis=1)
    intervalle = df[masque]
    return intervalle

def seconds_to_hms(seconds):
    """
    Convertit une liste de temps en secondes en format "hh:mm:ss"    

    Parameters
    ----------
    seconds : python list()
        Liste d'entier de plsuieurs temps en secondes au format : [300, 500, etc].

    Returns
    -------
    temps_formatte : pyhton list()
        Liste de strings de temps au format "hh:mm:ss".

    """

    temps_formatte = list() # on instacie une liste vide dans laquelle on stockera les chaine des caractères
    for sec in seconds: # boucle sur toutes les entités de la liste de nombre réels
        delta = dtm.timedelta(seconds=sec) # on calcule le delta entre 00:00 et le 
                                                # nombre de secondes de l'entité courante
        # on converti en heures, minutes, secondes : 
        heures, remainder = divmod(delta.seconds, 3600)
        minutes, secondes = divmod(remainder, 60)
        # on convertit en string et on amende la liste
        temps_formatte.append('{:02}:{:02}:{:02}'.format(heures, minutes, secondes))
    # on renvoit la liste de strings
    return temps_formatte
    
    



