import time
import os

from graph import *
from mst import *
from tsp import *

def run_benchmarks(is_weighted: bool, is_directed: bool, test_files: list, run_bfs: bool, run_mst: bool, run_tsp: bool, run_tsp_exact: bool):
    
    print(f"{'='*60}")
    print(f"{'GRAPHEN-PRAKTIKUM: BENCHMARKING':^60}")
    print(f"{'='*60}\n")

    for filepath in test_files:
        print(f"--- Starte Auswertung für: {filepath} ---")
        
        if not os.path.exists(filepath):
            print(f"[Fehler] Datei '{filepath}' nicht gefunden. Überspringe...\n")
            continue

        # ---------------------------------------------------------
        # 1. EINLESEN
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
        # 2. ZUSAMMENHANGSKOMPONENTEN (BFS)
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
        # 3. MINIMAL SPANNENDE BÄUME (MST)
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
        # 4. TSP HEURISTIKEN (Teil 1)
        # ---------------------------------------------------------
        if run_tsp:
            if not is_connected:
                print("[TSP] Übersprungen (Graph ist nicht zusammenhängend).")
            else:
                try:
                    t_start = time.perf_counter()
                    dist_nn, _ = nearest_neighbor(graph)
                    t_end = time.perf_counter()
                    print(f"[TSP] Nearest-Neighbour Distanz: {dist_nn:.4f} \t| Zeit: {(t_end - t_start):.6f} s")
                except Exception as e:
                    print(f"[TSP] Nearest-Neighbour fehlgeschlagen: {e}")

                try:
                    t_start = time.perf_counter()
                    dist_dt, _ = double_tree(graph)
                    t_end = time.perf_counter()
                    print(f"[TSP] Doppelter-Baum Distanz   : {dist_dt:.4f} \t| Zeit: {(t_end - t_start):.6f} s")
                except Exception as e:
                    print(f"[TSP] Doppelter-Baum fehlgeschlagen: {e}")

        # ---------------------------------------------------------
        # 5. TSP EXAKT (Teil 2)
        # ---------------------------------------------------------
        if run_tsp_exact:
            if not is_connected:
                print("[TSP Exakt] Übersprungen (Graph ist nicht zusammenhängend).")
            elif num_nodes > 12:
                print(f"[TSP Exakt] Übersprungen: Graph zu groß (Knoten = {num_nodes}). Max erlaubt: 12.")
            else:
                try:
                    t_start = time.perf_counter()
                    dist_bb, _ = tsp_branch_and_bound(graph)
                    t_end = time.perf_counter()
                    print(f"[TSP] Branch & Bound Distanz : {dist_bb:.4f} \t| Zeit: {(t_end - t_start):.6f} s")
                except Exception as e:
                    print(f"[TSP] Branch & Bound fehlgeschlagen: {e}")
                    
                try:
                    t_start = time.perf_counter()
                    dist_bf, _ = tsp_brute_force(graph)
                    t_end = time.perf_counter()
                    print(f"[TSP] Brute-Force Distanz    : {dist_bf:.4f} \t| Zeit: {(t_end - t_start):.6f} s")
                except Exception as e:
                    print(f"[TSP] Brute-Force fehlgeschlagen: {e}")

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
        ]
    }
    
    # Auswahl der Testdateien
    AKTUELLER_TEST = FILE_SETS["mst_tests"]

    # Auswahl der Algorithmen
    RUN_BFS = True
    RUN_MST = True
    RUN_TSP = False
    RUN_TSP_EXACT = False

    is_weighted = False
    if RUN_MST or RUN_TSP or RUN_TSP_EXACT:
        is_weighted = True
    
    t_start_test = time.perf_counter()
    run_benchmarks(
        is_weighted=is_weighted,
        is_directed=False,
        test_files=AKTUELLER_TEST,
        run_bfs=RUN_BFS,
        run_mst=RUN_MST,
        run_tsp=RUN_TSP,
        run_tsp_exact=RUN_TSP_EXACT
    )
    t_end_test = time.perf_counter()
    print(f"Gesamtdauer aller Benchmarks: {(t_end_test - t_start_test):.4f} Sekunden")