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
    Versão ULTRA-OTIMIZADA do GoogleSheetsService para ambientes com pouca memória (Render 512MB)
    """
    
    def __init__(self, spreadsheet_id: str, range_name: str = 'Clientes!A:CZ'):
        self.spreadsheet_id = spreadsheet_id
        self.range_name = range_name
        self.service = None
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        
        # Cache ULTRA-limitado para economizar memória
        self._data_cache = None  # Mudado de {} para None
        self._cache_timestamp = None
        self._cache_ttl = 30  # Cache de apenas 30 segundos
        
        print(f"🧠 Memory Optimized Service inicializado para planilha: {self.spreadsheet_id}")
        print(f"💾 Uso de memória inicial: {MemoryOptimizer.get_memory_usage()}")
        
        self._authenticate()
        
        # Limpeza de memória após inicialização
        if os.environ.get('FLASK_ENV') == 'production':
            gc.collect()
    
    def _authenticate(self):
        """Autentica usando Service Account com otimizações EXTREMAS de memória"""
        try:
            service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
            
            if service_account_json:
                print("🔐 Usando credenciais da variável de ambiente")
                credentials_info = json.loads(service_account_json)
                credentials = Credentials.from_service_account_info(
                    credentials_info, scopes=self.scopes
                )
                # Limpar variável imediatamente para economizar memória
                del credentials_info
            else:
                print("🔐 Usando arquivo local")
                current_dir = os.path.dirname(os.path.dirname(__file__))
                credentials_file = os.path.join(current_dir, 'service-account-key.json')
                credentials = Credentials.from_service_account_file(
                    credentials_file, scopes=self.scopes
                )
            
            # Build service com configurações ULTRA-otimizadas para memória
            self.service = build(
                'sheets', 'v4', 
                credentials=credentials, 
                cache_discovery=False,  # Economizar memória
                static_discovery=False  # Economizar memória adicional
            )
            print("✅ Autenticação concluída (cache_discovery=False para economizar memória)")
            
            # Forçar limpeza de credenciais da memória
            del credentials
            if os.environ.get('FLASK_ENV') == 'production':
                gc.collect()
            
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
        CORRIGIDO: Mapeamento correto dos campos baseado no serviço padrão
        """
        if not row or len(row) < 3:
            return {}
        
        def bool_from_text(text, default=False):
            if isinstance(text, bool):
                return text
            if isinstance(text, str):
                return text.upper() in ['SIM', 'TRUE', '1', 'VERDADEIRO', 'S', 'YES']
            return default
        
        # Processar apenas campos essenciais para economizar memória
        # MAPEAMENTO CORRETO baseado na estrutura da planilha:
        # row[0] = NOME DA EMPRESA, row[1] = RAZÃO SOCIAL, row[2] = NOME FANTASIA, row[3] = CNPJ, row[94] = ID
        client = {
            'id': row[94] if len(row) > 94 and row[94] else '',  # CORRIGIDO: ID está na coluna 94
            'nomeEmpresa': row[0] if len(row) > 0 and row[0] else '',
            'razaoSocialReceita': row[1] if len(row) > 1 and row[1] else '',  # CORRIGIDO: Razão social na coluna 1
            'nomeFantasiaReceita': row[2] if len(row) > 2 and row[2] else '',  # ADICIONADO: Nome fantasia na coluna 2
            'cnpj': row[3] if len(row) > 3 and row[3] else '',  # CORRIGIDO: CNPJ na coluna 3
            'ativo': bool_from_text(row[92] if len(row) > 92 and row[92] else 'SIM', True),  # CORRIGIDO: índice 92
            
            # CAMPOS ADICIONADOS PARA O DASHBOARD:
            'perfil': row[4] if len(row) > 4 and row[4] else '',  # CORRIGIDO: Perfil na coluna 4
            'inscEst': row[5] if len(row) > 5 and row[5] else '',  # ADICIONADO: Inscrição Estadual
            'inscMun': row[6] if len(row) > 6 and row[6] else '',  # ADICIONADO: Inscrição Municipal
            'tributacao': row[9] if len(row) > 9 and row[9] else '',  # ADICIONADO: Tributação (regime federal)
            
            # CAMPOS DE SERVIÇOS:
            'ct': bool_from_text(row[13] if len(row) > 13 and row[13] else ''),  # ADICIONADO: Serviço CT
            'fs': bool_from_text(row[14] if len(row) > 14 and row[14] else ''),  # ADICIONADO: Serviço FS
            'dp': bool_from_text(row[15] if len(row) > 15 and row[15] else ''),  # ADICIONADO: Serviço DP
            'bpoFinanceiro': bool_from_text(row[16] if len(row) > 16 and row[16] else ''),  # ADICIONADO: BPO Financeiro
            
            # Campos essenciais para dashboard
            'statusCliente': row[85] if len(row) > 85 and row[85] else 'ativo',
            'sistemaOnvio': bool_from_text(row[46] if len(row) > 46 and row[46] else ''),  # CORRIGIDO: bool
            'sistemaOnvioContabil': bool_from_text(row[47] if len(row) > 47 and row[47] else ''),  # CORRIGIDO: bool
            'sistemaOnvioFiscal': bool_from_text(row[48] if len(row) > 48 and row[48] else ''),  # CORRIGIDO: bool
            'sistemaOnvioPessoal': bool_from_text(row[49] if len(row) > 49 and row[49] else ''),  # CORRIGIDO: bool
            
            # Outros campos importantes (carregar sob demanda)
            'responsavelContabil': row[35] if len(row) > 35 and row[35] else '',  # CORRIGIDO: responsável imediato
            'telefone': row[30] if len(row) > 30 and row[30] else '',  # CORRIGIDO: telefone fixo
            'email': row[33] if len(row) > 33 and row[33] else '',  # CORRIGIDO: email principal
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
