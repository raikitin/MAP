from collections import deque
from time import time

class Graph:
    def __init__(self, filename: str, is_directed=False, is_weighted=False):
        self.directed = is_directed
        self.is_weighted = is_weighted

        with open(filename, 'r') as f:
            # Erste Zeile auslesen
            first_line = f.readline().strip()
            num_vertices = int(first_line)

            self.num_vertices = num_vertices
            # Adjazenzliste: Der Index ist der Knoten, der Wert ist eine Liste seiner Nachbarn.
            self.adj_list = [[] for _ in range(num_vertices)]

            # Restliche Zeilen iterieren
            for line in f:
                if not line.strip():
                    continue

                u, v = map(int, line.split())
                self.add_edge(u, v, self.directed)

    def add_edge(self, u, v, is_directed=False, weight=1):
        if self.is_weighted:
            self.adj_list[u].append((v, weight))
            if not is_directed:
                self.adj_list[v].append((u, weight))
        else:
            self.adj_list[u].append(v)
            if not is_directed:
                self.adj_list[v].append(u)

    def __str__(self):
        if self.is_weighted:
            result = []
            for i, neighbors in enumerate(self.adj_list):
                neighbor_str = ', '.join(f"{v}({w})" for v, w in neighbors)
                result.append(f"{i}: {neighbor_str}")
            return f"{self.num_vertices}\n" + "\n".join(result)

        result = []
        for i, neighbors in enumerate(self.adj_list):
            result.append(f"{i}: {', '.join(map(str, neighbors))}")
        return f"{self.num_vertices}\n" + "\n".join(result)

# Gemini-Funktion zum Ausgeben des BFS-Baums
def print_bfs_tree(parents: dict, discovery_order: list, start: int):
    """Gibt den BFS-Baum als Baumstruktur aus."""
    children = {node: [] for node in parents}
    for node in discovery_order[1:]:
        parent = parents[node]
        children[parent].append(node)

    step_of = {node: i for i, node in enumerate(discovery_order)}
    print("\nBFS-Baum:")
    print(f"{start} (Start)")

    def _print_subtree(node: int, prefix: str = ""):
        node_children = children.get(node, [])
        for i, child in enumerate(node_children):
            is_last = i == len(node_children) - 1
            connector = "`-- " if is_last else "|-- "
            print(f"{prefix}{connector}{child} (Schritt {step_of[child]})")
            next_prefix = prefix + ("    " if is_last else "|   ")
            _print_subtree(child, next_prefix)

    _print_subtree(start)

def bfs(graph: Graph, start: int, visited=None):
    parents = {start: None}
    discovery_order = [start]

    queue = deque([start])
    if visited is None:
        visited = [False] * graph.num_vertices
        
    visited[start] = True

    while queue:
        k = queue.popleft()

        for n in graph.adj_list[k]:
            if graph.is_weighted: 
                neighbor = n[0] 
            else: 
                neighbor = n
            
            if not visited[neighbor]:
                visited[neighbor] = True
                queue.append(neighbor)
                parents[neighbor] = k
                discovery_order.append(neighbor)

    return parents, discovery_order, visited

def anz_zsmhg_komponenten(graph: Graph):
    global_visited = [False] * graph.num_vertices
    count = 0

    for vertex in range(graph.num_vertices):
        if not global_visited[vertex]:
            count += 1
            bfs(graph, vertex, global_visited)

    return count

if __name__ == "__main__":
    timeStart = time()
    # paths = ['MAP\example\graph\Graph1.txt', 
    #          'MAP\example\graph\Graph2.txt', 
    #          'MAP\example\graph\Graph3.txt', 
    #          'MAP\example\graph\Graph_gross.txt', 
    #          'MAP\example\graph\Graph_ganzgross.txt', 
    #          'MAP\example\graph\Graph_ganzganzgross.txt'
    #          ]
    paths = ['MAP\example\graph\Graph_ganzganzgross.txt']
    Graphen = [Graph(path) for path in paths]
    timeEnd = time()
    print(f"Zeit zum Einlesen der Graphen: {timeEnd - timeStart:.4f} Sekunden")
    
    timeStart = time()
    for i, graph in enumerate(Graphen):
        print(f"Anzahl der zusammenhängenden Komponenten von Graph{i+1}: {anz_zsmhg_komponenten(graph)}")
    timeEnd = time()
    print(f"Zeit zum Berechnen der zusammenhängenden Komponenten: {timeEnd - timeStart:.4f} Sekunden")