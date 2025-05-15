import json  # Necessário para manipulação de JSON
import random  # Necessário para gerar números aleatórios


def gerar_topologia(num_roteadores, ip_base="192.168.0.", porta_base=5000):
    """
    Gera uma topologia de rede com um número especificado de roteadores.

    -> Parâmetros:
    num_roteadores: Número de roteadores na topologia.
    ip_base: Prefixo de IP para roteadores. (Padrão: "192.168.0.")
    porta_base: Porta base para roteadores. (Padrão: 5000)

    -> Retorno:
    topologia: Dicionário contendo a topologia gerada.

    1. Cria uma lista de roteadores com IDs "R1", "R2", ..., "Rn".
    2. Gera endereços IP para cada roteador com base no prefixo fornecido.
    3. Cria um dicionário para armazenar a topologia gerada.    
    4. Adiciona conexões aleatórias para garantir conectividade mínima.
    5. Adiciona conexões extras aleatórias entre os roteadores.
    6. Retorna a topologia gerada como um dicionário.
    """
    roteadores = [f"R{i+1}" for i in range(num_roteadores)]
    ips = {r: f"{ip_base}{i+1}" for i, r in enumerate(roteadores)}

    topologia = {r: {} for r in roteadores}

    for i in range(num_roteadores - 1):
        r1 = roteadores[i]
        r2 = roteadores[i + 1]
        custo = random.randint(1, 10)
        topologia[r1][r2] = [ips[r2], porta_base, custo]
        topologia[r2][r1] = [ips[r1], porta_base, custo]

    for _ in range(num_roteadores):
        r1, r2 = random.sample(roteadores, 2)
        if r2 not in topologia[r1]:
            custo = random.randint(1, 10)
            topologia[r1][r2] = [ips[r2], porta_base, custo]
            topologia[r2][r1] = [ips[r1], porta_base, custo]

    return topologia


def salvar_topologia(arquivo, topologia):
    with open(arquivo, "w") as f:
        json.dump(topologia, f, indent=4)


if __name__ == "__main__":
    topo = gerar_topologia(5)
    salvar_topologia("configs/topologia.json", topo)
    print("Topologia salva em configs/topologia.json")
