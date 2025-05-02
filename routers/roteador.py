import threading  # Importando a biblioteca threading para criar threads
import socket  # Importando a biblioteca socket para comunicação de rede via UDP
import json  # Importando a biblioteca json para manipulação de dados em formato JSON
# Importando funções auxiliares para manipulação de topologia e algoritmo de Dijkstra
from utils import dijkstra, parse_topologia

ROTEADOR_ID = "R1"  # Identificador do roteador atual

# Armazenar todos os pacotes recebidos de vizinhos (Link State Database)
LSDB = {}


def envia_pacotes(vizinhos):
    """
    Envia pacotes de estado de enlace para os vizinhos do roteador atual.

    -> Atributo:
    Vizinhos: Dicionário contendo os vizinhos do roteador atual e suas informações (IP, porta, custo). 

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


def recebe_pacotes():
    """
    Recebe pacotes de estado de enlace enviados por outros roteadores.

    1. Cria um socket UDP para receber pacotes de outros roteadores.
    2. O socket recebe pacotes em formato JSON, decodificados para strings.
    3. Os pacotes recebidos são armazenados na LSDB (Link State Database).
    4. O dicionário LSDB é atualizado com o ID do roteador e os vizinhos recebidos.
    5. O algoritmo de Dijkstra é chamado para calcular as rotas a partir da LSDB atualizada.
    6. O recebimento é feito em uma thread separada para não bloquear o restante do código.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 5000))  # porta padrão
    while True:
        data, _ = s.recvfrom(1024)
        pacote = json.loads(data.decode())
        LSDB[pacote["id"]] = pacote["vizinhos"]
        dijkstra(LSDB, ROTEADOR_ID)


def main():
    """
    Função principal do roteador.

    1. Chama a função parse_topologia para obter os vizinhos do roteador atual.
    2. Cria duas threads para enviar e receber pacotes de estado de enlace.
    3. A primeira thread envia pacotes para os vizinhos do roteador atual.
    4. A segunda thread recebe pacotes de outros roteadores.
    5. Aguarda o usuário pressionar ENTER para sair do programa.
    """
    vizinhos = parse_topologia("configs/topologia.json", ROTEADOR_ID)

    threading.Thread(target=envia_pacotes, args=(
        vizinhos,), daemon=True).start()
    threading.Thread(target=recebe_pacotes, daemon=True).start()

    input("Pressione ENTER para sair...")


if __name__ == "__main__":
    main()
