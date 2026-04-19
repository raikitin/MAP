from abc import ABC, abstractmethod
from collections.abc import Iterator
import io
import time
from typing import List, Tuple, Iterable
from collections import deque

class Graph(ABC):
    
    @abstractmethod
    def add_edge(self, u: int, v: int, weight: float = 0.0) -> None:
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

    @property
    @abstractmethod
    def is_weighted(self) -> bool:
        pass


class AdjacencyListGraph(Graph):
    def __init__(self, num_nodes: int, directed: bool = False, weighted: bool = False):
        self.num_nodes = num_nodes
        self._directed = directed
        self._weighted = weighted
        # [ Knoten -> [(Nachbar, Gewicht), ...] ]
        self.adj_list: List[List[Tuple[int, float]]] = [[] for _ in range(num_nodes)]

    @property
    def is_directed(self) -> bool:
        return self._directed

    @property
    def is_weighted(self) -> bool:
        return self._weighted

    def add_edge(self, u: int, v: int, weight: float = 0.0) -> None:
        self.adj_list[u].append((v, weight))
        if not self._directed:
            self.adj_list[v].append((u, weight))

    def get_neighbors(self, u: int) -> Iterable[Tuple[int, float]]:
        return self.adj_list[u]

    def get_nodes(self) -> Iterable[int]:
        return range(self.num_nodes)


class AdjacencyMatrixGraph(Graph):
    def __init__(self, num_nodes: int, directed: bool = False, weighted: bool = False):
        self.num_nodes = num_nodes
        self._directed = directed
        self._weighted = weighted
        self.matrix = [[None for _ in range(num_nodes)] for _ in range(num_nodes)]

    @property
    def is_directed(self) -> bool:
        return self._directed

    @property
    def is_weighted(self) -> bool:
        return self._weighted

    def add_edge(self, u: int, v: int, weight: float = 0.0) -> None:
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


def load_graph_fast(filepath: str, graph_class, directed: bool = False, weighted: bool = True) -> Graph:
    
    with open(filepath, 'r') as f:
        file_iter = iter(f)
        
        try:
            num_nodes = int(next(file_iter))
        except StopIteration:
            raise ValueError("Die Datei ist leer.")
            
        graph = graph_class(num_nodes, directed, weighted)
        add_edge = graph.add_edge
        
        # Langsamer Teil
        if weighted:
            for line in file_iter:
                parts = line.split()
                if parts:
                    add_edge(int(parts[0]), int(parts[1]), float(parts[2]))
        else:
            for line in file_iter:
                parts = line.split()
                if parts:
                    add_edge(int(parts[0]), int(parts[1]), 0.0)
                    
    return graph


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
    # visited_global = set()
    visited = [False] * graph.num_nodes
    components = 0
    all_nodes = graph.get_nodes()
    
    # Erster BFS erzeugt 95% der Analyse Zeit
    for node in all_nodes:
        # if node not in visited_global:
        if not visited[node]:
            components += 1
            component_nodes = bfs(graph, node)
            for component_node in component_nodes:
                visited[component_node] = True
            # visited_global.update(component_nodes)

    return components

def load_graph(filepath: str, graph_class, directed: bool = False, weighted: bool = False) -> Graph:
    
    t_start = time.perf_counter()
    with io.open(filepath, 'r') as f:
        lines = f.readlines()
    t_end = time.perf_counter()
    print(f"File-Read abgeschlossen in {(t_end - t_start):.4f} s.")
    
    num_nodes = int(lines[0].strip())
    
    graph = graph_class(num_nodes, directed, weighted)
    # add_edge = graph.add_edge()
    
    if weighted:
        for line in lines[1:]:
            parts = line.split()
            if parts:
                graph.add_edge(int(parts[0]), int(parts[1]), float(parts[2]))
    else:
        for line in lines[1:]:
            parts = line.split()
            if parts:
                graph.add_edge(int(parts[0]), int(parts[1]), 0.0)
        
    return graph