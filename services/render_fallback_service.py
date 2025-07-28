import os
import json
import gc
from typing import Dict, List, Optional
from datetime import datetime

class RenderFallbackService:
    """
    Serviço de fallback para quando a autenticação do Google Sheets falha no Render
    Usa armazenamento local temporário e fornece mensagens amigáveis ao usuário
    """
    
    def __init__(self):
        self.is_fallback = True
        self.data_file = 'data/clients_fallback.json'
        self.status_message = "🔧 Sistema em modo de manutenção - usando dados locais"
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        # Dados de exemplo para demonstração
        self.sample_data = self._get_sample_data()
        print("⚠️ Render Fallback Service ativado")
    
    def _get_sample_data(self) -> List[Dict]:
        """Retorna dados de exemplo para demonstração"""
        return [
            {
                'id': '1',
                'nomeEmpresa': 'Empresa Exemplo Ltda',
                'cnpj': '12.345.678/0001-90',
                'razaoSocialReceita': 'EMPRESA EXEMPLO LIMITADA',
                'ativo': True,
                'statusCliente': 'ativo',
                'sistemaOnvio': True,
                'sistemaOnvioContabil': False,
                'sistemaOnvioFiscal': True,
                'sistemaOnvioPessoal': False,
                'responsavelContabil': 'Contador Exemplo',
                'telefone': '(11) 99999-9999',
                'email': 'contato@exemplo.com.br',
                'ct': True,
                'fs': True,
                'dp': False,
                'regimeFederal': 'Simples Nacional',
                'perfil': 'Empresa'
            },
            {
                'id': '2',
                'nomeEmpresa': 'Sistema Indisponível',
                'cnpj': '00.000.000/0001-00',
                'razaoSocialReceita': 'SISTEMA TEMPORARIAMENTE INDISPONIVEL',
                'ativo': True,
                'statusCliente': 'manutenção',
                'sistemaOnvio': False,
                'sistemaOnvioContabil': False,
                'sistemaOnvioFiscal': False,
                'sistemaOnvioPessoal': False,
                'responsavelContabil': 'Suporte Técnico',
                'telefone': 'Entre em contato',
                'email': 'suporte@controlcontabilidade.com',
                'ct': False,
                'fs': False,
                'dp': False,
                'regimeFederal': 'N/A',
                'perfil': 'Sistema'
            }
        ]
    
    def get_clients(self) -> List[Dict]:
        """Retorna clientes com aviso de fallback"""
        print("⚠️ Usando dados de fallback - Google Sheets indisponível")
        
        # Tentar carregar dados salvos localmente
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data:
                        return data
        except Exception as e:
            print(f"⚠️ Erro ao carregar dados locais: {e}")
        
        # Retornar dados de exemplo
        return self.sample_data
    
    def get_client(self, client_id: str) -> Optional[Dict]:
        """Busca cliente específico"""
        clients = self.get_clients()
        for client in clients:
            if client.get('id') == client_id:
                return client
        return None
    
    def save_client(self, client_data: Dict) -> bool:
        """Salva cliente localmente (temporário)"""
        print("⚠️ Salvamento temporário - dados não sincronizados com Google Sheets")
        
        try:
            clients = self.get_clients()
            
            # Atualizar ou adicionar cliente
            client_id = client_data.get('id')
            found = False
            
            for i, client in enumerate(clients):
                if client.get('id') == client_id:
                    clients[i] = client_data
                    found = True
                    break
            
            if not found:
                # Gerar novo ID se necessário
                if not client_id:
                    client_data['id'] = str(len(clients) + 1)
                clients.append(client_data)
            
            # Salvar localmente
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(clients, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar cliente: {e}")
            return False
    
    def delete_client(self, client_id: str) -> bool:
        """Deleta cliente (soft delete local)"""
        try:
            client = self.get_client(client_id)
            if client:
                client['ativo'] = False
                return self.save_client(client)
            return False
        except Exception as e:
            print(f"❌ Erro ao deletar cliente: {e}")
            return False
    
    def get_status_info(self) -> Dict:
        """Retorna informações sobre o status do sistema"""
        return {
            'status': 'fallback',
            'message': self.status_message,
            'timestamp': datetime.now().isoformat(),
            'data_source': 'local_fallback',
            'google_sheets_available': False,
            'total_clients': len(self.get_clients()),
            'instructions': [
                "O sistema está temporariamente usando dados locais",
                "Verifique as configurações do Google Service Account",
                "Confirme se a variável GOOGLE_SERVICE_ACCOUNT_JSON está definida",
                "Dados inseridos não serão sincronizados até a conexão ser restabelecida"
            ]
        }
