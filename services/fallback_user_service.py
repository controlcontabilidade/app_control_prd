"""
Serviço de fallback para usuários quando Google Sheets não está disponível
"""
import json
import os
from pathlib import Path

class FallbackUserService:
    def __init__(self):
        self.users_file = Path(__file__).parent.parent / 'data' / 'users_fallback.json'
        self.users_data = self._load_users()
    
    def _load_users(self):
        """Carrega usuários do arquivo JSON local"""
        try:
            if self.users_file.exists():
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Dados padrão se o arquivo não existir
                return {
                    "users": [
                        {
                            "id": "admin-fallback",
                            "nome": "Administrador (Fallback)",
                            "email": "admin@controlcontabilidade.com",
                            "usuario": "admin",
                            "senha_hash": "admin123",
                            "perfil": "admin",
                            "ativo": True,
                            "data_criacao": "2024-01-01",
                            "ultimo_login": None
                        }
                    ]
                }
        except Exception as e:
            print(f"❌ Erro ao carregar usuários fallback: {e}")
            return {"users": []}
    
    def authenticate_user(self, username, password):
        """Autentica usuário com credenciais de fallback"""
        print(f"🔄 FALLBACK: Tentando autenticar {username}")
        
        for user in self.users_data.get('users', []):
            if (user.get('usuario') == username and 
                user.get('ativo', True) and 
                user.get('senha_hash') == password):  # Senha simples para fallback
                
                print(f"✅ FALLBACK: Usuário {username} autenticado")
                return {
                    'id': user['id'],
                    'nome': user['nome'],
                    'email': user['email'],
                    'perfil': user['perfil']
                }
        
        print(f"❌ FALLBACK: Falha na autenticação para {username}")
        return None
    
    def get_user_by_id(self, user_id):
        """Busca usuário por ID"""
        for user in self.users_data.get('users', []):
            if user.get('id') == user_id and user.get('ativo', True):
                return {
                    'id': user['id'],
                    'nome': user['nome'],
                    'email': user['email'],
                    'perfil': user['perfil']
                }
        return None
    
    def list_users(self):
        """Lista todos os usuários ativos"""
        return [
            {
                'id': user['id'],
                'nome': user['nome'],
                'email': user['email'],
                'perfil': user['perfil']
            }
            for user in self.users_data.get('users', [])
            if user.get('ativo', True)
        ]
    
    def create_user(self, nome, email, usuario, senha, perfil):
        """Criar usuário (não implementado no fallback)"""
        return {
            'success': False,
            'message': 'Criação de usuários não disponível no modo fallback'
        }
    
    def update_user(self, user_id, **kwargs):
        """Atualizar usuário (não implementado no fallback)"""
        return {
            'success': False,
            'message': 'Atualização de usuários não disponível no modo fallback'
        }
    
    def delete_user(self, user_id):
        """Deletar usuário (não implementado no fallback)"""
        return {
            'success': False,
            'message': 'Exclusão de usuários não disponível no modo fallback'
        }
