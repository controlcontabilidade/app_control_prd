import os
import json
import random
import traceback
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime
from typing import List, Dict, Optional

class GoogleSheetsServiceAccountService:
    """
    Serviço para Google Sheets usando Service Account
    Mais simples que OAuth2 - ideal para aplicações server-side
    """
    
    def __init__(self, spreadsheet_id: str, range_name: str = 'Clientes!A:CZ'):
        self.spreadsheet_id = spreadsheet_id
        self.range_name = range_name
        self.service = None
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        
        print(f"🔧 Service Account Service inicializado para planilha: {self.spreadsheet_id}")
        self._authenticate()
        
        # Garantir que os cabeçalhos estejam na ordem correta
        self.ensure_correct_headers()
    
    def _authenticate(self):
        """Autentica usando Service Account (local ou variável de ambiente)"""
        try:
            # Tenta primeiro variável de ambiente (produção)
            service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
            
            if service_account_json:
                print("🔐 Usando credenciais da variável de ambiente (produção)")
                print(f"🔍 Tamanho da variável: {len(service_account_json)} caracteres")
                print(f"🔍 Primeiros 50 caracteres: {service_account_json[:50]}...")
                
                try:
                    credentials_info = json.loads(service_account_json)
                    print(f"✅ JSON parseado com sucesso!")
                    print(f"🔍 Chaves do JSON: {list(credentials_info.keys())}")
                    print(f"🔍 Project ID: {credentials_info.get('project_id', 'N/A')}")
                    print(f"🔍 Client Email: {credentials_info.get('client_email', 'N/A')}")
                    
                    credentials = Credentials.from_service_account_info(
                        credentials_info, scopes=self.scopes
                    )
                    print("✅ Credenciais Service Account criadas da variável de ambiente!")
                    
                except json.JSONDecodeError as json_error:
                    print(f"❌ Erro ao fazer parse do JSON da variável de ambiente: {json_error}")
                    print(f"❌ Conteúdo da variável (primeiros 200 chars): {service_account_json[:200]}")
                    raise
                    
            else:
                # Fallback para arquivo local (desenvolvimento)
                print("🔐 Variável de ambiente não encontrada, tentando arquivo local...")
                current_dir = os.path.dirname(os.path.dirname(__file__))
                credentials_file = os.path.join(current_dir, 'service-account-key.json')
                print(f"📁 Procurando credenciais em: {credentials_file}")
                
                if not os.path.exists(credentials_file):
                    raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {credentials_file}")
                    
                print("✅ Arquivo de credenciais encontrado!")
                credentials = Credentials.from_service_account_file(
                    credentials_file, scopes=self.scopes
                )
                print("✅ Credenciais Service Account criadas do arquivo local!")
            
            print("🔐 Autenticando com Service Account...")
            print(f"🔍 Scopes solicitados: {self.scopes}")
            
            self.service = build('sheets', 'v4', credentials=credentials)
            print("✅ Autenticação Service Account concluída!")
            
            # Testar a conexão fazendo uma requisição simples
            print("🔍 Testando conexão com Google Sheets...")
            try:
                # Tentar obter metadados da planilha
                spreadsheet = self.service.spreadsheets().get(
                    spreadsheetId=self.spreadsheet_id
                ).execute()
                
                sheet_title = spreadsheet.get('properties', {}).get('title', 'N/A')
                sheet_count = len(spreadsheet.get('sheets', []))
                print(f"✅ Conexão testada com sucesso!")
                print(f"📊 Planilha: '{sheet_title}' com {sheet_count} aba(s)")
                
            except Exception as test_error:
                print(f"❌ Erro ao testar conexão: {test_error}")
                print(f"❌ Spreadsheet ID usado: {self.spreadsheet_id}")
                raise
            
        except Exception as e:
            print(f"❌ Erro na autenticação Service Account: {e}")
            print(f"❌ Tipo do erro: {type(e).__name__}")
            import traceback
            print(f"❌ Traceback completo: {traceback.format_exc()}")
            raise
    
    def save_client(self, client: Dict) -> bool:
        """Salva ou atualiza cliente no Google Sheets - CORRIGIDO PARA EVITAR DUPLICAÇÃO"""
        try:
            print(f"🔍 [SERVICE] ===== PROCESSANDO CLIENTE =====")
            print(f"🔍 [SERVICE] Cliente: '{client.get('nomeEmpresa')}'")
            print(f"🔍 [SERVICE] ID do cliente: '{client.get('id')}'")
            print(f"🔍 [SERVICE] Dados recebidos: {list(client.keys())}")
            
            client_id = client.get('id')
            
            # VALIDAÇÃO RIGOROSA: Verificar se o ID é válido
            if client_id and str(client_id).strip() and str(client_id) != 'None':
                print("🔍 [SERVICE] ===== OPERAÇÃO: ATUALIZAÇÃO =====")
                print(f"🔍 [SERVICE] Verificando se cliente ID '{client_id}' existe...")
                
                # Buscar linha do cliente
                row_index = self.find_client_row(client_id)
                
                if row_index > 0:
                    print(f"✅ [SERVICE] Cliente existe na linha {row_index} - ATUALIZANDO")
                    return self.update_client(client)
                else:
                    print(f"⚠️ [SERVICE] Cliente ID '{client_id}' NÃO encontrado!")
                    print(f"⚠️ [SERVICE] Isso pode indicar:")
                    print(f"   - ID inválido ou corrompido")
                    print(f"   - Cliente foi deletado")
                    print(f"   - Problemas na planilha")
                    print(f"❌ [SERVICE] ABORTANDO operação para evitar duplicação")
                    return False
            else:
                print("🔍 [SERVICE] ===== OPERAÇÃO: NOVO CLIENTE =====")
                # Gerar ID único baseado em timestamp + random
                import random
                timestamp = int(datetime.now().timestamp())
                random_suffix = random.randint(100, 999)
                client['id'] = f"{timestamp}{random_suffix}"
                client['criadoEm'] = datetime.now().isoformat()
                print(f"🔍 [SERVICE] ID gerado: {client['id']}")
                return self.add_new_client(client)
                
        except Exception as e:
            print(f"❌ [SERVICE] Erro ao processar cliente: {e}")
            import traceback
            print(f"❌ [SERVICE] Traceback: {traceback.format_exc()}")
            return False
    
    def add_new_client(self, client: Dict) -> bool:
        """Adiciona novo cliente na planilha"""
        try:
            print(f"➕ Adicionando novo cliente '{client.get('nomeEmpresa')}'...")
            
            row_data = self.client_to_row(client)
            body = {'values': [row_data]}
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range='Clientes!A:CZ',
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            print(f"✅ Novo cliente adicionado! Linhas: {result.get('updates', {}).get('updatedRows', 0)}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao adicionar cliente: {e}")
            return False
    
    def update_client(self, client: Dict) -> bool:
        """Atualiza cliente existente na planilha - CORRIGIDO PARA EVITAR DUPLICAÇÃO"""
        try:
            print(f"✏️ [SERVICE] ===== ATUALIZANDO CLIENTE =====")
            print(f"✏️ [SERVICE] Cliente ID: {client.get('id')}")
            print(f"✏️ [SERVICE] Nome: {client.get('nomeEmpresa')}")
            
            # Validação rigorosa
            client_id = client.get('id')
            if not client_id or str(client_id).strip() == '' or str(client_id) == 'None':
                print("❌ [SERVICE] ID do cliente é inválido para atualização")
                return False
                
            if not client.get('nomeEmpresa'):
                print("❌ [SERVICE] Nome da empresa é obrigatório")
                return False
            
            # Buscar a linha do cliente (DEVE existir)
            print("🔍 [SERVICE] Localizando cliente na planilha...")
            row_index = self.find_client_row(client_id)
            print(f"🔍 [SERVICE] Resultado da busca: {row_index}")
            
            if row_index <= 0:
                print(f"❌ [SERVICE] ERRO CRÍTICO: Cliente ID '{client_id}' não encontrado!")
                print("❌ [SERVICE] ABORTAR atualização para evitar duplicação")
                return False
            
            # Manter dados originais importantes
            if not client.get('criadoEm'):
                print("🔍 [SERVICE] Recuperando criadoEm original...")
                try:
                    existing_client = self.get_client(client_id)
                    if existing_client:
                        client['criadoEm'] = existing_client.get('criadoEm', datetime.now().isoformat())
                        print(f"✅ [SERVICE] CriadoEm recuperado: {client['criadoEm']}")
                    else:
                        client['criadoEm'] = datetime.now().isoformat()
                        print(f"⚠️ [SERVICE] CriadoEm não encontrado, usando atual")
                except Exception as e:
                    print(f"⚠️ [SERVICE] Erro ao recuperar criadoEm: {e}")
                    client['criadoEm'] = datetime.now().isoformat()
            
            # Garantir que está sendo uma atualização
            client['ultimaAtualizacao'] = datetime.now().isoformat()
            
            # Preparar dados para atualização
            print("🔧 [SERVICE] Preparando dados para atualização...")
            try:
                row_data = self.client_to_row(client)
                print(f"✅ [SERVICE] Linha preparada: {len(row_data)} colunas")
                
                if len(row_data) < 93:
                    print(f"⚠️ [SERVICE] Linha tem menos colunas que esperado: {len(row_data)}")
                    
            except Exception as e:
                print(f"❌ [SERVICE] Erro ao preparar dados: {e}")
                return False
            
            # CORREÇÃO: Verificar se a linha atual na planilha precisa ser expandida
            print("🔧 [SERVICE] Verificando se linha atual precisa ser expandida...")
            try:
                # Buscar linha atual da planilha
                current_range = f'Clientes!A{row_index}:CZ{row_index}'
                current_result = self.service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id,
                    range=current_range
                ).execute()
                
                current_row = current_result.get('values', [[]])[0] if current_result.get('values') else []
                print(f"🔍 [SERVICE] Linha atual na planilha tem {len(current_row)} colunas")
                
                if len(current_row) < 93:
                    print(f"🔧 [SERVICE] Expandindo linha de {len(current_row)} para 93 colunas...")
                    # Expandir a linha atual primeiro
                    expanded_row = current_row[:]
                    
                    # Se já tem o ID mas em posição errada, preservar
                    existing_id = client_id
                    if len(current_row) > 89 and current_row[89]:  # Se tinha ID na posição antiga
                        existing_id = current_row[89]
                    
                    # Expandir até 93 colunas
                    while len(expanded_row) < 93:
                        expanded_row.append('')
                    
                    # Colocar o ID na posição correta (índice 92)
                    expanded_row[92] = existing_id
                    
                    print(f"✅ [SERVICE] Linha expandida para {len(expanded_row)} colunas com ID '{existing_id}' no índice 92")
                    
                    # Atualizar a planilha com a linha expandida primeiro
                    expand_body = {'values': [expanded_row]}
                    self.service.spreadsheets().values().update(
                        spreadsheetId=self.spreadsheet_id,
                        range=current_range,
                        valueInputOption='USER_ENTERED',
                        body=expand_body
                    ).execute()
                    
                    print("✅ [SERVICE] Linha expandida na planilha com sucesso!")
                    
            except Exception as expand_error:
                print(f"⚠️ [SERVICE] Erro ao expandir linha: {expand_error}")
                # Continuar mesmo com erro de expansão
            
            # Executar atualização
            range_name = f'Clientes!A{row_index}:CZ{row_index}'
            print(f"🔧 [SERVICE] Atualizando range: {range_name}")
            
            body = {'values': [row_data]}
            
            try:
                result = self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption='USER_ENTERED',
                    body=body
                ).execute()
                
                updated_cells = result.get('updatedCells', 0)
                print(f"✅ [SERVICE] Cliente atualizado com sucesso!")
                print(f"✅ [SERVICE] Linha: {row_index}, Células: {updated_cells}")
                return True
                
            except Exception as api_error:
                print(f"❌ [SERVICE] Erro na API durante atualização: {api_error}")
                return False
            
        except Exception as e:
            print(f"❌ [SERVICE] Erro geral ao atualizar cliente: {e}")
            import traceback
            print(f"❌ [SERVICE] Traceback: {traceback.format_exc()}")
            return False
    
    def find_client_row(self, client_id: str) -> int:
        """Encontra a linha do cliente na planilha - MÉTODO OTIMIZADO COM DEBUG PRODUÇÃO"""
        try:
            print(f"🔍 [SERVICE] ===== BUSCANDO CLIENTE (PRODUÇÃO) =====")
            print(f"🔍 [SERVICE] ID do cliente recebido: '{client_id}' (tipo: {type(client_id)})")
            print(f"🔍 [SERVICE] Spreadsheet ID: {self.spreadsheet_id}")
            print(f"🔍 [SERVICE] Range: {self.range_name}")
            
            if not client_id or str(client_id).strip() == '' or str(client_id) == 'None':
                print("⚠️ [SERVICE] ID do cliente está vazio ou None!")
                return -1
            
            # Normalizar o ID para busca
            search_id = str(client_id).strip()
            print(f"🔍 [SERVICE] ID normalizado para busca: '{search_id}'")
            
            # Verificar se o serviço está autenticado
            if not self.service:
                print("❌ [SERVICE] Serviço Google Sheets não está autenticado!")
                return -1
            
            # Buscar dados da planilha
            print("🔍 [SERVICE] Fazendo requisição para Google Sheets...")
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Clientes!A:CZ'
            ).execute()
            
            values = result.get('values', [])
            print(f"🔍 [SERVICE] Resposta da API recebida: {len(values)} linhas")
            
            if not values:
                print("⚠️ [SERVICE] Planilha vazia ou sem dados")
                return -1
            
            # Primeira linha são os cabeçalhos
            headers = values[0] if values else []
            print(f"🔍 [SERVICE] Planilha tem {len(values)} linhas no total")
            print(f"🔍 [SERVICE] Cabeçalhos encontrados: {len(headers)} colunas")
            
            # Debug dos primeiros cabeçalhos
            if len(headers) >= 5:
                print(f"🔍 [SERVICE] Primeiros 5 cabeçalhos: {headers[:5]}")
            if len(headers) >= 90:
                print(f"🔍 [SERVICE] Cabeçalho da coluna 90 (ID): '{headers[89]}'")
            
            # Encontrar índice da coluna ID
            id_column_index = -1
            for i, header in enumerate(headers):
                if str(header).strip().upper() == 'ID':
                    id_column_index = i
                    print(f"🔍 [SERVICE] Coluna ID encontrada no índice {i} (header: '{header}')")
                    break
            
            if id_column_index == -1:
                print("❌ [SERVICE] Coluna ID não encontrada nos cabeçalhos!")
                print(f"❌ [SERVICE] Cabeçalhos disponíveis: {[h for h in headers if h]}")
                return -1
            
            # Analisar primeiras linhas para debug
            print(f"🔍 [SERVICE] ===== ANALISANDO PRIMEIRAS {min(5, len(values)-1)} LINHAS =====")
            for row_idx in range(1, min(6, len(values))):  # Começar da linha 2 (índice 1)
                row = values[row_idx]
                print(f"🔍 [SERVICE] Linha {row_idx + 1}: {len(row)} colunas")
                if id_column_index < len(row):
                    row_id = str(row[id_column_index]).strip()
                    print(f"🔍 [SERVICE] Linha {row_idx + 1} - ID na posição {id_column_index}: '{row_id}'")
                else:
                    print(f"🔍 [SERVICE] Linha {row_idx + 1} - Coluna ID não existe (linha tem {len(row)} colunas)")
            
            # Buscar o ID específico
            print(f"🔍 [SERVICE] ===== BUSCANDO ID '{search_id}' =====")
            found_ids = []  # Para debug - coletar todos os IDs encontrados
            
            for row_idx in range(1, len(values)):  # Pular cabeçalho
                row = values[row_idx]
                if id_column_index < len(row):
                    row_id = str(row[id_column_index]).strip()
                    actual_row_number = row_idx + 1  # +1 porque é 1-indexed
                    
                    # Coletar para debug
                    if row_id:  # Só adicionar IDs não vazios
                        found_ids.append(row_id)
                    
                    print(f"🔍 [SERVICE] Linha {actual_row_number}: ID '{row_id}' vs busca '{search_id}' - Match: {row_id == search_id}")
                    if row_id == search_id:
                        print(f"✅ [SERVICE] ===== CLIENTE ENCONTRADO NA LINHA {actual_row_number} =====")
                        return actual_row_number
            
            print(f"❌ [SERVICE] Cliente '{search_id}' não encontrado")
            print(f"🔍 [SERVICE] Total de IDs encontrados na planilha: {len(found_ids)}")
            print(f"🔍 [SERVICE] Primeiros 10 IDs encontrados: {found_ids[:10]}")
            
            return -1
            
        except Exception as e:
            print(f"❌ [SERVICE] Erro ao buscar cliente: {e}")
            print(f"❌ [SERVICE] Tipo do erro: {type(e).__name__}")
            import traceback
            print(f"❌ [SERVICE] Traceback completo: {traceback.format_exc()}")
            return -1

    def get_client(self, client_id: str) -> Optional[Dict]:
        """Busca cliente específico - COM DEBUG AVANÇADO PARA PRODUÇÃO"""
        try:
            print(f"🔍 [GET_CLIENT] ===== BUSCANDO CLIENTE ESPECÍFICO (PRODUÇÃO) =====")
            print(f"🔍 [GET_CLIENT] ID recebido: '{client_id}' (tipo: {type(client_id)})")
            print(f"🔍 [GET_CLIENT] ID válido: {bool(client_id and str(client_id).strip())}")
            
            if not client_id or str(client_id).strip() == '' or str(client_id) == 'None':
                print("❌ [GET_CLIENT] ID inválido!")
                return None
            
            # Normalizar ID para busca
            search_id = str(client_id).strip()
            print(f"🔍 [GET_CLIENT] ID normalizado: '{search_id}'")
            
            print("🔍 [GET_CLIENT] Chamando find_client_row...")
            row_index = self.find_client_row(search_id)
            print(f"🔍 [GET_CLIENT] Resultado find_client_row: {row_index}")
            
            if row_index <= 0:
                print(f"❌ [GET_CLIENT] Cliente '{search_id}' não encontrado na planilha")
                print("🔍 [GET_CLIENT] Tentando busca em todos os clientes como fallback...")
                
                # FALLBACK: Buscar em todos os clientes
                all_clients = self.get_clients()
                print(f"🔍 [GET_CLIENT] Total de clientes na planilha: {len(all_clients)}")
                
                for client in all_clients:
                    client_existing_id = client.get('id', '')
                    if str(client_existing_id).strip() == search_id:
                        print(f"✅ [GET_CLIENT] Cliente encontrado via fallback!")
                        print(f"✅ [GET_CLIENT] Nome: {client.get('nomeEmpresa')}")
                        return client
                
                print(f"❌ [GET_CLIENT] Cliente '{search_id}' não encontrado nem via fallback")
                return None
                
            # Buscar os dados da linha específica
            range_name = f'Clientes!A{row_index}:CZ{row_index}'
            print(f"🔍 [GET_CLIENT] Buscando dados do range: {range_name}")
            
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            print(f"🔍 [GET_CLIENT] Dados recebidos: {len(values)} linha(s)")
            
            if values and len(values[0]) > 0:
                print(f"🔍 [GET_CLIENT] Primeira linha tem {len(values[0])} colunas")
                
                client = self.row_to_client(values[0])
                client['_row_number'] = row_index
                
                # Debug do cliente convertido
                converted_id = client.get('id', '')
                client_name = client.get('nomeEmpresa', 'N/A')
                
                print(f"✅ [GET_CLIENT] Cliente convertido com sucesso!")
                print(f"✅ [GET_CLIENT] Nome: '{client_name}'")
                print(f"✅ [GET_CLIENT] ID convertido: '{converted_id}'")
                print(f"✅ [GET_CLIENT] Linha: {row_index}")
                print(f"✅ [GET_CLIENT] Total de campos no cliente: {len(client.keys())}")
                
                # Verificar se os IDs coincidem
                if str(converted_id).strip() != search_id:
                    print(f"⚠️ [GET_CLIENT] AVISO: ID convertido '{converted_id}' != ID buscado '{search_id}'")
                    print(f"⚠️ [GET_CLIENT] Forçando ID correto...")
                    client['id'] = search_id
                
                return client
            else:
                print(f"❌ [GET_CLIENT] Dados vazios na linha {row_index}")
                return None
            
        except Exception as e:
            print(f"❌ [GET_CLIENT] Erro ao buscar cliente {client_id}: {e}")
            print(f"❌ [GET_CLIENT] Tipo do erro: {type(e).__name__}")
            import traceback
            print(f"❌ [GET_CLIENT] Traceback completo: {traceback.format_exc()}")
            return None
    
    def get_clients(self) -> List[Dict]:
        """Busca clientes da planilha - COM DEBUG PARA PRODUÇÃO"""
        try:
            print("📊 ===== BUSCANDO CLIENTES (PRODUÇÃO) =====")
            print(f"📊 Spreadsheet ID: {self.spreadsheet_id}")
            print(f"📊 Range: {self.range_name}")
            
            if not self.service:
                print("❌ Serviço Google Sheets não está autenticado!")
                return []
            
            print("📊 Fazendo requisição para Google Sheets...")
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=self.range_name
            ).execute()
            
            values = result.get('values', [])
            print(f"📊 Resposta da API: {len(values)} linhas recebidas")
            
            if not values:
                print("📝 Nenhum cliente encontrado na planilha")
                return []
            
            # Debug dos cabeçalhos
            headers = values[0] if values else []
            print(f"📊 Cabeçalhos: {len(headers)} colunas")
            
            # Encontrar coluna ID para debug
            id_column_index = -1
            for i, header in enumerate(headers):
                if str(header).strip().upper() == 'ID':
                    id_column_index = i
                    break
            
            print(f"📊 Coluna ID encontrada no índice: {id_column_index}")
            
            clients = []
            rows_processed = 0
            rows_with_data = 0
            rows_with_valid_id = 0
            
            for i, row in enumerate(values[1:], 2):  # Skip header, start from row 2
                rows_processed += 1
                
                if len(row) > 0 and row[0]:  # Check if first column has value
                    rows_with_data += 1
                    
                    client = self.row_to_client(row)
                    client['_row_number'] = i  # Store row number for updates/deletes
                    
                    # Debug do ID do cliente
                    client_id = client.get('id', '')
                    if client_id and str(client_id).strip():
                        rows_with_valid_id += 1
                        if len(clients) < 5:  # Debug apenas dos primeiros 5
                            print(f"📊 Cliente {len(clients)+1}: '{client.get('nomeEmpresa')}' - ID: '{client_id}' - Linha: {i}")
                    
                    clients.append(client)
            
            print(f"📊 ===== RESUMO DA BUSCA =====")
            print(f"📊 Linhas processadas: {rows_processed}")
            print(f"📊 Linhas com dados: {rows_with_data}")
            print(f"📊 Linhas com ID válido: {rows_with_valid_id}")
            print(f"📊 Total de clientes carregados: {len(clients)}")
            
            return clients
            
        except Exception as e:
            print(f"❌ Erro ao buscar clientes: {e}")
            print(f"❌ Tipo do erro: {type(e).__name__}")
            import traceback
            print(f"❌ Traceback completo: {traceback.format_exc()}")
            return []
    
    def delete_client(self, client_id: str) -> bool:
        """Remove cliente da planilha (exclusão real)"""
        try:
            print(f"🗑️ Deletando cliente ID: {client_id}")
            
            # Buscar a linha do cliente
            row_index = self.find_client_row(client_id)
            if row_index <= 0:
                print(f"⚠️ Cliente {client_id} não encontrado")
                return False
            
            # Deletar a linha da planilha
            request_body = {
                'requests': [
                    {
                        'deleteDimension': {
                            'range': {
                                'sheetId': 0,  # Primeira aba da planilha
                                'dimension': 'ROWS',
                                'startIndex': row_index - 1,  # 0-based para API
                                'endIndex': row_index
                            }
                        }
                    }
                ]
            }
            
            result = self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=request_body
            ).execute()
            
            print(f"✅ Cliente deletado da linha {row_index}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao deletar cliente: {e}")
            return False

    def get_headers(self) -> List[str]:
        """Retorna lista completa de cabeçalhos organizados por blocos"""
        return [
            # Bloco 1: Informações da Pessoa Física / Jurídica (13 campos obrigatórios)
            'NOME DA EMPRESA',                   # 1. Nome da empresa/fantasia
            'RAZÃO SOCIAL NA RECEITA',           # 2. Nome oficial na Receita Federal
            'NOME FANTASIA NA RECEITA',          # 3. Nome fantasia na Receita Federal
            'CNPJ',                              # 4. CNPJ (14 dígitos)
            'PERFIL',                            # 5. Perfil tributário (A, B, C, etc.)
            'INSCRIÇÃO ESTADUAL',                # 6. IE - Inscrição Estadual
            'INSCRIÇÃO MUNICIPAL',               # 7. IM - Inscrição Municipal
            'ESTADO',                            # 8. UF do Estado
            'CIDADE',                            # 9. Município
            'REGIME FEDERAL',                    # 10. Simples Nacional, Lucro Real, etc.
            'REGIME ESTADUAL',                   # 11. Normal, Simples, etc.
            'SEGMENTO',                          # 12. Indústria, Comércio, Serviços
            'ATIVIDADE',                         # 13. Atividade principal do negócio
            
            # Bloco 2: Serviços Prestados pela Control
            'SERVIÇO CT',                        # 14. Contabilidade (SIM/NÃO)
            'SERVIÇO FS',                        # 15. Fiscal (SIM/NÃO)
            'SERVIÇO DP',                        # 16. Departamento Pessoal (SIM/NÃO)
            'SERVIÇO BPO FINANCEIRO',            # 17. BPO Financeiro (SIM/NÃO)
            'DATA INÍCIO DOS SERVIÇOS',          # 18. Quando começou a prestação
            
            # Códigos dos Sistemas (Bloco 2)
            'CÓDIGO FORTES CT',                  # 19. Código no sistema Fortes Contábil
            'CÓDIGO FORTES FS',                  # 20. Código no sistema Fortes Fiscal
            'CÓDIGO FORTES PS',                  # 21. Código no sistema Fortes Pessoal
            'CÓDIGO DOMÍNIO',                    # 22. Código no sistema Domínio
            'SISTEMA UTILIZADO',                 # 23. Sistema principal em uso
            'MÓDULO SPED TRIER',                 # 24. Módulo/versão do SPED Trier
            
            # Bloco 3: Quadro Societário (campos base + dinâmicos)
            'SÓCIO 1 NOME',                      # 25. Nome completo do sócio 1
            'SÓCIO 1 CPF',                       # 26. CPF do sócio 1
            'SÓCIO 1 DATA NASCIMENTO',           # 27. Data nascimento sócio 1
            'SÓCIO 1 ADMINISTRADOR',             # 28. É administrador? (SIM/NÃO)
            'SÓCIO 1 COTAS',                     # 29. Percentual de cotas
            'SÓCIO 1 RESPONSÁVEL LEGAL',         # 30. Responsável legal? (SIM/NÃO)
            
            # Bloco 4: Contatos
            'TELEFONE FIXO',                     # 31. Telefone comercial
            'TELEFONE CELULAR',                  # 32. Celular principal
            'WHATSAPP',                          # 33. Número do WhatsApp
            'EMAIL PRINCIPAL',                   # 34. Email principal da empresa
            'EMAIL SECUNDÁRIO',                  # 35. Email alternativo
            'RESPONSÁVEL IMEDIATO',              # 36. Contato direto na empresa
            'EMAILS DOS SÓCIOS',                 # 37. Emails dos sócios
            'CONTATO CONTADOR',                  # 38. Nome do contador atual
            'TELEFONE CONTADOR',                 # 39. Telefone do contador
            'EMAIL CONTADOR',                    # 40. Email do contador
            
            # Bloco 5: Sistemas e Acessos
            'SISTEMA PRINCIPAL',                 # 42. ERP/Sistema principal
            'VERSÃO DO SISTEMA',                 # 43. Versão/release
            'CÓDIGO ACESSO SIMPLES NACIONAL',    # 44. Código de acesso SN
            'CPF/CNPJ PARA ACESSO',              # 45. CPF/CNPJ usado nos acessos
            'PORTAL CLIENTE ATIVO',              # 46. Portal ativo? (SIM/NÃO)
            'INTEGRAÇÃO DOMÍNIO',                # 47. Integrado Domínio? (SIM/NÃO)
            'SISTEMA ONVIO',                     # 48. Usa Onvio? (SIM/NÃO)
            'SISTEMA ONVIO CONTÁBIL',           # 49. Sistema Onvio Contábil (SIM/NÃO)
            'SISTEMA ONVIO FISCAL',             # 50. Sistema Onvio Fiscal (SIM/NÃO)
            'SISTEMA ONVIO PESSOAL',            # 51. Sistema Onvio Pessoal (SIM/NÃO)
            
            # Bloco 6: Senhas e Credenciais
            'ACESSO ISS',                        # 49. Login ISS municipal
            'SENHA ISS',                         # 50. Senha ISS municipal
            'ACESSO SEFIN',                      # 51. Login SEFIN estadual
            'SENHA SEFIN',                       # 52. Senha SEFIN estadual
            'ACESSO SEUMA',                      # 53. Login SEUMA ambiental
            'SENHA SEUMA',                       # 54. Senha SEUMA ambiental
            'ACESSO EMPWEB',                     # 55. Login eSocial/EmpWeb
            'SENHA EMPWEB',                      # 56. Senha eSocial/EmpWeb
            'ACESSO FAP/INSS',                   # 57. Login FAP/INSS
            'SENHA FAP/INSS',                    # 58. Senha FAP/INSS
            'ACESSO CRF',                        # 59. Login CRF (farmácias)
            'SENHA CRF',                         # 60. Senha CRF (farmácias)
            'EMAIL GESTOR',                      # 61. Email para gestão
            'SENHA EMAIL GESTOR',                # 62. Senha email gestão
            'ANVISA GESTOR',                     # 63. Login ANVISA gestor
            'ANVISA EMPRESA',                    # 64. Login ANVISA empresa
            'ACESSO IBAMA',                      # 65. Login IBAMA
            'SENHA IBAMA',                       # 66. Senha IBAMA
            'ACESSO SEMACE',                     # 67. Login SEMACE estadual
            'SENHA SEMACE',                      # 68. Senha SEMACE estadual
            
            # Bloco 7: Procurações
            'PROCURAÇÃO RFB',                    # 69. Tem procuração RFB? (SIM/NÃO)
            'DATA PROCURAÇÃO RFB',               # 70. Data da procuração RFB
            'PROCURAÇÃO RECEITA ESTADUAL',       # 71. Tem procuração RE? (SIM/NÃO)
            'DATA PROCURAÇÃO RC',                # 72. Data da procuração RC
            'PROCURAÇÃO CAIXA ECONÔMICA',        # 73. Tem procuração CEF? (SIM/NÃO)
            'DATA PROCURAÇÃO CX',                # 74. Data da procuração CX
            'PROCURAÇÃO PREVIDÊNCIA SOCIAL',     # 75. Tem procuração INSS? (SIM/NÃO)
            'DATA PROCURAÇÃO SW',                # 76. Data da procuração SW
            'PROCURAÇÃO MUNICIPAL',              # 77. Tem procuração municipal? (SIM/NÃO)
            'DATA PROCURAÇÃO MUNICIPAL',         # 78. Data da procuração municipal
            'OUTRAS PROCURAÇÕES',                # 79. Outras procurações
            'OBSERVAÇÕES PROCURAÇÕES',           # 80. Obs sobre procurações
            
            # Bloco 8: Observações e Dados Adicionais
            'OBSERVAÇÕES GERAIS',                # 81. Observações livres
            'TAREFAS VINCULADAS',                # 82. Número de tarefas pendentes
            'DATA INÍCIO SERVIÇOS',              # 83. Data início (duplicate for compatibility)
            'STATUS DO CLIENTE',                 # 84. ATIVO, INATIVO, SUSPENSO
            'ÚLTIMA ATUALIZAÇÃO',                # 85. Timestamp última modificação
            'RESPONSÁVEL ATUALIZAÇÃO',           # 86. Quem fez a última alteração
            'PRIORIDADE',                        # 87. ALTA, NORMAL, BAIXA
            'TAGS/CATEGORIAS',                   # 88. Tags do cliente
            'HISTÓRICO DE ALTERAÇÕES',           # 89. Log de alterações
            
            # Campos internos do sistema
            'DONO/RESPONSÁVEL',                  # 90. Dono/Responsável (compatibilidade)
            'CLIENTE ATIVO',                     # 91. Cliente ativo? (SIM/NÃO)
            'DATA DE CRIAÇÃO',                   # 92. Data de criação do registro
            'ID',                                # 93. ID único do cliente
        ]

    def ensure_correct_headers(self):
        """Garante que os cabeçalhos estejam na ordem correta"""
        try:
            print("🔧 Verificando cabeçalhos da planilha...")
            
            # Busca dados atuais
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Clientes!A1:CZ1'
            ).execute()
            
            current_headers = result.get('values', [[]])[0] if result.get('values') else []
            correct_headers = self.get_headers()
            
            # Se não há cabeçalhos ou estão diferentes, atualiza
            if not current_headers or current_headers != correct_headers:
                print("📝 Atualizando cabeçalhos da planilha...")
                
                body = {
                    'values': [correct_headers]
                }
                
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range='Clientes!A1:CZ1',
                    valueInputOption='RAW',
                    body=body
                ).execute()
                
                print("✅ Cabeçalhos atualizados com sucesso!")
            else:
                print("✅ Cabeçalhos já estão corretos")
                
        except Exception as e:
            print(f"❌ Erro ao verificar/atualizar cabeçalhos: {e}")

    def client_to_row(self, client: Dict) -> List:
        """Converte cliente para linha da planilha - SIGEC organizado por blocos"""
        
        # DEBUG: Log do ID do cliente
        client_id = client.get('id', '')
        print(f"🔍 [SERVICE] ===== CLIENT_TO_ROW =====")
        print(f"🔍 [SERVICE] Cliente: {client.get('nomeEmpresa')}")
        print(f"🔍 [SERVICE] ID do cliente: '{client_id}' (tipo: {type(client_id)})")
        print(f"🔍 [SERVICE] ID será colocado na posição 89 (coluna 90)")
        
        row_data = [
            # Bloco 1: Informações da Pessoa Jurídica (13 campos obrigatórios)
            client.get('nomeEmpresa', ''),                    # 1. NOME DA EMPRESA
            client.get('razaoSocialReceita', ''),             # 2. RAZÃO SOCIAL NA RECEITA
            client.get('nomeFantasiaReceita', ''),            # 3. NOME FANTASIA NA RECEITA
            client.get('cnpj', ''),                           # 4. CNPJ
            client.get('perfil', ''),                         # 5. PERFIL
            client.get('inscEst', ''),                        # 6. INSCRIÇÃO ESTADUAL
            client.get('inscMun', ''),                        # 7. INSCRIÇÃO MUNICIPAL
            client.get('estado', ''),                         # 8. ESTADO
            client.get('cidade', ''),                         # 9. CIDADE
            client.get('regimeFederal', ''),                  # 10. REGIME FEDERAL
            client.get('regimeEstadual', ''),                 # 11. REGIME ESTADUAL
            client.get('segmento', ''),                       # 12. SEGMENTO
            client.get('atividade', ''),                      # 13. ATIVIDADE
            
            # Bloco 2: Serviços Prestados pela Control
            'SIM' if client.get('ct') else 'NÃO',             # 14. SERVIÇO CT
            'SIM' if client.get('fs') else 'NÃO',             # 15. SERVIÇO FS
            'SIM' if client.get('dp') else 'NÃO',             # 16. SERVIÇO DP
            'SIM' if client.get('bpoFinanceiro') else 'NÃO',  # 17. SERVIÇO BPO FINANCEIRO
            '',                                               # 18. (REMOVIDO DUPLICAÇÃO - DATA INÍCIO ESTÁ NO ÍNDICE 85)
            
            # Códigos dos Sistemas (Bloco 2)
            client.get('codFortesCt', ''),                    # 19. CÓDIGO FORTES CT
            client.get('codFortesFs', ''),                    # 20. CÓDIGO FORTES FS
            client.get('codFortesPs', ''),                    # 21. CÓDIGO FORTES PS
            client.get('codDominio', ''),                     # 22. CÓDIGO DOMÍNIO
            client.get('sistemaUtilizado', ''),               # 23. SISTEMA UTILIZADO
            client.get('moduloSpedTrier', ''),                # 24. MÓDULO SPED TRIER
            
            # Bloco 3: Quadro Societário (campos base + dinâmicos)
            client.get('socio1_nome', client.get('socio1', '')),     # 25. SÓCIO 1 NOME
            client.get('socio1_cpf', ''),                            # 26. SÓCIO 1 CPF
            client.get('socio1_nascimento', ''),                     # 27. SÓCIO 1 DATA NASCIMENTO
            'SIM' if client.get('socio1_admin') else 'NÃO',         # 28. SÓCIO 1 ADMINISTRADOR
            client.get('socio1_cotas', ''),                          # 29. SÓCIO 1 COTAS
            'SIM' if client.get('socio1_resp_legal') else 'NÃO',     # 30. SÓCIO 1 RESPONSÁVEL LEGAL
            
            # Bloco 4: Contatos
            client.get('telefoneFixo', ''),                   # 31. TELEFONE FIXO
            client.get('telefoneCelular', ''),                # 32. TELEFONE CELULAR
            client.get('whatsapp', ''),                       # 33. WHATSAPP
            client.get('emailPrincipal', ''),                 # 34. EMAIL PRINCIPAL
            client.get('emailSecundario', ''),                # 35. EMAIL SECUNDÁRIO
            client.get('responsavelImediato', ''),            # 36. RESPONSÁVEL IMEDIATO
            client.get('emailsSocios', ''),                   # 37. EMAILS DOS SÓCIOS
            client.get('contatoContador', ''),                # 38. CONTATO CONTADOR
            client.get('telefoneContador', ''),               # 39. TELEFONE CONTADOR
            client.get('emailContador', ''),                  # 40. EMAIL CONTADOR
            
            # Bloco 5: Sistemas e Acessos
            client.get('sistemaPrincipal', ''),               # 42. SISTEMA PRINCIPAL
            client.get('versaoSistema', ''),                  # 43. VERSÃO DO SISTEMA
            client.get('codAcessoSimples', ''),               # 44. CÓDIGO ACESSO SIMPLES NACIONAL
            client.get('cpfCnpjAcesso', ''),                  # 45. CPF/CNPJ PARA ACESSO
            'SIM' if client.get('portalClienteAtivo') else 'NÃO',    # 46. PORTAL CLIENTE ATIVO
            'SIM' if client.get('integracaoDominio') else 'NÃO',     # 47. INTEGRAÇÃO DOMÍNIO
            'SIM' if client.get('sistemaOnvio') else 'NÃO',          # 47. SISTEMA ONVIO (corrigido índice)
            'SIM' if client.get('sistemaOnvioContabil') else 'NÃO',  # 48. SISTEMA ONVIO CONTÁBIL (corrigido índice)
            'SIM' if client.get('sistemaOnvioFiscal') else 'NÃO',    # 49. SISTEMA ONVIO FISCAL (corrigido índice)
            'SIM' if client.get('sistemaOnvioPessoal') else 'NÃO',   # 50. SISTEMA ONVIO PESSOAL (corrigido índice)
            
            # Bloco 6: Senhas e Credenciais
            client.get('acessoIss', ''),                      # 52. ACESSO ISS
            client.get('senhaIss', ''),                       # 53. SENHA ISS
            client.get('acessoSefin', ''),                    # 54. ACESSO SEFIN
            client.get('senhaSefin', ''),                     # 55. SENHA SEFIN
            client.get('acessoSeuma', ''),                    # 56. ACESSO SEUMA
            client.get('senhaSeuma', ''),                     # 57. SENHA SEUMA
            client.get('acessoEmpWeb', ''),                   # 58. ACESSO EMPWEB
            client.get('senhaEmpWeb', ''),                    # 59. SENHA EMPWEB
            client.get('acessoFapInss', ''),                  # 60. ACESSO FAP/INSS
            client.get('senhaFapInss', ''),                   # 61. SENHA FAP/INSS
            client.get('acessoCrf', ''),                      # 62. ACESSO CRF
            client.get('senhaCrf', ''),                       # 63. SENHA CRF
            client.get('emailGestor', ''),                    # 64. EMAIL GESTOR
            client.get('senhaEmailGestor', ''),               # 65. SENHA EMAIL GESTOR
            client.get('anvisaGestor', ''),                   # 66. ANVISA GESTOR
            client.get('anvisaEmpresa', ''),                  # 67. ANVISA EMPRESA
            client.get('acessoIbama', ''),                    # 68. ACESSO IBAMA
            client.get('senhaIbama', ''),                     # 69. SENHA IBAMA
            client.get('acessoSemace', ''),                   # 70. ACESSO SEMACE
            client.get('senhaSemace', ''),                    # 71. SENHA SEMACE
            
            # Bloco 7: Procurações
            'SIM' if client.get('procRfb') else 'NÃO',        # 72. PROCURAÇÃO RFB
            client.get('procRfbData', ''),                    # 73. DATA PROCURAÇÃO RFB
            'SIM' if client.get('procRc') else 'NÃO',         # 74. PROCURAÇÃO RECEITA ESTADUAL
            client.get('procRcData', ''),                     # 75. DATA PROCURAÇÃO RC
            'SIM' if client.get('procCx') else 'NÃO',         # 76. PROCURAÇÃO CAIXA ECONÔMICA
            client.get('procCxData', ''),                     # 77. DATA PROCURAÇÃO CX
            'SIM' if client.get('procSw') else 'NÃO',         # 78. PROCURAÇÃO PREVIDÊNCIA SOCIAL
            client.get('procSwData', ''),                     # 79. DATA PROCURAÇÃO SW
            'SIM' if client.get('procMunicipal') else 'NÃO',  # 80. PROCURAÇÃO MUNICIPAL
            client.get('procMunicipalData', ''),              # 81. DATA PROCURAÇÃO MUNICIPAL
            client.get('outrasProc', ''),                     # 82. OUTRAS PROCURAÇÕES
            client.get('obsProcuracoes', ''),                 # 83. OBSERVAÇÕES PROCURAÇÕES
            
            # Bloco 8: Observações e Dados Adicionais
            client.get('observacoesGerais', ''),              # 84. OBSERVAÇÕES GERAIS
            client.get('tarefasVinculadas', 0),               # 85. TAREFAS VINCULADAS
            client.get('dataInicioServicos', ''),             # 86. DATA INÍCIO SERVIÇOS
            client.get('statusCliente', 'ATIVO'),             # 87. STATUS DO CLIENTE
            client.get('ultimaAtualizacao', ''),              # 88. ÚLTIMA ATUALIZAÇÃO
            client.get('responsavelAtualizacao', ''),         # 89. RESPONSÁVEL ATUALIZAÇÃO
            client.get('prioridadeCliente', 'NORMAL'),        # 90. PRIORIDADE
            client.get('tagsCliente', ''),                    # 91. TAGS/CATEGORIAS
            client.get('historicoAlteracoes', ''),            # 92. HISTÓRICO DE ALTERAÇÕES
            
            # Campos internos do sistema (temporários - serão reposicionados)
            client.get('donoResp', ''),                       # 93. DONO/RESPONSÁVEL
            'SIM' if client.get('ativo', True) else 'NÃO',    # 94. CLIENTE ATIVO
        ]
        
        # CORREÇÃO: Garantir que a linha tenha pelo menos 95 colunas
        # Preencher com strings vazias até atingir 95 colunas (índices 0-94)
        while len(row_data) < 95:
            row_data.append('')
        
        # Colocar o ID na posição correta (índice 94, que é a coluna 95)
        row_data[94] = client.get('id', '')
        
        # DEBUG: Verificar se o ID foi colocado corretamente
        print(f"🔍 [SERVICE] ID na posição 94: '{row_data[94]}' (deve ser '{client_id}')")
        print(f"✅ [SERVICE] Total de colunas na linha: {len(row_data)}")
        print(f"✅ [SERVICE] Linha preparada corretamente com ID no índice 94")
        
        return row_data
    
    def row_to_client(self, row: List) -> Dict:
        """Converte linha da planilha para dicionário do cliente - SIGEC organizado por blocos"""
        def safe_get(row, index, default=''):
            try:
                return row[index] if index < len(row) and row[index] else default
            except:
                return default
                
        def bool_from_text(text, default=False):
            if isinstance(text, bool):
                return text
            if isinstance(text, str):
                return text.upper() in ['SIM', 'TRUE', '1', 'VERDADEIRO', 'S', 'YES']
            return default
        
        result = {
            # Bloco 1: Informações da Pessoa Jurídica
            'nomeEmpresa': safe_get(row, 0),                    # 1. NOME DA EMPRESA
            'razaoSocialReceita': safe_get(row, 1),             # 2. RAZÃO SOCIAL NA RECEITA
            'nomeFantasiaReceita': safe_get(row, 2),            # 3. NOME FANTASIA NA RECEITA
            'cnpj': safe_get(row, 3),                           # 4. CNPJ
            'perfil': safe_get(row, 4),                         # 5. PERFIL
            'inscEst': safe_get(row, 5),                        # 6. INSCRIÇÃO ESTADUAL
            'inscMun': safe_get(row, 6),                        # 7. INSCRIÇÃO MUNICIPAL
            'estado': safe_get(row, 7),                         # 8. ESTADO
            'cidade': safe_get(row, 8),                         # 9. CIDADE
            'regimeFederal': safe_get(row, 9),                  # 10. REGIME FEDERAL
            'regimeEstadual': safe_get(row, 10),                # 11. REGIME ESTADUAL
            'segmento': safe_get(row, 11),                      # 12. SEGMENTO
            'atividade': safe_get(row, 12),                     # 13. ATIVIDADE
            
            # Compatibilidade com campos legados
            'tributacao': safe_get(row, 9),                     # Alias para regimeFederal
            'cpfCnpj': safe_get(row, 3),                        # Alias para cnpj
            
            # Bloco 2: Serviços Prestados pela Control
            'ct': bool_from_text(safe_get(row, 13)),            # 14. SERVIÇO CT
            'fs': bool_from_text(safe_get(row, 14)),            # 15. SERVIÇO FS
            'dp': bool_from_text(safe_get(row, 15)),            # 16. SERVIÇO DP
            'bpoFinanceiro': bool_from_text(safe_get(row, 16)), # 17. SERVIÇO BPO FINANCEIRO
            # 18. (REMOVIDO DUPLICAÇÃO - DATA INÍCIO ESTÁ NO ÍNDICE 84)
            
            # Códigos dos Sistemas (Bloco 2)
            'codFortesCt': safe_get(row, 18),                   # 19. CÓDIGO FORTES CT
            'codFortesFs': safe_get(row, 19),                   # 20. CÓDIGO FORTES FS
            'codFortesPs': safe_get(row, 20),                   # 21. CÓDIGO FORTES PS
            'codDominio': safe_get(row, 21),                    # 22. CÓDIGO DOMÍNIO
            'sistemaUtilizado': safe_get(row, 22),              # 23. SISTEMA UTILIZADO
            'moduloSpedTrier': safe_get(row, 23),               # 24. MÓDULO SPED TRIER
            
            # Bloco 3: Quadro Societário
            'socio1_nome': safe_get(row, 24),                   # 25. SÓCIO 1 NOME
            'socio1_cpf': safe_get(row, 25),                    # 26. SÓCIO 1 CPF
            'socio1_nascimento': safe_get(row, 26),             # 27. SÓCIO 1 DATA NASCIMENTO
            'socio1_admin': bool_from_text(safe_get(row, 27)),  # 28. SÓCIO 1 ADMINISTRADOR
            'socio1_cotas': safe_get(row, 28),                  # 29. SÓCIO 1 COTAS
            'socio1_resp_legal': bool_from_text(safe_get(row, 29)), # 30. SÓCIO 1 RESPONSÁVEL LEGAL
            
            # Campos legados para compatibilidade
            'socio1': safe_get(row, 24),                        # Alias para socio1_nome
            'mesAnoInicio': safe_get(row, 17),                  # Alias para dataInicioServicos
            
            # Bloco 4: Contatos
            'telefoneFixo': safe_get(row, 30),                  # 31. TELEFONE FIXO
            'telefoneCelular': safe_get(row, 31),               # 32. TELEFONE CELULAR
            'whatsapp': safe_get(row, 32),                      # 33. WHATSAPP
            'emailPrincipal': safe_get(row, 33),                # 34. EMAIL PRINCIPAL
            'emailSecundario': safe_get(row, 34),               # 35. EMAIL SECUNDÁRIO
            'responsavelImediato': safe_get(row, 35),           # 36. RESPONSÁVEL IMEDIATO
            'emailsSocios': safe_get(row, 36),                  # 37. EMAILS DOS SÓCIOS
            'contatoContador': safe_get(row, 37),               # 38. CONTATO CONTADOR
            'telefoneContador': safe_get(row, 38),              # 39. TELEFONE CONTADOR
            'emailContador': safe_get(row, 39),                 # 40. EMAIL CONTADOR
            
            # Campos legados para compatibilidade
            'emailsSocio': safe_get(row, 36),                   # Alias para emailsSocios
            
            # Bloco 5: Sistemas e Acessos
            'sistemaPrincipal': safe_get(row, 40),              # 41. SISTEMA PRINCIPAL
            'versaoSistema': safe_get(row, 42),                 # 43. VERSÃO DO SISTEMA
            'codAcessoSimples': safe_get(row, 43),              # 44. CÓDIGO ACESSO SIMPLES NACIONAL
            'cpfCnpjAcesso': safe_get(row, 44),                 # 45. CPF/CNPJ PARA ACESSO
            'portalClienteAtivo': bool_from_text(safe_get(row, 45)), # 46. PORTAL CLIENTE ATIVO
            'integracaoDominio': bool_from_text(safe_get(row, 46)),  # 47. INTEGRAÇÃO DOMÍNIO
            'sistemaOnvio': bool_from_text(safe_get(row, 46)),  # 47. SISTEMA ONVIO (corrigido índice)
            'sistemaOnvioContabil': bool_from_text(safe_get(row, 47)), # 48. SISTEMA ONVIO CONTÁBIL (corrigido índice)
            'sistemaOnvioFiscal': bool_from_text(safe_get(row, 48)),   # 49. SISTEMA ONVIO FISCAL (corrigido índice)
            'sistemaOnvioPessoal': bool_from_text(safe_get(row, 49)),  # 50. SISTEMA ONVIO PESSOAL (corrigido índice)
            
            # Campos legados para compatibilidade
            'portalCliente': bool_from_text(safe_get(row, 45)), # Alias para portalClienteAtivo
            'integradoDominio': bool_from_text(safe_get(row, 46)), # Alias para integracaoDominio
            'onvio': bool_from_text(safe_get(row, 46)),         # Alias para sistemaOnvio (corrigido índice)
            
            # Bloco 6: Senhas e Credenciais
            'acessoIss': safe_get(row, 51),                     # 52. ACESSO ISS
            'senhaIss': safe_get(row, 52),                      # 53. SENHA ISS
            'acessoSefin': safe_get(row, 53),                   # 54. ACESSO SEFIN
            'senhaSefin': safe_get(row, 54),                    # 55. SENHA SEFIN
            'acessoSeuma': safe_get(row, 55),                   # 56. ACESSO SEUMA
            'senhaSeuma': safe_get(row, 56),                    # 57. SENHA SEUMA
            'acessoEmpWeb': safe_get(row, 57),                  # 58. ACESSO EMPWEB
            'senhaEmpWeb': safe_get(row, 58),                   # 59. SENHA EMPWEB
            'acessoFapInss': safe_get(row, 59),                 # 60. ACESSO FAP/INSS
            'senhaFapInss': safe_get(row, 60),                  # 61. SENHA FAP/INSS
            'acessoCrf': safe_get(row, 61),                     # 62. ACESSO CRF
            'senhaCrf': safe_get(row, 62),                      # 63. SENHA CRF
            'emailGestor': safe_get(row, 63),                   # 64. EMAIL GESTOR
            'senhaEmailGestor': safe_get(row, 64),              # 65. SENHA EMAIL GESTOR
            'anvisaGestor': safe_get(row, 65),                  # 66. ANVISA GESTOR
            'anvisaEmpresa': safe_get(row, 66),                 # 67. ANVISA EMPRESA
            'acessoIbama': safe_get(row, 67),                   # 68. ACESSO IBAMA
            'senhaIbama': safe_get(row, 68),                    # 69. SENHA IBAMA
            'acessoSemace': safe_get(row, 69),                  # 70. ACESSO SEMACE
            'senhaSemace': safe_get(row, 70),                   # 71. SENHA SEMACE
            
            # Bloco 7: Procurações
            'procRfb': bool_from_text(safe_get(row, 71)),       # 72. PROCURAÇÃO RFB
            'procRfbData': safe_get(row, 72),                   # 73. DATA PROCURAÇÃO RFB
            'procRc': bool_from_text(safe_get(row, 73)),        # 74. PROCURAÇÃO RECEITA ESTADUAL
            'procRcData': safe_get(row, 74),                    # 75. DATA PROCURAÇÃO RC
            'procCx': bool_from_text(safe_get(row, 75)),        # 76. PROCURAÇÃO CAIXA ECONÔMICA
            'procCxData': safe_get(row, 76),                    # 77. DATA PROCURAÇÃO CX
            'procSw': bool_from_text(safe_get(row, 77)),        # 78. PROCURAÇÃO PREVIDÊNCIA SOCIAL
            'procSwData': safe_get(row, 78),                    # 79. DATA PROCURAÇÃO SW
            'procMunicipal': bool_from_text(safe_get(row, 79)), # 80. PROCURAÇÃO MUNICIPAL
            'procMunicipalData': safe_get(row, 80),             # 81. DATA PROCURAÇÃO MUNICIPAL
            'outrasProc': safe_get(row, 81),                    # 82. OUTRAS PROCURAÇÕES
            'obsProcuracoes': safe_get(row, 82),                # 83. OBSERVAÇÕES PROCURAÇÕES
            
            # Bloco 8: Observações e Dados Adicionais
            'observacoesGerais': safe_get(row, 83),             # 84. OBSERVAÇÕES GERAIS
            'tarefasVinculadas': int(safe_get(row, 84, 0)) if str(safe_get(row, 84, 0)).isdigit() else 0, # 85. TAREFAS VINCULADAS 
            'dataInicioServicos': safe_get(row, 85),            # 86. DATA INÍCIO SERVIÇOS (corrigido índice)
            'statusCliente': safe_get(row, 85, 'ATIVO'),        # 86. STATUS DO CLIENTE (corrigido índice)
            'ultimaAtualizacao': safe_get(row, 86),             # 87. ÚLTIMA ATUALIZAÇÃO (corrigido índice)
            'responsavelAtualizacao': safe_get(row, 87),        # 88. RESPONSÁVEL ATUALIZAÇÃO (corrigido índice)
            'prioridadeCliente': safe_get(row, 88, 'NORMAL'),   # 89. PRIORIDADE (corrigido índice)
            'tagsCliente': safe_get(row, 89),                   # 90. TAGS/CATEGORIAS (corrigido índice)
            'historicoAlteracoes': safe_get(row, 90),           # 91. HISTÓRICO DE ALTERAÇÕES (corrigido índice)
            
            # Campos internos do sistema
            'id': safe_get(row, 94),                            # 95. ID
            'ativo': bool_from_text(safe_get(row, 92, 'SIM'), True), # 93. CLIENTE ATIVO (corrigido índice)
            'criadoEm': safe_get(row, 95, datetime.now().isoformat()) # 96. DATA DE CRIAÇÃO (corrigido)
        }
        
        # DEBUG e VALIDAÇÃO do ID
        client_id = result.get('id', '')
        nome_empresa = result.get('nomeEmpresa', 'N/A')
        
        # Se o ID estiver vazio, gerar um baseado no nome da empresa e timestamp
        if not client_id or str(client_id).strip() == '':
            print(f"⚠️ [ROW_TO_CLIENT] Cliente '{nome_empresa}' sem ID! Gerando ID temporário...")
            
            # Gerar ID baseado no nome da empresa (primeiros 3 chars + timestamp)
            safe_name = ''.join(c for c in nome_empresa[:3] if c.isalnum()).upper()
            timestamp_id = int(datetime.now().timestamp())
            temp_id = f"{safe_name}{timestamp_id}"
            result['id'] = temp_id
            print(f"⚠️ [ROW_TO_CLIENT] ID temporário gerado: '{temp_id}'")
        else:
            print(f"✅ [ROW_TO_CLIENT] Cliente '{nome_empresa}' com ID válido: '{client_id}'")
        
        return result
    
    def worksheet_exists(self, worksheet_name: str) -> bool:
        """Verifica se uma aba (worksheet) existe na planilha"""
        try:
            # Obter metadados da planilha
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            # Verificar se a aba existe
            for sheet in spreadsheet.get('sheets', []):
                sheet_title = sheet.get('properties', {}).get('title', '')
                if sheet_title == worksheet_name:
                    return True
                    
            return False
            
        except Exception as e:
            print(f"❌ Erro ao verificar existência da aba '{worksheet_name}': {e}")
            return False
    
    def create_worksheet(self, worksheet_name: str, headers: List[str] = None) -> bool:
        """Cria uma nova aba (worksheet) na planilha"""
        try:
            print(f"📝 Criando aba '{worksheet_name}'...")
            
            # Criar a aba
            requests = [{
                'addSheet': {
                    'properties': {
                        'title': worksheet_name
                    }
                }
            }]
            
            body = {'requests': requests}
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()
            
            print(f"✅ Aba '{worksheet_name}' criada com sucesso!")
            
            # Se headers foram fornecidos, adiciona-los
            if headers:
                print(f"📝 Adicionando cabeçalhos à aba '{worksheet_name}'...")
                body = {
                    'values': [headers]
                }
                
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{worksheet_name}!A1",
                    valueInputOption='USER_ENTERED',
                    body=body
                ).execute()
                
                print(f"✅ Cabeçalhos adicionados à aba '{worksheet_name}'!")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar aba '{worksheet_name}': {e}")
            return False
    
    def get_worksheet_data(self, worksheet_name: str, range_suffix: str = "A:Z") -> List[List]:
        """Obtém dados de uma aba específica"""
        try:
            range_name = f"{worksheet_name}!{range_suffix}"
            
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            return result.get('values', [])
            
        except Exception as e:
            print(f"❌ Erro ao obter dados da aba '{worksheet_name}': {e}")
            return []
    
    def append_to_worksheet(self, worksheet_name: str, data: List[List]) -> bool:
        """Adiciona dados ao final de uma aba"""
        try:
            range_name = f"{worksheet_name}!A:Z"
            
            body = {
                'values': data
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            rows_added = result.get('updates', {}).get('updatedRows', 0)
            print(f"✅ {rows_added} linha(s) adicionada(s) à aba '{worksheet_name}'")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao adicionar dados à aba '{worksheet_name}': {e}")
            return False
    
    def get_worksheet(self, worksheet_name: str):
        """Obtém referência para uma aba específica (compatibilidade com gspread)"""
        # Este método é chamado por alguns serviços que esperam compatibilidade com gspread
        # Como estamos usando Google API diretamente, retornamos um objeto simulado
        class WorksheetShim:
            def __init__(self, service, spreadsheet_id, worksheet_name):
                self.service = service
                self.spreadsheet_id = spreadsheet_id
                self.worksheet_name = worksheet_name
            
            def get_all_values(self):
                """Simula gspread.get_all_values()"""
                try:
                    result = self.service.spreadsheets().values().get(
                        spreadsheetId=self.spreadsheet_id,
                        range=f"{self.worksheet_name}!A:Z"
                    ).execute()
                    return result.get('values', [])
                except Exception as e:
                    print(f"❌ Erro ao obter valores da aba '{self.worksheet_name}': {e}")
                    return []
            
            def append_row(self, row_data):
                """Simula gspread.append_row()"""
                try:
                    body = {'values': [row_data]}
                    result = self.service.spreadsheets().values().append(
                        spreadsheetId=self.spreadsheet_id,
                        range=f"{self.worksheet_name}!A:Z",
                        valueInputOption='USER_ENTERED',
                        body=body
                    ).execute()
                    return True
                except Exception as e:
                    print(f"❌ Erro ao adicionar linha à aba '{self.worksheet_name}': {e}")
                    return False
            
            def row_values(self, row_number):
                """Simula gspread.row_values()"""
                try:
                    range_name = f"{self.worksheet_name}!{row_number}:{row_number}"
                    result = self.service.spreadsheets().values().get(
                        spreadsheetId=self.spreadsheet_id,
                        range=range_name
                    ).execute()
                    values = result.get('values', [])
                    return values[0] if values else []
                except Exception as e:
                    print(f"❌ Erro ao obter linha {row_number} da aba '{self.worksheet_name}': {e}")
                    return []
            
            @property
            def row_count(self):
                """Simula gspread.row_count"""
                try:
                    all_values = self.get_all_values()
                    return len(all_values)
                except Exception as e:
                    print(f"❌ Erro ao contar linhas da aba '{self.worksheet_name}': {e}")
                    return 0
            
            def insert_row(self, values, index=1):
                """Simula gspread.insert_row()"""
                try:
                    # Para inserir uma linha no início, precisamos usar batchUpdate
                    requests = [{
                        'insertDimension': {
                            'range': {
                                'sheetId': self._get_sheet_id(),
                                'dimension': 'ROWS',
                                'startIndex': index - 1,
                                'endIndex': index
                            },
                            'inheritFromBefore': False
                        }
                    }]
                    
                    body = {'requests': requests}
                    self.service.spreadsheets().batchUpdate(
                        spreadsheetId=self.spreadsheet_id,
                        body=body
                    ).execute()
                    
                    # Agora adiciona os valores na linha inserida
                    range_name = f"{self.worksheet_name}!A{index}:Z{index}"
                    body = {'values': [values]}
                    
                    self.service.spreadsheets().values().update(
                        spreadsheetId=self.spreadsheet_id,
                        range=range_name,
                        valueInputOption='USER_ENTERED',
                        body=body
                    ).execute()
                    
                    return True
                except Exception as e:
                    print(f"❌ Erro ao inserir linha na aba '{self.worksheet_name}': {e}")
                    return False
            
            def _get_sheet_id(self):
                """Obtém o ID da aba para operações batch"""
                try:
                    spreadsheet = self.service.spreadsheets().get(
                        spreadsheetId=self.spreadsheet_id
                    ).execute()
                    
                    for sheet in spreadsheet.get('sheets', []):
                        if sheet.get('properties', {}).get('title') == self.worksheet_name:
                            return sheet.get('properties', {}).get('sheetId', 0)
                    
                    return 0
                except Exception as e:
                    print(f"❌ Erro ao obter ID da aba '{self.worksheet_name}': {e}")
                    return 0
        
        return WorksheetShim(self.service, self.spreadsheet_id, worksheet_name)
