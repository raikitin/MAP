import itertools
from graph import *
from mst import kruskal, prim, prim_optimized

def nearest_neighbor(graph: Graph, start_node: int = 0) -> Tuple[float, List[int]]:

    nodes = list(graph.get_nodes())
    if not nodes:
        return 0.0, []
        
    num_nodes = len(nodes)
    visited = {start_node}
    tour = [start_node]
    total_distance = 0.0
    
    current_node = start_node
    
    while len(visited) < num_nodes:
        nearest_node = None
        min_distance = float('inf')
        
        for neighbor, weight in graph.get_neighbors(current_node):
            if neighbor not in visited and weight < min_distance:
                min_distance = weight
                nearest_node = neighbor
                
        if nearest_node is None:
            raise ValueError("Der Graph ist nicht vollständig! TSP kann nicht beendet werden.")
            
        visited.add(nearest_node)
        tour.append(nearest_node)
        total_distance += min_distance
        current_node = nearest_node
        
    for neighbor, weight in graph.get_neighbors(current_node):
        if neighbor == start_node:
            total_distance += weight
            tour.append(start_node)
            break
            
    return total_distance, tour


def double_tree(graph: Graph, start_node: int = 0) -> Tuple[float, List[int]]:

    # MST berechnen
    _, mst_edges = prim_optimized(graph, start_node)
    
    # MST-Kanten zu Adjazenzliste
    mst_adj = {node: [] for node in graph.get_nodes()}
    for u, v, weight in mst_edges:
        mst_adj[u].append(v)
        mst_adj[v].append(u)
        
    # DFS auf MST
    visited = set()
    tour = []
    
    def dfs(node):
        visited.add(node)
        tour.append(node)
        for neighbor in mst_adj[node]:
            if neighbor not in visited:
                dfs(neighbor)
                
    dfs(start_node)
    
    tour.append(start_node)
    
    total_distance = 0.0
    for i in range(len(tour) - 1):
        u = tour[i]
        v = tour[i+1]

        edge_weight = float('inf')
        for neighbor, weight in graph.get_neighbors(u):
            if neighbor == v:
                edge_weight = weight
                break
        total_distance += edge_weight
        
    return total_distance, tour


def _build_dist_matrix(graph: Graph) -> Tuple[List[List[float]], int]:

    nodes = list(graph.get_nodes())
    n = len(nodes)
    matrix = [[float('inf')] * n for _ in range(n)]
    
    for u in nodes:
        for v, weight in graph.get_neighbors(u):
            matrix[u][v] = weight
            
    return matrix, n


def tsp_brute_force(graph: Graph, start_node: int = 0) -> Tuple[float, List[int]]:

    matrix, n = _build_dist_matrix(graph)
    
    other_nodes = [i for i in range(n) if i != start_node]
    
    best_distance = float('inf')
    best_tour = []
    
    # itertools.permutations für alle möglichen Reihenfolgen
    for perm in itertools.permutations(other_nodes):
        current_distance = 0.0
        valid_path = True
        prev_node = start_node
        
        for current_node in perm:
            weight = matrix[prev_node][current_node]
            if weight == float('inf'):
                valid_path = False
                break
            current_distance += weight
            prev_node = current_node
            
        if valid_path:
            return_weight = matrix[prev_node][start_node]
            if return_weight != float('inf'):
                total_distance = current_distance + return_weight
                
                if total_distance < best_distance:
                    best_distance = total_distance
                    best_tour = [start_node] + list(perm) + [start_node]
                    
    return best_distance, best_tour


