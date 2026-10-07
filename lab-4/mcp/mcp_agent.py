#!/usr/bin/env python3
import socket
import json
import argparse
import ollama

MODELO_OLLAMA = "qwen2.5:0.5b"  # ou "llama3.2:1b"

class NetworkMCPHost:
    def __init__(self, host: str, port: int):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.reader = self.sock.makefile('r', encoding='utf-8')
        self.msg_id = 0

    def rpc(self, metodo: str, params: dict = None) -> dict:
        self.msg_id += 1
        msg = {
            "jsonrpc": "2.0",
            "id": self.msg_id,
            "method": metodo,
            "params": params or {}
        }
        self.sock.sendall((json.dumps(msg) + "\n").encode('utf-8'))
        linha = self.reader.readline()
        return json.loads(linha)

    def handshake(self):
        return self.rpc("initialize")

    def listar_ferramentas(self):
        res = self.rpc("tools/list")
        return [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["inputSchema"]
                }
            }
            for t in res["result"]["tools"]
        ]

    def executar_ferramenta(self, nome: str, argumentos: dict) -> str:
        res = self.rpc("tools/call", {"name": nome, "arguments": argumentos})
        return res["result"]["content"][0]["text"]

    def fechar(self):
        self.sock.close()


def rodar_agente(server_ip: str, server_port: int, pergunta: str):
    print(f"\n=======================================================")
    print(f"CONECTANDO AO SERVIDOR MCP EM {server_ip}:{server_port}")
    print(f"USUARIO: \"{pergunta}\"")
    print(f"=======================================================\n")

    mcp = NetworkMCPHost(server_ip, server_port)
    mcp.handshake()
    tools = mcp.listar_ferramentas()

    mensagens = [
        {
            "role": "system",
            "content": (
                "Voce e um assistente de monitoramento de infraestrutura remota. "
                "Use as ferramentas MCP para consultar informacoes do servidor e "
                "responda de forma objetiva em portugues com base no retorno."
            )
        },
        {"role": "user", "content": pergunta}
    ]

    # 1. Avaliação do modelo com ferramentas descobertas pela rede
    resposta = ollama.chat(
        model=MODELO_OLLAMA,
        messages=mensagens,
        tools=tools,
        options={"num_ctx": 1024}
    )

    chamadas = resposta.get("message", {}).get("tool_calls", [])

    if chamadas:
        mensagens.append(resposta["message"])
        
        for call in chamadas:
            funcao = call["function"]["name"]
            argumentos = call["function"]["arguments"]
            print(f"[IA Decidiu Chamar MCP Remoto] -> {funcao}({argumentos})")

            # 2. Executa a chamada pela rede
            resultado = mcp.executar_ferramenta(funcao, argumentos)
            print(f"[Retorno Recebido da Rede] -> {resultado}")

            mensagens.append({
                "role": "tool",
                "content": f"Resultado de {funcao}: {resultado}"
            })

        # 3. Síntese final com o retorno
        sintese = ollama.chat(
            model=MODELO_OLLAMA,
            messages=mensagens,
            options={"num_ctx": 1024}
        )
        print(f"\n\033[92mASSISTENTE:\033[0m\n{sintese['message']['content']}")
    else:
        print(f"\n\033[92mASSISTENTE:\033[0m\n{resposta['message']['content']}")

    mcp.fechar()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Cliente Agente MCP de Rede")
    parser.add_argument("--server", "-s", default="127.0.0.1", help="IP da maquina que roda o mcp_network_server.py")
    parser.add_argument("--port", "-p", type=int, default=8999, help="Porta TCP do servidor MCP")
    parser.add_argument("--query", "-q", default="Quais sao as configuracoes de hardware e SO desse servidor remoto?", help="Pergunta ao agente")
    args = parser.parse_args()

    rodar_agente(args.server, args.port, args.query)
