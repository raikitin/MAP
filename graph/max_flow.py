from collections import deque
from typing import Tuple, List, Dict

def edmonds_karp(graph, source: int, sink: int) -> float:
    """
    Berechnet den maximalen Fluss von der Quelle (source) zur Senke (sink)
    mit dem Edmonds-Karp-Algorithmus.
    Laufzeit: O(V * E^2)
    """
    nodes = list(graph.get_nodes())
    
    # 1. Residualgraphen aufbauen (Kapazitäten)
    # capacity[u][v] speichert die aktuell noch verfügbare Restkapazität
    capacity = {u: {} for u in nodes}
    # adj speichert die Nachbarn für die BFS (inklusive künstlicher Rückwärtskanten)
    adj = {u: [] for u in nodes}
    
    for u in nodes:
        for v, cap in graph.get_neighbors(u):
            # Vorwärtskante initialisieren
            capacity[u][v] = cap
            adj[u].append(v)
            
            # Künstliche Rückwärtskante initialisieren (falls nicht im Originalgraphen)
            if u not in capacity[v]:
                capacity[v][u] = 0.0
                adj[v].append(u)

    max_flow = 0.0

    # 2. Schleife: Solange wir einen erweiternden Pfad finden, erhöhe den Fluss
    while True:
        # BFS, um den kürzesten erweiternden Pfad zu finden
        parent = {node: -1 for node in nodes}
        parent[source] = source
        
        queue = deque([source])
        path_found = False
        
        while queue and not path_found:
            current = queue.popleft()
            
            for neighbor in adj[current]:
                # Nachbarn noch nicht besucht haben und noch Platz
                if parent[neighbor] == -1 and capacity[current][neighbor] > 0:
                    parent[neighbor] = current
                    
                    if neighbor == sink:
                        path_found = True
                        break
                        
                    queue.append(neighbor)
                    
        # BFS erreicht die Senke nicht mehr, kein erweiternder Pfad mehr vorhanden
        if not path_found:
            break
            
        # Bottleneck auf dem gefundenen Pfad suchen
        path_flow = float('inf')
        current = sink
        while current != source:
            prev = parent[current]
            path_flow = min(path_flow, capacity[prev][current])
            current = prev
            
        # Residualgraphen aktualisieren 
        current = sink
        while current != source:
            prev = parent[current]
            # Vorwärtskante: Kapazität wird verbraucht 
            capacity[prev][current] -= path_flow
            # Rückwärtskante: Virtuelle Kapazität entsteht
            capacity[current][prev] += path_flow
            current = prev
            
        max_flow += path_flow

    return max_flow