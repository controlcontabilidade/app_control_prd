import json
import os
from typing import List, Dict, Optional

class LocalStorageService:
    def __init__(self, file_path: str = 'data/clients.json'):
        self.file_path = file_path
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def get_clients(self) -> List[Dict]:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def get_client(self, client_id: str) -> Optional[Dict]:
        clients = self.get_clients()
        for client in clients:
            if client.get('id') == str(client_id):
                return client
        return None
    
    def save_client(self, client_data: Dict) -> bool:
        try:
            clients = self.get_clients()
            
            if client_data.get('id'):
                # Editar cliente existente
                for i, client in enumerate(clients):
                    if client.get('id') == client_data['id']:
                        clients[i] = client_data
                        break
            else:
                # Novo cliente
                import time
                client_data['id'] = str(int(time.time() * 1000))
                clients.append(client_data)
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(clients, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Erro ao salvar cliente: {e}")
            return False
    
    def delete_client(self, client_id: str) -> bool:
        try:
            clients = self.get_clients()
            clients = [client for client in clients if client.get('id') != str(client_id)]
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(clients, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Erro ao deletar cliente: {e}")
            return False
