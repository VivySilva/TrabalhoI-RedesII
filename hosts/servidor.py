import socket


def start_udp_server(port=5001):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', port))
    print(f"[SERVER] Escutando UDP na porta {port}...")

    while True:
        data, addr = s.recvfrom(1024)
        print(f"[SERVER] Recebido de {addr}: {data.decode()}")
        s.sendto("pong".encode(), addr)


if __name__ == "__main__":
    start_udp_server()
