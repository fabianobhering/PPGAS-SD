#!/usr/bin/env python3
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

HOST = '0.0.0.0'
PORT = 8082

# Banco de dados em memória (Recurso: Tarefas)
tarefas_db = {
    1: {"id": 1, "titulo": "Configurar Cluster", "concluida": False},
    2: {"id": 2, "titulo": "Implementar Proxy", "concluida": True}
}
contador_id = 2

class RestRequestHandler(BaseHTTPRequestHandler):
    
    def _enviar_resposta(self, status_code: int, dados: dict = None):
        """Padroniza os cabeçalhos REST e a resposta JSON."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        # Princípio Stateless: não mantém conexão persistente
        self.send_header('Connection', 'close')
        
        if dados is not None:
            corpo = json.dumps(dados, ensure_ascii=False).encode('utf-8')
            self.send_header('Content-Length', str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)
        else:
            self.send_header('Content-Length', '0')
            self.end_headers()

    def _extrair_id(self, path: str):
        """Extrai o ID da URI, ex: /api/tarefas/1 -> 1"""
        partes = [p for p in path.strip('/').split('/') if p]
        if len(partes) == 3 and partes[0] == 'api' and partes[1] == 'tarefas':
            try:
                return int(partes[2])
            except ValueError:
                return None
        return None

    # --- GET: Leitura / Consulta de Recursos (Idempotente e Seguro) ---
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # GET /api/tarefas (Coleção)
        if path == '/api/tarefas':
            self._enviar_resposta(200, list(tarefas_db.values()))
            return

        # GET /api/tarefas/{id} (Item individual)
        tarefa_id = self._extrair_id(path)
        if tarefa_id is not None:
            tarefa = tarefas_db.get(tarefa_id)
            if tarefa:
                self._enviar_resposta(200, tarefa)
            else:
                self._enviar_resposta(404, {"erro": "Tarefa não encontrada"})
            return

        self._enviar_resposta(404, {"erro": "Recurso não encontrado"})

    # --- POST: Criação de Recurso (Não-Idempotente) ---
    def do_POST(self):
        global contador_id
        if self.path == '/api/tarefas':
            try:
                content_len = int(self.headers.get('Content-Length', 0))
                payload = json.loads(self.rfile.read(content_len).decode('utf-8'))
                
                if "titulo" not in payload:
                    self._enviar_resposta(400, {"erro": "Campo 'titulo' obrigatório"})
                    return

                contador_id += 1
                nova_tarefa = {
                    "id": contador_id,
                    "titulo": payload["titulo"],
                    "concluida": payload.get("concluida", False)
                }
                tarefas_db[contador_id] = nova_tarefa
                
                # 201 Created com a representação do recurso criado
                self._enviar_resposta(201, nova_tarefa)
            except Exception as e:
                self._enviar_resposta(400, {"erro": f"JSON inválido: {e}"})
            return

        self._enviar_resposta(404, {"erro": "Rota de criação inválida"})

    # --- PUT: Atualização Completa / Substituição ---
    def do_PUT(self):
        tarefa_id = self._extrair_id(self.path)
        if tarefa_id is None:
            self._enviar_resposta(400, {"erro": "ID inválido ou rota incorreta"})
            return

        if tarefa_id not in tarefas_db:
            self._enviar_resposta(404, {"erro": "Tarefa não encontrada para atualização"})
            return

        try:
            content_len = int(self.headers.get('Content-Length', 0))
            payload = json.loads(self.rfile.read(content_len).decode('utf-8'))

            tarefas_db[tarefa_id]["titulo"] = payload.get("titulo", tarefas_db[tarefa_id]["titulo"])
            tarefas_db[tarefa_id]["concluida"] = payload.get("concluida", tarefas_db[tarefa_id]["concluida"])

            self._enviar_resposta(200, tarefas_db[tarefa_id])
        except Exception as e:
            self._enviar_resposta(400, {"erro": f"JSON inválido: {e}"})

    # --- DELETE: Remoção de Recurso ---
    def do_DELETE(self):
        tarefa_id = self._extrair_id(self.path)
        if tarefa_id is None:
            self._enviar_resposta(400, {"erro": "ID inválido"})
            return

        if tarefa_id in tarefas_db:
            del tarefas_db[tarefa_id]
            self._enviar_resposta(200, {"mensagem": f"Tarefa {tarefa_id} removida com sucesso"})
        else:
            self._enviar_resposta(404, {"erro": "Tarefa não encontrada para deleção"})

    def log_message(self, format, *args):
        # Log limpo das requisições recebidas
        print(f"[HTTP REST] {self.client_address[0]} - {format % args}")

if __name__ == '__main__':
    print(f"=== Servidor RESTful ativo em http://{HOST}:{PORT} ===")
    httpd = HTTPServer((HOST, PORT), RestRequestHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando servidor...")
        httpd.server_close()
