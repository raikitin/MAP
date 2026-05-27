import time
import os

from graph import *
from mst import *
from tsp import *
from sp import *
from max_flow import *

def run_benchmarks(is_weighted: bool, is_directed: bool, test_files: list, run_bfs: bool, run_mst: bool, run_tsp: bool, run_tsp_exact: bool, run_shortest_paths: bool, run_max_flow: bool):
    
    print(f"{'='*60}")
    print(f"{'GRAPHEN-PRAKTIKUM: BENCHMARKING':^60}")
    print(f"{'='*60}\n")

    for filepath in test_files:
        print(f"--- Starte Auswertung für: {filepath} ---")
        
        if not os.path.exists(filepath):
            print(f"[Fehler] Datei '{filepath}' nicht gefunden. Überspringe...\n")
            continue

        # ---------------------------------------------------------
        # 0. EINLESEN
        # ---------------------------------------------------------
        t_start = time.perf_counter()
        graph = load_graph_fast(filepath, AdjacencyListGraph, directed=is_directed, weighted=is_weighted)
        # graph = load_graph(filepath, AdjacencyListGraph, directed=is_directed, weighted=is_weighted)
        t_end = time.perf_counter()

        if run_tsp_exact:
            graph = load_graph_fast(filepath, AdjacencyMatrixGraph, directed=is_directed, weighted=is_weighted)
        
        # num_nodes = len(list(graph.get_nodes()))
        num_nodes = graph.num_nodes
        print(f"Einlesen abgeschlossen in {(t_end - t_start):.4f} s.")
        print(f"-> Knotenanzahl: {num_nodes}")

        is_connected = True # Standard-Annahme, falls BFS nicht ausgeführt wird

        # ---------------------------------------------------------
        # 1. ZUSAMMENHANGSKOMPONENTEN (BFS)
        # ---------------------------------------------------------
        if run_bfs:
            t_start = time.perf_counter()
            components = count_connected_components(graph)
            t_end = time.perf_counter()
            print(f"[BFS] Zusammenhangskomponenten : {components} \t| Zeit: {(t_end - t_start):.6f} s")
            
            if components > 1:
                is_connected = False
                print("[Info] Graph besteht aus mehreren Komponenten.")

        # ---------------------------------------------------------
        # 2. MINIMAL SPANNENDE BÄUME (MST)
        # ---------------------------------------------------------
        if run_mst:
            if not is_connected:
                print("[MST] Übersprungen (Graph ist nicht zusammenhängend).")
            else:
                t_start = time.perf_counter()
                # weight_prim, _ = prim(graph)
                weight_prim, _ = prim_optimized(graph)
                t_end = time.perf_counter()
                print(f"[MST] Prim Gesamtgewicht       : {weight_prim:.4f} \t| Zeit: {(t_end - t_start):.6f} s")

                t_start = time.perf_counter()
                weight_kruskal, _ = kruskal(graph)
                t_end = time.perf_counter()
                print(f"[MST] Kruskal Gesamtgewicht    : {weight_kruskal:.4f} \t| Zeit: {(t_end - t_start):.6f} s")

        # ---------------------------------------------------------
        # 3.1 TSP HEURISTIKEN (Teil 1)
        # ---------------------------------------------------------
        if run_tsp:
            if not is_connected:
                print("[TSP] Übersprungen (Graph ist nicht zusammenhängend).")
            else:
                try:
                    t_start = time.perf_counter()
                    dist_nn, tour = nearest_neighbor(graph)
                    t_end = time.perf_counter()
                    print(f"[TSP] Nearest-Neighbour Distanz: {dist_nn:.4f} \t| Zeit: {(t_end - t_start):.6f} s")
                    print(f"[TSP] Nearest-Neighbour Tour   : {tour}")
                except Exception as e:
                    print(f"[TSP] Nearest-Neighbour fehlgeschlagen: {e}")

                try:
                    t_start = time.perf_counter()
                    dist_dt, tour = double_tree(graph)
                    t_end = time.perf_counter()
                    print(f"[TSP] Doppelter-Baum Distanz   : {dist_dt:.4f} \t| Zeit: {(t_end - t_start):.6f} s")
                    print(f"[TSP] Doppelter-Baum Tour      : {tour}")
                except Exception as e:
                    print(f"[TSP] Doppelter-Baum fehlgeschlagen: {e}")

        # ---------------------------------------------------------
        # 3.2 TSP EXAKT (Teil 2)
        # ---------------------------------------------------------
        if run_tsp_exact:
            if not is_connected:
                print("[TSP Exakt] Übersprungen (Graph ist nicht zusammenhängend).")
            elif num_nodes > 12:
                print(f"[TSP Exakt] Übersprungen: Graph zu groß (Knoten = {num_nodes}). Max erlaubt: 12.")
            else:
                try:
                    t_start = time.perf_counter()
                    # dist_bb, _ = tsp_branch_and_bound(graph)
                    dist_bb, tour = tsp_branch_and_bound_optimized(graph)
                    t_end = time.perf_counter()
                    print(f"[TSP] Branch & Bound Distanz : {dist_bb:.4f} \t| Zeit: {(t_end - t_start):.6f} s")
                    # print(f"[TSP] Branch & Bound Tour      : {tour}")
                except Exception as e:
                    print(f"[TSP] Branch & Bound fehlgeschlagen: {e}")
                    
                try:
                    t_start = time.perf_counter()
                    dist_bf, tour = tsp_brute_force(graph)
                    t_end = time.perf_counter()
                    print(f"[TSP] Brute-Force Distanz    : {dist_bf:.4f} \t| Zeit: {(t_end - t_start):.6f} s")
                    # print(f"[TSP] Brute-Force Tour      : {tour}")
                except Exception as e:
                    print(f"[TSP] Brute-Force fehlgeschlagen: {e}")

        # ---------------------------------------------------------
        # 4. KÜRZESTE WEGE (Dijkstra & Moore-Bellman-Ford)
        # ---------------------------------------------------------
        if run_shortest_paths:
            kontroll_tests = [
                {"file": "Wege1.txt", "directed": True,  "start": 2, "target": 0},
                {"file": "Wege2.txt", "directed": True,  "start": 2, "target": 0},
                {"file": "Wege3.txt", "directed": True,  "start": 0, "target": 1},
                {"file": "G_1_2.txt", "directed": True,  "start": 0, "target": 1},
                {"file": "G_1_2.txt", "directed": False, "start": 0, "target": 1},
            ]

            current_filename = os.path.basename(filepath)
            tests_for_current_file = [t for t in kontroll_tests if t["file"] == current_filename]

            for test in tests_for_current_file:
                sp_graph = load_graph_fast(filepath, AdjacencyListGraph, directed=test["directed"], weighted=True)
                # sp_graph = graph
                start_n = test["start"]
                target_n = test["target"]

                dir_str = "gerichtet" if test["directed"] else "ungerichtet"
                print(f"-> Wege-Test ({dir_str}): Knoten {start_n} zu Knoten {target_n}")

                # DIJKSTRA
                try:
                    t_start = time.perf_counter()
                    dist_dijkstra, parents = dijkstra(sp_graph, start_n)
                    t_end = time.perf_counter()
                    
                    val_d = dist_dijkstra[target_n]
                    str_d = f"{val_d:.5f}".rstrip('0').rstrip('.') if val_d != float('inf') else "Unerreichbar"
                    print(f"[Dijkstra]     : {str_d:^16} | Zeit: {(t_end - t_start):.6f} s")
                    # Rekonstruiere den Weg
                    tour = reconstruct_path(parents, target_n)
                    # print(f"[Dijkstra]     : Tour      : {tour}")
                except Exception as e:
                    print(f"[Dijkstra]     : Fehlgeschlagen ({e})")

                # BELLMAN-FORD
                try:
                    t_start = time.perf_counter()
                    dist_mbf, parents = bellman_ford(sp_graph, start_n)
                    t_end = time.perf_counter()
                    
                    val_m = dist_mbf[target_n]
                    str_m = f"{val_m:.5f}".rstrip('0').rstrip('.') if val_m != float('inf') else "Unerreichbar"
                    print(f"[Bellman-Ford] : {str_m:^16} | Zeit: {(t_end - t_start):.6f} s")
                    # Rekonstruiere den Weg
                    tour = reconstruct_path(parents, target_n)
                    # print(f"[Bellman-Ford] : Tour      : {tour}")
                except Exception as e:
                    print(f"[Bellman-Ford] : Fehlgeschlagen ({e})")
                print("")

        # ---------------------------------------------------------
        # 5. MAXIMALE FLÜSSE (Edmonds-Karp)
        # ---------------------------------------------------------
        if run_max_flow:
            fluss_kontroll_tests = [
                {"file": "Fluss.txt",  "directed": True, "start": 0, "target": 7, "expected": "4"},
                {"file": "Fluss2.txt", "directed": True, "start": 0, "target": 7, "expected": "5"},
                {"file": "G_1_2.txt",  "directed": True, "start": 0, "target": 7, "expected": "0.75447"},
            ]

            current_filename = os.path.basename(filepath)
            tests_for_current_file = [t for t in fluss_kontroll_tests if t["file"] == current_filename]

            for test in tests_for_current_file:
                # Graph zwingend als gerichtet einlesen, da Flussnetzwerke Richtungen haben!
                # flow_graph = load_graph_fast(filepath, AdjacencyListGraph, directed=test["directed"], weighted=True)
                flow_graph = graph
                start_n = test["start"]
                target_n = test["target"]
                # expected = test["expected"]

                print(f"-> Fluss-Test: Quelle {start_n} zu Senke {target_n}")

                try:
                    t_start = time.perf_counter()
                    flow = edmonds_karp(flow_graph, start_n, target_n)
                    t_end = time.perf_counter()
                    
                    str_flow = f"{flow:.5f}".rstrip('0').rstrip('.')
                    print(f"[Edmonds-Karp] : Max Fluss = {str_flow:^8} | Zeit: {(t_end - t_start):.6f} s")
                except Exception as e:
                    print(f"[Edmonds-Karp] : Fehlgeschlagen ({e})")

        print("\n" + "-"*60 + "\n")


