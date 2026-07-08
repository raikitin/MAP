from graph import MinCostFlowGraph, load_mcf_graph

def _get_initial_feasible_flow(graph: MinCostFlowGraph):
    balances = list(graph.balances)
    
    while True:
        # Quellen und Senken finden
        supply_nodes = [i for i, b in enumerate(balances) if b > 0]
        demand_nodes = [i for i, b in enumerate(balances) if b < 0]
        
        if not supply_nodes or not demand_nodes:
            break
            
        s = supply_nodes[0]
        
        # BFS für beliebigen Weg zu einer Senke zu finden
        queue = [s]
        parent_edge = [None] * graph.num_nodes
        visited = [False] * graph.num_nodes
        visited[s] = True
        
        target = None
        while queue and target is None:
            curr = queue.pop(0)
            for edge in graph.adj[curr]:
                if not visited[edge['to']] and edge['cap'] - edge['flow'] > 0:
                    visited[edge['to']] = True
                    parent_edge[edge['to']] = edge
                    queue.append(edge['to'])
                    if balances[edge['to']] < 0:
                        target = edge['to']
                        break
                        
        if target is None:
            raise ValueError("Problem ist unlösbar: Kein zulässiger Fluss möglich!")
            
        # Bottleneck finden
        path_cap = float('inf')
        curr = target
        while curr != s:
            edge = parent_edge[curr]
            path_cap = min(path_cap, edge['cap'] - edge['flow'])
            curr = edge['from']
            
        push_flow = min(balances[s], -balances[target], path_cap)
        
        # Fluss erhöhen
        curr = target
        while curr != s:
            edge = parent_edge[curr]
            edge['flow'] += push_flow
            edge['rev']['flow'] -= push_flow
            curr = edge['from']
            
        balances[s] -= push_flow
        balances[target] += push_flow


def cycle_canceling(graph: MinCostFlowGraph) -> float:
    # Startfluss mit BFS
    _get_initial_feasible_flow(graph)
    
    # Negative Zyklen suchen und eliminieren
    while True:
        dist = [0.0] * graph.num_nodes
        parent_edge = [None] * graph.num_nodes
        cycle_node = -1
        
        # Relaxiere alle Kanten V mal
        for _ in range(graph.num_nodes):
            changed = False
            for u in range(graph.num_nodes):
                for edge in graph.adj[u]:
                    # Kanten mit freien Kapazität
                    if edge['cap'] - edge['flow'] > 0:
                        if dist[u] + edge['cost'] < dist[edge['to']]:
                            dist[edge['to']] = dist[u] + edge['cost']
                            parent_edge[edge['to']] = edge
                            changed = True
                            cycle_node = edge['to']
                            
        if not changed:
            break # Kein negativer Zyklus mehr
            
        # Zyklus gefunden, V Schritte zurück um im Zyklus zu sein
        curr = cycle_node
        for _ in range(graph.num_nodes):
            curr = parent_edge[curr]['from']
            
        cycle_start = curr
        
        # Bottleneck vom Zyklus
        path_cap = float('inf')
        while True:
            edge = parent_edge[curr]
            path_cap = min(path_cap, edge['cap'] - edge['flow'])
            curr = edge['from']
            if curr == cycle_start:
                break
                
        # Fluss durch Zyklus schicken
        curr = cycle_start
        while True:
            edge = parent_edge[curr]
            edge['flow'] += path_cap
            edge['rev']['flow'] -= path_cap
            curr = edge['from']
            if curr == cycle_start:
                break

    # Kosten berechnen
    total_cost = 0.0
    for u in range(graph.num_nodes):
        for edge in graph.adj[u]:
            if edge['cap'] > 0 and edge['flow'] > 0:
                total_cost += edge['flow'] * edge['cost']
                
    return total_cost

def successive_shortest_path(graph: MinCostFlowGraph) -> float:
    
    # Initialisierung
    for u in range(graph.num_nodes):
        for edge in graph.adj[u]:
            edge['flow'] = 0.0
            
    balances = list(graph.balances)
    
    # negative Kanten sättigen
    for u in range(graph.num_nodes):
        for edge in graph.adj[u]:
            if edge['cap'] > 0 and edge['cost'] < 0:
                cap = edge['cap']
                edge['flow'] = cap
                edge['rev']['flow'] = -cap
                # Balancen anpassen
                balances[u] -= cap
                balances[edge['to']] += cap
    

    # Restlichen Fluss routen
    while True:
        
        supply_nodes = [i for i, b in enumerate(balances) if b > 0]
        demand_nodes = [i for i, b in enumerate(balances) if b < 0]
        
        if not supply_nodes or not demand_nodes:
            break # Alle Balancen ausgeglichen
            
        s = supply_nodes[0]
        
        # Bellman-Ford
        dist = [float('inf')] * graph.num_nodes
        parent_edge = [None] * graph.num_nodes
        dist[s] = 0.0
        
        for _ in range(graph.num_nodes - 1):
            changed = False
            for u in range(graph.num_nodes):
                if dist[u] == float('inf'):
                    continue
                for edge in graph.adj[u]:
                    res_cap = round(edge['cap'] - edge['flow'], 7)
                    if res_cap > 0:
                        if dist[u] + edge['cost'] < dist[edge['to']]:
                            dist[edge['to']] = dist[u] + edge['cost']
                            parent_edge[edge['to']] = edge
                            changed = True
            if not changed:
                break
                
        # Zielknoten mit den geringsten Transportkosten finden
        target = None
        min_dist = float('inf')
        for d in demand_nodes:
            if dist[d] < min_dist:
                min_dist = dist[d]
                target = d
                
        if target is None:
            raise ValueError("Problem unlösbar: Kann Fluss nicht weiter routen.")
            
        # Bottleneck bestimmen
        path_cap = float('inf')
        curr = target
        while curr != s:
            edge = parent_edge[curr]
            res_cap = edge['cap'] - edge['flow']
            path_cap = min(path_cap, res_cap)
            curr = edge['from']
            
        # Minimalen Fluss aus Angebot, Nachfrage und Kapazitätbestimmen
        push_flow = min(balances[s], -balances[target], path_cap)
        
        if push_flow <= 0:
            break
            
        # Fluss updaten
        curr = target
        while curr != s:
            edge = parent_edge[curr]
            edge['flow'] += push_flow
            edge['rev']['flow'] -= push_flow
            curr = edge['from']
            
        balances[s] -= push_flow
        balances[target] += push_flow

    # Gesamtkosten berechnen
    total_cost = 0.0
    for u in range(graph.num_nodes):
        for edge in graph.adj[u]:
            if edge['cap'] > 0 and edge['flow'] > 0:
                total_cost += edge['flow'] * edge['cost']
                
    return total_cost