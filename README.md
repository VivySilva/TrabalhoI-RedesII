# Projeto de Roteamento por Estado de Enlace (Link-State Routing)

Este projeto foi desenvolvido como parte da disciplina **Redes de Computadores II** do curso de **Bacharelado em Sistemas de Informação** na **Universidade Federal do Piauí (UFPI)**. O objetivo é simular uma rede de computadores com múltiplos roteadores e hosts interligados, utilizando o algoritmo de **Roteamento por Estado de Enlace (LSR)**, baseado no protocolo UDP.

## Objetivo

Simular uma rede com roteadores e hosts utilizando contêiners Docker. Cada roteador é responsável por:

* Trocar mensagens HELLO com seus vizinhos;
* Anunciar o estado de seus enlaces via pacotes LSA (Link State Advertisement);
* Construir uma Link State Database (LSDB);
* Calcular rotas com o algoritmo de Dijkstra;
* Configurar rotas com base nas rotas mais curtas calculadas.

## Estrutura do Projeto

```bash
.
├── configs/
│   └── topologia.json         # Define os vizinhos de cada roteador (topologia da rede)
│   └── gerarTopologia.json    # Gera e salva em .json uma topologia aleatória (parcialmente conectada)
│   └── Topologia da Rede.png  # Imagem da topologia criada feita pela autora

├── docker/
│   ├── Dockerfile.roteador    # Imagem para contêiner dos roteadores
│   └── Dockerfile.host        # Imagem para contêiner dos hosts
├── hosts/
│   └── entrypoint.sh          # Script de inicialização dos hosts
├── routers/
│   └── router.py              # Implementação da lógica do roteador (classe Router e auxiliares)
├── test/
│   ├── testhost.sh            # Script de teste de ping entre hosts
│   └── testrouter.sh          # Script de teste de ping entre roteadores
├── docker-compose.yml         # Orquestra toda a topologia com Docker
└── README.md                  # Este arquivo
```

## Topologia da Rede

A topologia definida em `configs/topologia.json` representa os roteadores e suas ligações de acordo com o exemplo abaixo:

![Topologia da Rede](./configs/Topologia%20da%20Rede.png)

Cada roteador se comunica com seus vizinhos através da rede de interconexão (172.50.0.0/24). Os hosts estão alocados em subredes distintas (10.1.0.0/24 a 10.5.0.0/24).

## Execução

Para levantar a rede:

```bash
docker compose up --build
```

Abra outro terminal para executar os testes de conectividade assim que os containers estiverem rodando:

```bash
bash test/testhost.sh     # Testa pings entre os hosts
bash test/testrouter.sh   # Testa pings entre os roteadores
```

## Tecnologias Utilizadas

* Python 3.10 (lógica dos roteadores)
* Docker e Docker Compose
* Protocolo de roteamento inspirado no OSPF
* Algoritmo de Dijkstra
* Bash para scripts de teste

## Autora

Este projeto foi desenvolvido por \[Vivinay da Silva Araújo], discente da Universidade Federal do Piauí.

---

Para mais informações sobre o funcionamento interno dos roteadores, veja o código em `routers/router.py`.

> Projeto entregue como Avaliação 1 de Redes de Computadores II
