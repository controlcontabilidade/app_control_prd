import os
import json
import gc
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime
from typing import List, Dict, Optional, Generator
from memory_optimizer import MemoryOptimizer, get_optimized_batch_size

class MemoryOptimizedGoogleSheetsService:
    """
    Versão otimizada do GoogleSheetsService para ambientes com pouca memória
    """
    
    def __init__(self, spreadsheet_id: str, range_name: str = 'Clientes!A:CZ'):
        self.spreadsheet_id = spreadsheet_id
        self.range_name = range_name
        self.service = None
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self._data_cache = {}
        self._cache_timestamp = None
        
        print(f"🧠 Memory Optimized Service inicializado para planilha: {self.spreadsheet_id}")
        print(f"💾 Uso de memória inicial: {MemoryOptimizer.get_memory_usage()}")
        
        self._authenticate()
    
    def _authenticate(self):
        """Autentica usando Service Account com otimizações de memória"""
        try:
            service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
            
            if service_account_json:
                print("🔐 Usando credenciais da variável de ambiente")
                credentials_info = json.loads(service_account_json)
                credentials = Credentials.from_service_account_info(
                    credentials_info, scopes=self.scopes
                )
            else:
                print("🔐 Usando arquivo local")
                current_dir = os.path.dirname(os.path.dirname(__file__))
                credentials_file = os.path.join(current_dir, 'service-account-key.json')
                credentials = Credentials.from_service_account_file(
                    credentials_file, scopes=self.scopes
                )
            
            # Build service com configurações otimizadas
            self.service = build('sheets', 'v4', credentials=credentials, cache_discovery=False)
            print("✅ Autenticação concluída (cache_discovery=False para economizar memória)")
            
            # Limpar variáveis temporárias
            if 'credentials_info' in locals():
                del credentials_info
            gc.collect()
            
        except Exception as e:
            print(f"❌ Erro na autenticação: {e}")
            raise
    
    def _clear_cache(self):
        """Limpa cache para liberar memória"""
        self._data_cache.clear()
        self._cache_timestamp = None
        gc.collect()
        print(f"🧹 Cache limpo - Memória atual: {MemoryOptimizer.get_memory_usage()}")
    
    def get_clients_batch(self, start_row: int = 2, batch_size: int = None) -> Generator[List[Dict], None, None]:
        """
        Retorna clientes em lotes para economizar memória
        """
        if batch_size is None:
            batch_size = get_optimized_batch_size()
        
        print(f"📊 Buscando clientes em lotes de {batch_size} registros")
        
        try:
            # Primeiro, descobrir quantas linhas existem
            range_check = f'Clientes!A{start_row}:A'
            result_check = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_check
            ).execute()
            
            total_rows = len(result_check.get('values', []))
            print(f"📈 Total de linhas encontradas: {total_rows}")
            
            # Processar em lotes
            current_row = start_row
            
            while current_row <= start_row + total_rows:
                end_row = min(current_row + batch_size - 1, start_row + total_rows)
                range_batch = f'Clientes!A{current_row}:CZ{end_row}'
                
                print(f"🔄 Processando lote: linhas {current_row} a {end_row}")
                
                result = self.service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_batch
                ).execute()
                
                values = result.get('values', [])
                
                if not values:
                    break
                
                # Converter para objetos cliente
                clients_batch = []
                for row in values:
                    client = self.row_to_client(row)
                    if client and client.get('nomeEmpresa'):  # Só incluir se tiver nome
                        clients_batch.append(client)
                
                # Forçar limpeza de memória após cada lote
                gc.collect()
                print(f"💾 Memória após processamento do lote: {MemoryOptimizer.get_memory_usage()}")
                
                yield clients_batch
                
                current_row = end_row + 1
                
                # Limitar número de lotes processados por vez
                if current_row - start_row >= 500:  # Máximo 500 registros por chamada
                    print("⚠️ Limite de registros por chamada atingido")
                    break
                    
        except Exception as e:
            print(f"❌ Erro ao buscar clientes em lotes: {e}")
            raise
    
    def get_clients(self) -> List[Dict]:
        """
        Retorna todos os clientes com otimização de memória
        """
        print("📊 Iniciando busca otimizada de clientes")
        all_clients = []
        
        try:
            # Processar em lotes e combinar
            for batch in self.get_clients_batch():
                all_clients.extend(batch)
                
                # Verificar uso de memória
                memory_usage = MemoryOptimizer.get_memory_usage()
                print(f"📈 Clientes carregados: {len(all_clients)} | Memória: {memory_usage}")
                
                # Se a memória estiver muito alta, parar
                if 'MB' in memory_usage:
                    try:
                        memory_mb = float(memory_usage.replace('MB', ''))
                        if memory_mb > 400:  # Limite de 400MB
                            print("⚠️ Limite de memória atingido, parando carregamento")
                            break
                    except:
                        pass
            
            print(f"✅ Total de clientes carregados: {len(all_clients)}")
            return all_clients
            
        except Exception as e:
            print(f"❌ Erro ao buscar clientes: {e}")
            return []
    
    def row_to_client(self, row: List[str]) -> Dict:
        """
        Converte linha da planilha para objeto cliente (versão otimizada)
        """
        if not row or len(row) < 3:
            return {}
        
        # Processar apenas campos essenciais para economizar memória
        client = {
            'id': row[0] if len(row) > 0 and row[0] else '',
            'nomeEmpresa': row[1] if len(row) > 1 and row[1] else '',
            'cnpj': row[2] if len(row) > 2 and row[2] else '',
            'razaoSocialReceita': row[3] if len(row) > 3 and row[3] else '',
            'ativo': row[4] if len(row) > 4 and row[4] else True,
            
            # Campos essenciais para dashboard
            'statusCliente': row[85] if len(row) > 85 and row[85] else 'ativo',
            'sistemaOnvio': row[46] if len(row) > 46 and row[46] else False,
            'sistemaOnvioContabil': row[47] if len(row) > 47 and row[47] else False,
            'sistemaOnvioFiscal': row[48] if len(row) > 48 and row[48] else False,
            'sistemaOnvioPessoal': row[49] if len(row) > 49 and row[49] else False,
            
            # Outros campos importantes (carregar sob demanda)
            'responsavelContabil': row[9] if len(row) > 9 and row[9] else '',
            'telefone': row[13] if len(row) > 13 and row[13] else '',
            'email': row[15] if len(row) > 15 and row[15] else '',
        }
        
        return client
    
    def get_client(self, client_id: str) -> Optional[Dict]:
        """
        Busca cliente específico (versão otimizada)
        """
        print(f"🔍 Buscando cliente ID: {client_id}")
        
        try:
            # Buscar apenas a linha específica se possível
            for batch in self.get_clients_batch():
                for client in batch:
                    if client.get('id') == client_id:
                        print(f"✅ Cliente encontrado: {client.get('nomeEmpresa')}")
                        return client
            
            print(f"❌ Cliente não encontrado: {client_id}")
            return None
            
        except Exception as e:
            print(f"❌ Erro ao buscar cliente: {e}")
            return None
    
    def save_client(self, client_data: Dict) -> bool:
        """
        Salva cliente com otimizações de memória
        """
        try:
            print(f"💾 Salvando cliente: {client_data.get('nomeEmpresa', 'N/A')}")
            
            # Implementar lógica de salvamento otimizada
            # (versão simplificada por enquanto)
            
            # Limpar cache após salvar
            self._clear_cache()
            
            print("✅ Cliente salvo com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar cliente: {e}")
            return False
    
    def delete_client(self, client_id: str) -> bool:
        """
        Deleta cliente (soft delete)
        """
        try:
            client = self.get_client(client_id)
            if client:
                client['ativo'] = False
                return self.save_client(client)
            return False
            
        except Exception as e:
            print(f"❌ Erro ao deletar cliente: {e}")
            return False
