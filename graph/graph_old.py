from abc import ABC, abstractmethod
from typing import List, Tuple, Set
from collections import deque
from collections.abc import Iterator

# Interface
class Graph(ABC):
    """Abstrakte Basisklasse für alle Graphen-Implementierungen."""
    
    @abstractmethod
    def add_edge(self, u: int, v: int, weight: float = 1.0) -> None:
        """Fügt eine Kante zwischen u und v hinzu."""
        pass

    @abstractmethod
    def get_neighbors(self, u: int) -> List[Tuple[int, float]]:
        """Gibt eine Liste von (Nachbar, Gewicht)-Tupeln für Knoten u zurück."""
        pass

    @abstractmethod
    def get_nodes(self) -> List[int]:
        """Gibt alle Knoten-IDs des Graphen zurück."""
        pass
        
    @property
    @abstractmethod
    def is_directed(self) -> bool:
        """Gibt an, ob der Graph gerichtet ist."""
        pass

# Adjanzenzlisten-Implementierung
class AdjacencyListGraph(Graph):
    def __init__(self, num_nodes: int, directed: bool = False):
        self.num_nodes = num_nodes
        self._directed = directed
        # Dictionary: { Knoten -> [(Nachbar, Gewicht), ...] }
        self.adj_list = {i: [] for i in range(num_nodes)}

    @property
    def is_directed(self) -> bool:
        return self._directed

    def add_edge(self, u: int, v: int, weight: float = 1.0) -> None:
        self.adj_list[u].append((v, weight))
        if not self._directed:
            self.adj_list[v].append((u, weight))

    def get_neighbors(self, u: int) -> List[Tuple[int, float]]:
        return self.adj_list[u]

    def get_nodes(self) -> List[int]:
        return list(self.adj_list.keys())
    
# Adjanzenzmatrix-Implementierung
class AdjacencyMatrixGraph(Graph):
    def __init__(self, num_nodes: int, directed: bool = False):
        self.num_nodes = num_nodes
        self._directed = directed
        # 2D-Liste (Matrix), None bedeutet keine Kante
        self.matrix = [[None for _ in range(num_nodes)] for _ in range(num_nodes)]

    @property
    def is_directed(self) -> bool:
        return self._directed

    def add_edge(self, u: int, v: int, weight: float = 1.0) -> None:
        self.matrix[u][v] = weight
        if not self._directed:
            self.matrix[v][u] = weight

    def get_neighbors(self, u: int) -> List[Tuple[int, float]]:
        neighbors = []
        for v in range(self.num_nodes):
            weight = self.matrix[u][v]
            if weight is not None:
                neighbors.append((v, weight))
        return neighbors

    def get_nodes(self) -> List[int]:
        return list(range(self.num_nodes))
    
def load_graph(filepath: str, graph_class, directed: bool = False) -> Graph:
    """Liest eine txt-Datei und erstellt eine Graphen-Instanz."""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    num_nodes = int(lines[0].strip())
    
    graph = graph_class(num_nodes, directed)
    
    for line in lines[1:]:
        parts = line.strip().split()
        if not parts:
            continue
            
        u = int(parts[0])
        v = int(parts[1])

        weight = float(parts[2]) if len(parts) > 2 else 1.0
        
        graph.add_edge(u, v, weight)
        
    return graph

def load_graph_fast(filepath: str, graph_class, directed: bool = False, weighted: bool = False) -> Graph:
    with open(filepath, 'r') as f:
        # Iterator über die Datei erstellen (viel schneller als f.readlines())
        file_iter = iter(f)
        
        # Erste Zeile lesen
        try:
            num_nodes = int(next(file_iter))
        except StopIteration:
            raise ValueError("Die Datei ist leer.")
            
        graph = graph_class(num_nodes, directed)
        
        # Methoden-Lookup aus der Schleife ziehen (bringt ordentlich Speed in Python)
        add_edge = graph.add_edge
        
        # Fallunterscheidung aus der Schleife ziehen
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

def bfs(graph: Graph, start_node: int) -> List[int]:
    """Führt eine Breitensuche (BFS) durch."""
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

# def bfs_yield(graph: Graph, start_node: int) -> Iterator[int]:
#     """Führt eine Breitensuche (BFS) durch."""
#     visited = {start_node}
#     queue = deque([start_node])
    
#     while queue:
#         current = queue.popleft()
#         yield current
        
#         for neighbor, _ in graph.get_neighbors(current):
#             if neighbor not in visited:
#                 visited.add(neighbor)
#                 queue.append(neighbor)

# def bfs(graph: Graph, start_node: int) -> list[int]:
#     return list(bfs_yield(graph, start_node))

def count_connected_components(graph: Graph) -> int:
    """Berechnet die Anzahl der Zusammenhangskomponenten."""
    visited_global = set()
    components = 0
    
    for node in graph.get_nodes():
        if node not in visited_global:
            components += 1
            component_nodes = set(bfs(graph, node))
            visited_global.update(component_nodes)
            
    return components