if __name__ == "__main__":
    
    FILE_SETS = {
        "bfs_tests": [
            "example/graph/Graph1.txt",
            "example/graph/Graph2.txt",
            "example/graph/Graph3.txt",
            "example/graph/Graph_gross.txt",
            "example/graph/Graph_ganzgross.txt",
            "example/graph/Graph_ganzganzgross.txt"
        ],
        "mst_tests": [
            "example/mst/G_1_2.txt",
            "example/mst/G_1_20.txt",
            "example/mst/G_1_200.txt",
            "example/mst/G_10_20.txt",
            "example/mst/G_10_200.txt",
            "example/mst/G_100_200.txt"
        ],
        "tsp_tests": [
            "example/tsp/K_10.txt",
            "example/tsp/K_10e.txt",
            "example/tsp/K_12.txt",
            "example/tsp/K_12e.txt",
            "example/tsp/K_15.txt",
            "example/tsp/K_15e.txt",
            "example/tsp/K_20.txt",
            "example/tsp/K_30.txt",
            "example/tsp/K_50.txt",
            "example/tsp/K_70.txt",
            "example/tsp/K_100.txt"
        ],
        "sp_tests": [
            "example/sp/Wege1.txt",
            "example/sp/Wege2.txt",
            "example/sp/Wege3.txt",
            "example/sp/G_1_2.txt"
        ],
        "max_flow_tests": [
            "example/max_flow/Fluss.txt",
            "example/max_flow/Fluss2.txt",
            "example/sp/G_1_2.txt"
        ]
    }
    
    # Auswahl der Testdateien
    AKTUELLER_TEST = FILE_SETS["sp_tests"]

    # Auswahl der Algorithmen
    RUN_BFS = True
    RUN_MST = False
    RUN_TSP = False
    RUN_TSP_EXACT = False
    RUN_SP = True 
    RUN_MAX_FLOW = False

    is_weighted = True
    is_directed=True
    
    t_start_test = time.perf_counter()
    run_benchmarks(
        is_weighted=is_weighted,
        is_directed=is_directed,
        test_files=AKTUELLER_TEST,
        run_bfs=RUN_BFS,
        run_mst=RUN_MST,
        run_tsp=RUN_TSP,
        run_tsp_exact=RUN_TSP_EXACT,
        run_shortest_paths=RUN_SP,
        run_max_flow=RUN_MAX_FLOW
    )
    t_end_test = time.perf_counter()
    print(f"Gesamtdauer aller Benchmarks: {(t_end_test - t_start_test):.4f} Sekunden")