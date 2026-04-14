from MAP.graph.graph import *
from os import times
from time import time

paths = ['MAP\example\graph\Graph1.txt', 
         'MAP\example\graph\Graph2.txt', 
         'MAP\example\graph\Graph3.txt', 
         'MAP\example\graph\Graph_gross.txt', 
         'MAP\example\graph\Graph_ganzgross.txt', 
         'MAP\example\graph\Graph_ganzganzgross.txt'
         ]


# time_start = times().user
# g_liste = load_graph_fast(r"MAP\example\graph\Graph_ganzganzgross.txt", AdjacencyListGraph, directed=False, weighted=False)
# time_end = times().user
# print(f"Zeit für Einlesen: {time_end - time_start:.4f} Sekunden")

# time_start = times().user
# komponenten = count_connected_components(g_liste)
# print(f"Anzahl Komponenten (Liste): {komponenten}")
# time_end = times().user
# print(f"Zeit für Adjazenzliste: {time_end - time_start:.4f} Sekunden")