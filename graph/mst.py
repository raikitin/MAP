from graph import Graph
import heapq
from typing import List, Tuple

# Hilfsstruktur für Kruskal
# https://medium.com/@conniezhou678/mastering-dara-algorithm-part-28-understanding-union-find-in-python-155da9e04ccb
class UnionFind:

    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, i: int) -> int:
        if self.parent[i] == i:
            return i
        self.parent[i] = self.find(self.parent[i]) # Path Compression: Hängt alle Knoten auf dem Weg direkt an die Wurzel
        return self.parent[i]

    def union(self, i: int, j: int) -> bool:
        root_i = self.find(i)
        root_j = self.find(j)
        
        if root_i != root_j:
            # Union by Rank: Den flacheren Baum unter den tieferen hängen
            if self.rank[root_i] < self.rank[root_j]:
                self.parent[root_i] = root_j
            elif self.rank[root_i] > self.rank[root_j]:
                self.parent[root_j] = root_i
            else:
                self.parent[root_j] = root_i
                self.rank[root_i] += 1
            return True
        return False # Knoten waren bereits in derselben Menge (bilden einen Kreis)


def kruskal(graph: Graph) -> Tuple[float, List[Tuple[int, int, float]]]:

    edges = []
    nodes = list(graph.get_nodes())
    if not nodes:
        return 0.0, []
        
    for u in nodes:
        for v, weight in graph.get_neighbors(u):
            if u < v: 
                edges.append((weight, u, v))
                
    edges.sort(key=lambda x: x[0])
    
    # Union-Find initialisieren (Größe = maximaler Knoten-Index + 1)
    max_node_id = max(nodes) + 1
    uf = UnionFind(max_node_id)
    
    mst_edges = []
    total_weight = 0.0
    
    
    # Kanten durchgehen und zum MST hinzufügen, wenn sie keinen Kreis bilden
    for weight, u, v in edges:
        if uf.union(u, v):
            mst_edges.append((u, v, weight))
            total_weight += weight
            
            # maximal V - 1 Kanten
            if len(mst_edges) == len(nodes) - 1:
                break
                
    return total_weight, mst_edges


def prim(graph: Graph, start_node: int = 0) -> Tuple[float, List[Tuple[int, int, float]]]:

    nodes = list(graph.get_nodes())
    if not nodes:
        return 0.0, []
        
    visited = {start_node}
    mst_edges = []
    total_weight = 0.0
    
    # Priority Queue (Min-Heap) mit (Gewicht, Herkunftsknoten, Zielknoten)
    min_heap = []
    for v, weight in graph.get_neighbors(start_node):
        heapq.heappush(min_heap, (weight, start_node, v))
        
    while min_heap and len(mst_edges) < len(nodes) - 1:
        weight, u, v = heapq.heappop(min_heap)
        
        if v not in visited:
            visited.add(v)
            mst_edges.append((u, v, weight))
            total_weight += weight
            
            for next_v, next_weight in graph.get_neighbors(v):
                if next_v not in visited:
                    heapq.heappush(min_heap, (next_weight, v, next_v))
                    
    return total_weight, mst_edges

def prim_optimized(graph: Graph, start_node: int = 0) -> Tuple[float, List[Tuple[int, int, float]]]:
    # Methoden-Lookup Cache
    heappush = heapq.heappush
    heappop = heapq.heappop
    get_neighbors = graph.get_neighbors
    
    num_nodes = graph.num_nodes
    if num_nodes == 0:
        return 0.0, []

    visited = [False] * num_nodes
    visited[start_node] = True
    
    mst_edges = []
    total_weight = 0.0
    
    # Priority Queue (Min-Heap) mit (Gewicht, Startknoten, Zielknoten)
    min_heap = []
    
    for v, weight in get_neighbors(start_node):
        heappush(min_heap, (weight, start_node, v))
        
    edge_count = 0
    target_edges = num_nodes - 1
    
    while min_heap and edge_count < target_edges:
        weight, u, v = heappop(min_heap)
        
        if visited[v]:
            continue
            
        visited[v] = True
        mst_edges.append((u, v, weight))
        total_weight += weight
        edge_count += 1
        
        for next_v, next_weight in get_neighbors(v):
            if not visited[next_v]:
                heappush(min_heap, (next_weight, v, next_v))
                
    return total_weight, mst_edges