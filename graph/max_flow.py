from collections import deque
from typing import Tuple, List, Dict

def edmonds_karp(graph, source: int, sink: int) -> float:
    nodes = list(graph.get_nodes())
    
    # Residualgraphen aufbauen
    capacity = {u: {} for u in nodes}
    # adj speichert die Nachbarn für die BFS
    adj = {u: [] for u in nodes}
    
    for u in nodes:
        for v, cap in graph.get_neighbors(u):
            # Vorwärtskante
            capacity[u][v] = cap
            adj[u].append(v)
            
            # Künstliche Rückwärtskante
            if u not in capacity[v]:
                capacity[v][u] = 0.0
                adj[v].append(u)

    max_flow = 0.0

    while True:
        # BFS
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
                    
        # BFS erreicht die Senke nicht mehr
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
            capacity[prev][current] -= path_flow
            capacity[current][prev] += path_flow
            current = prev
            
        max_flow += path_flow

    return max_flow