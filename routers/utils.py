import json
import heapq


def parse_topologia(file_path, roteador_id):
    with open(file_path) as f:
        dados = json.load(f)
    return dados[roteador_id]


def dijkstra(lsdb, origem):
    dist = {node: float('inf') for node in lsdb}
    dist[origem] = 0
    visited = set()
    pq = [(0, origem)]

    while pq:
        custo, atual = heapq.heappop(pq)
        if atual in visited:
            continue
        visited.add(atual)

        for vizinho, (_, _, custo_viz) in lsdb.get(atual, {}).items():
            if dist[atual] + custo_viz < dist[vizinho]:
                dist[vizinho] = dist[atual] + custo_viz
                heapq.heappush(pq, (dist[vizinho], vizinho))

    print(f"[{origem}] Tabela de distâncias: {dist}")
