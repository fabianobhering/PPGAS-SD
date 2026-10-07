#!/usr/bin/env python3
import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8082/api/tarefas"

def requisicao(metodo: str, url: str, payload: dict = None):
    dados = json.dumps(payload).encode('utf-8') if payload else None
    headers = {'Content-Type': 'application/json'} if payload else {}
    
    req = urllib.request.Request(url, data=dados, headers=headers, method=metodo)
    try:
        with urllib.request.urlopen(req) as resp:
            corpo = resp.read().decode('utf-8')
            return resp.status, json.loads(corpo) if corpo else {}
    except urllib.error.HTTPError as e:
        corpo = e.read().decode('utf-8')
        return e.code, json.loads(corpo) if corpo else {}

def executar_testes():
    print("--- 1. GET /api/tarefas (Listar todas) ---")
    status, dados = requisicao("GET", BASE_URL)
    print(f"Status: {status} | Itens: {len(dados)}\n")

    print("--- 2. POST /api/tarefas (Criar nova tarefa) ---")
    status, nova = requisicao("POST", BASE_URL, {"titulo": "Simular Particionamento de Rede", "concluida": False})
    print(f"Status: {status} | Criado: {nova}\n")
    nova_id = nova["id"]

    print(f"--- 3. PUT /api/tarefas/{nova_id} (Atualizar status da tarefa) ---")
    status, alterada = requisicao("PUT", f"{BASE_URL}/{nova_id}", {"concluida": True})
    print(f"Status: {status} | Alterada: {alterada}\n")

    print(f"--- 4. DELETE /api/tarefas/{nova_id} (Remover tarefa) ---")
    status, remocao = requisicao("DELETE", f"{BASE_URL}/{nova_id}")
    print(f"Status: {status} | Resultado: {remocao}\n")

    print(f"--- 5. GET /api/tarefas/{nova_id} (Verificar se realmente foi removida - Esperado 404) ---")
    status, checagem = requisicao("GET", f"{BASE_URL}/{nova_id}")
    print(f"Status: {status} | Mensagem: {checagem}\n")

if __name__ == '__main__':
    executar_testes()
