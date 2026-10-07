#!/usr/bin/env python3
import socket
import threading
import json
import platform
import os

HOST = '0.0.0.0'  # Escuta em todas as interfaces de rede da máquina servidora
PORT = 8999

def obter_info_sistema():
    return {
        "host_servidor": socket.gethostname(),
        "so": platform.system(),
        "release": platform.release(),
        "arquitetura": platform.machine(),
        "processadores": os.cpu_count()
    }

def testar_conectividade(ip: str):
    ret = os.system(f"ping -c 1 -W 2 {ip} > /dev/null 2>&1")
    return {"ip": ip, "alcancavel": (ret == 0)}

MCP_TOOLS = [
    {
        "name": "obter_info_sistema",
        "description": "Retorna informacoes tecnicas de hardware e sistema operacional da maquina servidora remota.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "testar_conectividade",
        "description": "Executa um teste de ping ICMP a partir do servidor remoto para um endereco IP ou hostname.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ip": {"type": "string", "description": "Endereco IP ou dominio para testar"}
            },
            "required": ["ip"]
        }
    }
]

def processar_requisicao(req: dict) -> dict:
    msg_id = req.get("id")
    metodo = req.get("method")
    params = req.get("params", {})

    if metodo == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "Remote-Host-MCP", "version": "1.0"},
                "capabilities": {"tools": {}}
            }
        }

    elif metodo == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": MCP_TOOLS}
        }

    elif metodo == "tools/call":
        nome = params.get("name")
        args = params.get("arguments", {})

        if nome == "obter_info_sistema":
            res = obter_info_sistema()
        elif nome == "testar_conectividade":
            res = testar_conectividade(args.get("ip", "127.0.0.1"))
        else:
            return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "Ferramenta nao encontrada"}}

        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"content": [{"type": "text", "text": json.dumps(res)}]}
        }

    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "Metodo nao suportado"}}

def atender_cliente(conn, addr):
    print(f"[+] Agente remoto conectado: {addr[0]}:{addr[1]}")
    buffer = ""
    try:
        while True:
            chunk = conn.recv(4096).decode('utf-8')
            if not chunk:
                break
            buffer += chunk
            while "\n" in buffer:
                linha, buffer = buffer.split("\n", 1)
                if not linha.strip():
                    continue
                req = json.loads(linha)
                print(f"[{addr[0]}] Requisicao: {req.get('method')}")
                resp = processar_requisicao(req)
                conn.sendall((json.dumps(resp) + "\n").encode('utf-8'))
    except Exception as e:
        print(f"[-] Erro na conexao com {addr}: {e}")
    finally:
        conn.close()
        print(f"[-] Agente desconectado: {addr[0]}:{addr[1]}")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"=== Servidor MCP de Rede ativo na porta {PORT} ===")
    print(f"Aguardando conexoes de agentes remotos...\n")

    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=atender_cliente, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\nEncerrando servidor...")
    finally:
        server.close()

if __name__ == '__main__':
    main()
