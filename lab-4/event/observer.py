#!/usr/bin/env python3
import socket
import json
import sys
import argparse

def processar_evento(tipo_observador: str, evento: str, dados: dict):
    """Implementa a reação ao evento de acordo com a função do nó."""
    if tipo_observador == "logger":
        print(f"[AUDITORIA / LOG] Evento recebido: {evento} -> {dados}")

    elif tipo_observador == "alerta":
        temp = dados.get("temperatura", 0.0)
        if temp > 75.0:
            print(f"\033[91m[ALERTA CRÍTICO]\033[0m Superaquecimento no {dados.get('sensor')}: {temp}°C!")
        else:
            print(f"[Status Normal] {dados.get('sensor')}: {temp}°C (Abaixo do limite de 75°C)")

    elif tipo_observador == "dashboard":
        temp = dados.get("temperatura", 0.0)
        sensor = dados.get("sensor", "N/A")
        barra = "█" * int(temp // 5)
        print(f"[DASHBOARD] {sensor:<16} | {barra:<20} {temp:.1f}°C")


def main():
    parser = argparse.ArgumentParser(description="Cliente Observador de Eventos Distribuídos")
    parser.add_argument("--server", "-s", default="127.0.0.1", help="IP do Servidor Publicador")
    parser.add_argument("--port", "-p", type=int, default=9999, help="Porta do Servidor")
    parser.add_argument("--tipo", "-t", choices=["logger", "alerta", "dashboard"], default="logger",
                        help="Papel/Função deste observador")
    args = parser.parse_args()

    print(f"[*] Conectando ao Publicador em {args.server}:{args.port} como papel: [{args.tipo}]...")

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((args.server, args.port))
    except Exception as e:
        print(f"[Erro de Conexão] Não foi possível conectar ao servidor: {e}")
        sys.exit(1)

    print("[*] Conexão estabelecida com sucesso. Aguardando eventos remotos...\n")

    # Buffer de leitura por linhas (quebra por \n)
    buffer = ""
    try:
        while True:
            chunk = client.recv(4096).decode('utf-8')
            if not chunk:
                print("[-] Conexão encerrada pelo Publicador.")
                break

            buffer += chunk
            while "\n" in buffer:
                linha, buffer = buffer.split("\n", 1)
                if linha.strip():
                    mensagem = json.loads(linha)
                    processar_evento(args.tipo, mensagem["evento"], mensagem["dados"])
    except KeyboardInterrupt:
        print("\n[*] Assinante desconectado pelo usuário.")
    finally:
        client.close()

if __name__ == '__main__':
    main()
