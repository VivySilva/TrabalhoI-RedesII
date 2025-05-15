import threading  # Importando a biblioteca threading para criar threads
import socket  # Importando a biblioteca socket para comunicação de rede via UDP
import json  # Importando a biblioteca json para manipulação de dados em formato JSON
import os  # Importando a biblioteca os para manipulação de variáveis de ambiente
import time  # Importando a biblioteca time para manipulação de tempo
# Importando funções auxiliares do módulo utils
from utils import dijkstra, parse_topologia

# ID do roteador atual (padrão: "R1")
ROTEADOR_ID = os.getenv("ROTEADOR_ID", "R1")
# Armazenar todos os pacotes recebidos de vizinhos (Link State Database)
LSDB = {}
vizinhos = {}


def envia_pacotes(vizinhos):
    """
    Envia pacotes de estado de enlace para os vizinhos do roteador atual.

    -> Atributo:
    vizinhos: Dicionário contendo os vizinhos do roteador atual e suas informações (IP, porta, custo). 

    1. Cria um dicionário contendo o ID do roteador e os vizinhos com suas informações.
    2. Envia pacotes UDP para cada vizinho, contendo o dicionário criado.
    3. O envio é feito em um loop infinito, permitindo que o roteador envie pacotes continuamente.
    4. O pacote é enviado em formato JSON, codificado para bytes antes de ser enviado.
    5. O socket é fechado após o envio para liberar recursos.
    6. O envio é feito em uma thread separada para não bloquear o restante do código.    
    """
    while True:
        pacote = {
            "id": ROTEADOR_ID,
            "vizinhos": vizinhos
        }
        for vizinho_id, (ip, porta, custo) in vizinhos.items():
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.sendto(json.dumps(pacote).encode(), (ip, porta))
                print(
                    f"[{ROTEADOR_ID}] Enviando pacote para {vizinho_id} ({ip}:{porta})")
        time.sleep(20)


def recebe_pacotes():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 5000))

    while True:
        data, addr = s.recvfrom(1024)
        pacote = json.loads(data.decode())
        remetente = pacote.get("id")
        vizinhos_recebidos = pacote.get("vizinhos", {})

        print(f"[{ROTEADOR_ID}] Recebeu pacote de {remetente} ({addr[0]}:{addr[1]})")
        time.sleep(20)

        if not remetente or not isinstance(vizinhos_recebidos, dict):
            print(f"[{ROTEADOR_ID}] Pacote malformado de {addr}")
            continue

        # Atualiza ou mantém a LSDB
        if remetente not in LSDB:
            LSDB[remetente] = vizinhos_recebidos
        else:
            LSDB[remetente].update(vizinhos_recebidos)

        print(f"[{ROTEADOR_ID}] LSDB atualizada:")
        print(json.dumps(LSDB, indent=2))
        time.sleep(20)

        if ROTEADOR_ID not in LSDB:
            print(f"[{ROTEADOR_ID}] ERRO: Roteador ainda não se conhece na LSDB!")
            continue

        print(f"[{ROTEADOR_ID}] LSDB COMPLETA:")
        print(json.dumps(LSDB, indent=2))
        time.sleep(20)

        # Executa Dijkstra com LSDB completa
        tabela_proximos = dijkstra(LSDB, ROTEADOR_ID)
        configurar_rotas(tabela_proximos, ROTEADOR_ID, vizinhos)


def configurar_rotas(tabela_proximos, roteador_id, ip_vizinhos):
    for destino, proximo_salto in tabela_proximos.items():
        if proximo_salto not in ip_vizinhos:
            print(
                f"[{roteador_id}] ERRO: IP do próximo salto '{proximo_salto}' não encontrado.")
            continue

        ip_gateway = ip_vizinhos[proximo_salto][0]  # exemplo: "172.50.0.4"

        # Constrói a rede do destino (ex: R3 → 10.3.0.0/24)
        num = destino[1]
        rede_destino = f"10.{num}.0.0/24"

        comando = f"ip route replace {rede_destino} via {ip_gateway}"
        print(f"[{roteador_id}] Executando: {comando}")
        os.system(comando)


def main():
    global LSDB, ROTEADOR_ID, vizinhos

    ROTEADOR_ID = os.environ.get("ROTEADOR_ID", "RX")
    vizinhos = parse_topologia("configs/topologia.json", ROTEADOR_ID)

    # ✅ Adiciona o próprio roteador na LSDB antes de tudo
    LSDB = {ROTEADOR_ID: vizinhos}

    print(f"[{ROTEADOR_ID}] LSDB inicial:")
    print(json.dumps(LSDB, indent=2))

    # Inicia envio e recebimento de pacotes
    threading.Thread(target=envia_pacotes, args=(
        vizinhos,), daemon=True).start()
    threading.Thread(target=recebe_pacotes, daemon=True).start()

    # Loop principal
    while True:
        time.sleep(40)


if __name__ == "__main__":
    main()