def tsp_branch_and_bound(graph: Graph, start_node: int = 0) -> Tuple[float, List[int]]:
    """
    Branch & Bound Algorithmus 
    Schneidet schlechte Pfade frühzeitig ab (Pruning)
    """
    matrix, n = _build_dist_matrix(graph)
    
    best_distance = float('inf')
    best_tour = []
    
    nn_visited = [False] * n
    nn_visited[start_node] = True
    curr = start_node
    nn_dist = 0.0
    
    for _ in range(n - 1):
        next_n = -1
        min_w = float('inf')
        for v in range(n):
            if not nn_visited[v] and matrix[curr][v] < min_w:
                min_w = matrix[curr][v]
                next_n = v
        if next_n != -1:
            nn_visited[next_n] = True
            nn_dist += min_w
            curr = next_n
            
    # Rückweg zum Start
    if matrix[curr][start_node] != float('inf'):
        best_distance = nn_dist + matrix[curr][start_node]
   

    # DFS Zustand
    visited = [False] * n
    visited[start_node] = True
    current_path = [start_node]
    
    def dfs(current_node: int, current_distance: float, depth: int):
        nonlocal best_distance, best_tour
        
        # pruning
        if current_distance >= best_distance:
            return
            
        # basisfall
        if depth == n:
            return_weight = matrix[current_node][start_node]
            if return_weight != float('inf'):
                total_distance = current_distance + return_weight
                if total_distance < best_distance:
                    best_distance = total_distance
                    best_tour = current_path[:] + [start_node]
            return
            
        # recursion
        for next_node in range(n):
            if not visited[next_node]:
                weight = matrix[current_node][next_node]
                if weight != float('inf'):
                    visited[next_node] = True
                    current_path.append(next_node)
                    
                    dfs(next_node, current_distance + weight, depth + 1)
                    
                    # Backtracking 
                    current_path.pop()
                    visited[next_node] = False

    dfs(start_node, 0.0, 1)
    
    return best_distance, best_tour

def tsp_branch_and_bound_optimized(graph: AdjacencyMatrixGraph, start_node: int = 0) -> Tuple[float, list[int]]:
    matrix = graph.matrix
    n = graph.num_nodes
    
    best_distance = float('inf')
    best_tour = []
    
    # INITIALE SCHRANKE (Upper Bound via Nearest-Neighbour)
    nn_visited = [False] * n
    nn_visited[start_node] = True
    curr = start_node
    nn_dist = 0.0
    
    for _ in range(n - 1):
        next_n = -1
        min_w = float('inf')
        for v in range(n):
            if not nn_visited[v] and matrix[curr][v] < min_w and curr != v:
                min_w = matrix[curr][v]
                next_n = v
        if next_n != -1:
            nn_visited[next_n] = True
            nn_dist += min_w
            curr = next_n
            
    if matrix[curr][start_node] != float('inf'):
        best_distance = nn_dist + matrix[curr][start_node]
    
    
    # VORBEREITUNG LOOK-AHEAD (Minimale ausgehende Kanten)
    min_edges = [float('inf')] * n
    for i in range(n):
        for j in range(n):
            if i != j and matrix[i][j] < min_edges[i]:
                min_edges[i] = matrix[i][j]
                
    # Die initiale optimistische Reststrecke ist die Summe der minimalen 
    # Kanten aller unbesuchten Knoten (am Anfang alle außer Start)
    initial_remaining_bound = sum(min_edges) - min_edges[start_node]

    # REKURSIVE SUCHE MIT PRUNING
    visited = [False] * n
    visited[start_node] = True
    current_path = [start_node]
    
    def dfs(current_node: int, current_distance: float, depth: int, remaining_bound: float):
        nonlocal best_distance, best_tour
        
        # Wenn die aktuellen Kosten plus das bestmögliche Restszenario schlechter
        # sind als unser Rekord, macht es keinen Sinn, hier weiterzusuchen.
        if current_distance + remaining_bound >= best_distance:
            return
            
        # Basis-Fall: Alle Knoten besucht
        if depth == n:
            return_weight = matrix[current_node][start_node]
            if return_weight != float('inf'):
                total_distance = current_distance + return_weight
                if total_distance < best_distance:
                    best_distance = total_distance
                    best_tour = current_path[:] + [start_node]
            return
            
        # Rekursion
        for next_node in range(n):
            if not visited[next_node]:
                weight = matrix[current_node][next_node]
                if weight != float('inf'):
                    visited[next_node] = True
                    current_path.append(next_node)
                    
                    # Wir ziehen die Minimal-Kante des nächsten Knotens aus dem Bound ab,
                    # da wir diesen Knoten jetzt verbuchen.
                    new_bound = remaining_bound - min_edges[next_node]
                    
                    dfs(next_node, current_distance + weight, depth + 1, new_bound)
                    
                    # Backtracking
                    current_path.pop()
                    visited[next_node] = False

    dfs(start_node, 0.0, 1, initial_remaining_bound)
    
    return best_distance, best_tour