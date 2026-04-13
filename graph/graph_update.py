from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import List, Tuple, Iterable
from collections import deque

# ==========================================
# 1. SCHNITTSTELLE (INTERFACE)
# ==========================================
class Graph(ABC):
    
    @abstractmethod
    def add_edge(self, u: int, v: int, weight: float = 1.0) -> None:
        pass

    @abstractmethod
    def get_neighbors(self, u: int) -> Iterable[Tuple[int, float]]:
        pass

    @abstractmethod
    def get_nodes(self) -> Iterable[int]:
        pass
        
    @property
    @abstractmethod
    def is_directed(self) -> bool:
        pass

# ==========================================
# 2. DATENHALTUNG: LISTE VON LISTEN
# ==========================================
class AdjacencyListGraph(Graph):
    def __init__(self, num_nodes: int, directed: bool = False):
        self.num_nodes = num_nodes
        self._directed = directed
        # Liste von Listen: Der Index der äußeren Liste entspricht der Knoten-ID
        self.adj_list: List[List[Tuple[int, float]]] = [[] for _ in range(num_nodes)]

    @property
    def is_directed(self) -> bool:
        return self._directed

    def add_edge(self, u: int, v: int, weight: float = 1.0) -> None:
        # Direkter Indexzugriff ist schneller als Dictionary-Hashing
        self.adj_list[u].append((v, weight))
        if not self._directed:
            self.adj_list[v].append((u, weight))

    def get_neighbors(self, u: int) -> Iterable[Tuple[int, float]]:
        return self.adj_list[u]

    def get_nodes(self) -> Iterable[int]:
        # Wir geben einfach einen Range zurück (sehr speichereffizient)
        return range(self.num_nodes)

# ==========================================
# 3. DATENHALTUNG: ADJAZENZMATRIX
# ==========================================
class AdjacencyMatrixGraph(Graph):
    def __init__(self, num_nodes: int, directed: bool = False):
        self.num_nodes = num_nodes
        self._directed = directed
        self.matrix = [[None for _ in range(num_nodes)] for _ in range(num_nodes)]

    @property
    def is_directed(self) -> bool:
        return self._directed

    def add_edge(self, u: int, v: int, weight: float = 1.0) -> None:
        self.matrix[u][v] = weight
        if not self._directed:
            self.matrix[v][u] = weight

    def get_neighbors(self, u: int) -> Iterable[Tuple[int, float]]:
        for v in range(self.num_nodes):
            weight = self.matrix[u][v]
            if weight is not None:
                yield (v, weight)

    def get_nodes(self) -> Iterable[int]:
        return range(self.num_nodes)

# ==========================================
# 4. SCHNELLER DATEI-PARSER
# ==========================================
def load_graph_fast(filepath: str, graph_class, directed: bool = False, weighted: bool = True) -> Graph:
    with open(filepath, 'r') as f:
        file_iter = iter(f)
        
        try:
            num_nodes = int(next(file_iter))
        except StopIteration:
            raise ValueError("Die Datei ist leer.")
            
        graph = graph_class(num_nodes, directed)
        add_edge = graph.add_edge
        
        if weighted:
            for line in file_iter:
                parts = line.split()
                if parts:
                    add_edge(int(parts[0]), int(parts[1]), float(parts[2]))
        else:
            for line in file_iter:
                parts = line.split()
                if parts:
                    add_edge(int(parts[0]), int(parts[1]), 1.0)
                    
    return graph

# ==========================================
# 5. ALGORITHMEN
# ==========================================
def bfs(graph: Graph, start_node: int) -> List[int]:
    visited = {start_node}
    queue = deque([start_node])
    traversal_order = []
    
    while queue:
        current = queue.popleft()
        traversal_order.append(current)
        
        for neighbor, _ in graph.get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
                
    return traversal_order

def count_connected_components(graph: Graph) -> int:
    visited_global = set()
    components = 0
    
    for node in graph.get_nodes():
        if node not in visited_global:
            components += 1
            component_nodes = bfs(graph, node)
            visited_global.update(component_nodes)
            
    return components