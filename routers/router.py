import threading
import time
import os
import json
import socket
import heapq


class Topologia:
    def __init__(self, caminho_arquivo):
        self.caminho = caminho_arquivo
        self.topologia = self._carregar()

    def _carregar(self):
        with open(self.caminho) as f:
            return json.load(f)

    def obter_vizinhos(self, roteador_id):
        return self.topologia.get(roteador_id, {})


class LinkStateDatabase:
    def __init__(self):
        self.db = {}

    def update(self, router_id, neighbors):
        changed = router_id not in self.db or self.db[router_id] != neighbors
        self.db[router_id] = neighbors
        return changed

    def get_all(self):
        return self.db


class PacketManager:
    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip, port))

    def send(self, ip, port, data):
        payload = data.encode() if isinstance(data, str) else data
        self.sock.sendto(payload, (ip, port))

    def receive(self):
        data, addr = self.sock.recvfrom(4096)
        return data.decode(), addr


class Dijkstra:
    @staticmethod
    def calcular(lsdb, origem):
        print(f"[{origem}] Iniciando cálculo de rotas com LSDB: {lsdb}", flush=True)

        dist = {n: float("inf") for n in lsdb}
        dist[origem] = 0
        prev = {}
        visitados = set()
        queue = [(0, origem)]

        while queue:
            custo, atual = heapq.heappop(queue)
            if atual in visitados:
                continue
            visitados.add(atual)

            for vizinho, dados in lsdb.get(atual, {}).items():
                try:
                    peso = dados[2]
                except Exception:
                    print(
                        f"[{origem}] ERRO ao acessar peso de {vizinho}: {dados}", flush=True)
                    continue

                novo_custo = custo + peso
                if novo_custo < dist.get(vizinho, float("inf")):
                    dist[vizinho] = novo_custo
                    prev[vizinho] = atual
                    heapq.heappush(queue, (novo_custo, vizinho))

        # Montar tabela de próximos saltos
        tabela = {}
        for destino in dist:
            if destino == origem or dist[destino] == float("inf"):
                continue
            caminho = Dijkstra._reconstruir_caminho(prev, origem, destino)
            if len(caminho) > 1:
                tabela[destino] = caminho[1]

        print(f"[{origem}] Tabela de distâncias: {dist}", flush=True)
        print(f"[{origem}] Tabela de próximos saltos: {tabela}", flush=True)
        return tabela

    @staticmethod
    def _reconstruir_caminho(prev, origem, destino):
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


class Router:
    def __init__(self):
        self.router_id = os.environ.get("ROTEADOR_ID", "RX")
        self.topologia = Topologia("configs/topologia.json")
        self.vizinhos = self.topologia.obter_vizinhos(self.router_id)
        self.lsdb = LinkStateDatabase()
        self.lsdb.update(self.router_id, self.vizinhos)
        self.packet_manager = PacketManager("0.0.0.0", 5000)

    def criar_pacote_hello(self):
        return {
            "type": "HELLO",
            "id": self.router_id,
            "vizinhos": self.vizinhos,
            "timestamp": time.time()
        }

    def criar_pacote_lsa(self):
        return json.dumps({
            "type": "LSA",
            "id": self.router_id,
            "vizinhos": self.vizinhos
        })

    def envia_hellos(self):
        while True:
            pacote = self.criar_pacote_hello()
            for vizinho_id, (ip, porta, _) in self.vizinhos.items():
                self.packet_manager.send(ip, porta, json.dumps(pacote))
                print(f"[{self.router_id}] [HELLO] enviado para {vizinho_id}")
            time.sleep(5)

    def envia_lsa_para_todos(self):
        pacote = self.criar_pacote_lsa()
        for vizinho_id, (ip, porta, _) in self.vizinhos.items():
            self.packet_manager.send(ip, porta, pacote)
            print(f"[{self.router_id}] [LSA] enviado para {vizinho_id}")

    def recebe_pacotes(self):
        while True:
            data, addr = self.packet_manager.receive()
            try:
                pacote = json.loads(data)
            except Exception as e:
                print(f"[{self.router_id}] Erro ao decodificar pacote: {e}")
                continue

            tipo = pacote.get("type")
            remetente = pacote.get("id")
            vizinhos = pacote.get("vizinhos", {})

            if tipo == "HELLO":
                print(f"[{self.router_id}] [HELLO] recebido de {remetente}")
                if self.lsdb.update(remetente, vizinhos):
                    print(f"[{self.router_id}] LSDB atualizada com {remetente}")
                    self.envia_lsa_para_todos()

            elif tipo == "LSA":
                print(f"[{self.router_id}] [LSA] recebido de {remetente}")
                if self.lsdb.update(remetente, vizinhos):
                    print(f"[{self.router_id}] LSDB atualizada com {remetente}")
                    self.envia_lsa_para_todos()

            else:
                print(f"[{self.router_id}] Pacote desconhecido: {tipo}")
                continue

            tabela = Dijkstra.calcular(self.lsdb.get_all(), self.router_id)
            self.configurar_rotas(tabela)

    def configurar_rotas(self, tabela):
        for destino, proximo in tabela.items():
            if proximo not in self.vizinhos:
                print(f"[{self.router_id}] ERRO: {proximo} não é vizinho.")
                continue
            ip_prox = self.vizinhos[proximo][0]
            rede = f"10.{destino[1:]}.0.0/24"
            comando = f"ip route replace {rede} via {ip_prox}"
            print(f"[{self.router_id}] Rota: {comando}")
            os.system(comando)

    def run(self):
        os.system("sysctl -w net.ipv4.ip_forward=1")
        print(f"[{self.router_id}] Roteador iniciado.")
        threading.Thread(target=self.envia_hellos, daemon=True).start()
        threading.Thread(target=self.recebe_pacotes, daemon=True).start()
        while True:
            time.sleep(30)


if __name__ == "__main__":
    roteador = Router()
    roteador.run()
