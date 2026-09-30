#!/usr/bin/env python3
import socket
import threading
import json
import time
import random

HOST = '0.0.0.0'  # Escuta em todas as interfaces de rede
PORT = 9999

class DistributedEventManager:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.subscribers = []
        self.lock = threading.Lock()

    def add_subscriber(self, conn, addr):
        with self.lock:
            self.subscribers.append((conn, addr))
        print(f"[+] Novo Assinante Conectado: {addr}")

    def remove_subscriber(self, conn, addr):
        with self.lock:
            self.subscribers = [s for s in self.subscribers if s[0] != conn]
        try:
            conn.close()
        except:
            pass
        print(f"[-] Assinante Desconectado: {addr}")

    def notify(self, event_type: str, data: dict):
        """Dispersão 1:N pela rede (TCP Fan-out)."""
        payload = json.dumps({"evento": event_type, "dados": data}) + "\n"
        payload_bytes = payload.encode('utf-8')

        print(f"\n[Publicador] Disparando evento '{event_type}' para {len(self.subscribers)} nó(s)...")

        with self.lock:
            for conn, addr in list(self.subscribers):
                try:
                    conn.sendall(payload_bytes)
                except (BrokenPipeError, ConnectionResetError):
                    print(f"[!] Falha de entrega para {addr}. Removendo assinante.")
                    self.remove_subscriber(conn, addr)

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(10)
        print(f"=== Servidor Publicador de Eventos ativo em {self.host}:{self.port} ===")

        # Thread para aceitar novos clientes de forma não bloqueante
        def accept_clients():
            while True:
                conn, addr = server.accept()
                self.add_subscriber(conn, addr)

        threading.Thread(target=accept_clients, daemon=True).start()

        # Simulação contínua de eventos disparados pelo servidor
        self._loop_de_eventos()

    def _loop_de_eventos(self):
        sensores = ["Sensor-Norte", "Sensor-Sul", "Caldeira-Central"]
        while True:
            time.sleep(3.0)  # Gera um evento a cada 3 segundos
            temp = round(random.uniform(20.0, 95.0), 2)
            sensor = random.choice(sensores)

            # Notifica os servidores/clientes remotos
            self.notify("TEMPERATURA", {"sensor": sensor, "temperatura": temp})


if __name__ == '__main__':
    gerenciador = DistributedEventManager(HOST, PORT)
    try:
        gerenciador.start_server()
    except KeyboardInterrupt:
        print("\n[Publicador] Encerrado pelo usuário.")
