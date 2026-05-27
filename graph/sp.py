import heapq
from typing import Tuple, List

def reconstruct_path(parents: List[int], target_node: int) -> List[int]:
    path = []
    current = target_node
    while current != -1:
        path.append(current)
        current = parents[current]
        
    path.reverse() # Weil wir vom Ziel rückwärts zum Start gelaufen sind
    return path

def dijkstra(graph, start_node: int) -> Tuple[List[float], List[int]]:

    n = graph.num_nodes
    distances = [float('inf')] * n
    parents = [-1] * n
    
    distances[start_node] = 0.0
    
    # (Aktuelle_Distanz, Knoten_ID)
    pq = [(0.0, start_node)]
    
    while pq:
        current_dist, u = heapq.heappop(pq)
        
        # Lazy Deletion: Wenn es einen besseren Weg zu 'u' gibt, wird der alte Eintrag aus dem Heap geskippt
        if current_dist > distances[u]:
            continue
            
        for v, weight in graph.get_neighbors(u):
            if weight < 0:
                raise ValueError(f"Dijkstra gescheitert: Negative Kante ({u}->{v} mit {weight}) gefunden!")
                
            distance = current_dist + weight
            
            # Relaxation der Kante
            if distance < distances[v]:
                distances[v] = distance
                parents[v] = u
                heapq.heappush(pq, (distance, v))
                
    return distances, parents

def bellman_ford(graph, start_node: int) -> Tuple[List[float], List[int]]:

    n = getattr(graph, 'num_nodes', len(list(graph.get_nodes())))
    distances = [float('inf')] * n
    parents = [-1] * n
    
    distances[start_node] = 0.0
    nodes = list(graph.get_nodes())
    
    # Relaxiere alle Kanten (V - 1) mal
    for i in range(n - 1):
        changed = False
        for u in nodes:
            if distances[u] == float('inf'):
                continue
                
            for v, weight in graph.get_neighbors(u):
                if distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    parents[v] = u
                    changed = True
                    
        # Stop wenn sich in dem Durchlauf nichts geändert hat
        if not changed:
            break
            

    # for u in nodes:
    #     if distances[u] == float('inf'):
    #         continue
    #     for v, weight in graph.get_neighbors(u):
    #         if distances[u] + weight < distances[v]:
    #             raise ValueError("Graph enthält einen erreichbaren Zyklus mit negativem Gesamtgewicht!")
            
    # Wenn Kanten nochmal entspannt werden können, gibt es einen negativen Kreis.
    cycle_node = -1
    for u in nodes:
        if distances[u] == float('inf'):
            continue
        for v, weight in graph.get_neighbors(u):
            if distances[u] + weight < distances[v]:
                # Update parent ein letztes Mal, damit der Zyklus stimmt
                parents[v] = u
                cycle_node = v
                break
        if cycle_node != -1:
            break

    # cycle_node gefunden
    if cycle_node != -1:
        # N Schritte zurück gehen, um garantiert im Zyklus zu landen
        curr = cycle_node
        for _ in range(n):
            curr = parents[curr]
            
        # Zyklus speichern
        cycle = []
        cycle_start = curr
        while True:
            cycle.append(curr)
            curr = parents[curr]
            if curr == cycle_start:
                break
                
        # Array umdrehen und den Startknoten anhängen, um den Kreis zu schließen
        cycle.reverse()
        cycle.append(cycle[0])
        
        cycle_str = " -> ".join(map(str, cycle))
        raise ValueError(f"Negativer Zyklus: {cycle_str}")
                
    return distances, parents