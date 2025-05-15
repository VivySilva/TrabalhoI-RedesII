import heapq
import json  # Necessário para manipulação de JSON
import heapq  # Necessário para implementar a fila de prioridade no algoritmo de Dijkstra
import os  # Necessário para manipulação de caminhos de arquivos
import time


def parse_topologia(file_path, roteador_id):
    """
    Lê o arquivo de topologia e retorna os vizinhos do roteador especificado.

    -> Parâmetros:
    file_path: Caminho do arquivo JSON contendo a topologia.
    roteador_id: ID do roteador para o qual se deseja obter os vizinhos.

    -> Retorno:
    dados: Dicionário contendo os vizinhos do roteador especificado.

    1. Abre o arquivo JSON e carrega os dados.
    2. Atribuí os dados do roteador especificado a uma variável.
    3. Retorna os dados do roteador especificado. Usando o método get para evitar KeyError caso o roteador não exista.
    """
    with open(file_path) as f:
        dados = json.load(f)
    return dados.get(roteador_id, {})


def dijkstra(lsdb, origem):
    if origem not in lsdb:
        print(f"[{origem}] ERRO: Origem não encontrada na LSDB!")
        return {}

    dist = {node: float('inf') for node in lsdb}
    dist[origem] = 0
    prev = {}
    visitados = set()
    fila = [(0, origem)]

    while fila:
        custo, atual = heapq.heappop(fila)
        if atual in visitados:
            continue
        visitados.add(atual)

        print(f"[{origem}] Analisando vizinhos de {atual}:")
        for vizinho, dados in lsdb.get(atual, {}).items():
            print(f"  - {vizinho} => {dados}")
            time.sleep(1)

            try:
                peso = dados[2]
            except:
                print(f"[{origem}] ERRO ao acessar peso de {vizinho}: {dados}")
                continue

            novo_custo = custo + peso
            if novo_custo < dist.get(vizinho, float('inf')):
                dist[vizinho] = novo_custo
                prev[vizinho] = atual
                heapq.heappush(fila, (novo_custo, vizinho))

    # Reconstruir caminhos
    tabela_proximos = {}
    for destino in dist:
        if destino == origem or dist[destino] == float('inf'):
            continue
        caminho = reconstruir_caminho(prev, origem, destino)
        if len(caminho) > 1:
            tabela_proximos[destino] = caminho[1]

    print(f"[{origem}] Tabela de distâncias: {dist}")
    print(f"[{origem}] Tabela de próximos saltos: {tabela_proximos}")
    return tabela_proximos


def reconstruir_caminho(prev, origem, destino):
    caminho = []
    atual = destino

    while atual != origem:
        caminho.append(atual)
        atual = prev.get(atual)
        if atual is None:
            return []

    caminho.append(origem)
    caminho.reverse()

    return caminho
