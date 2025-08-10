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
    
    def __init__(self, spreadsheet_id: str, range_name: str = 'Clientes!A:CH'):
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
                # Deixe update_client decidir: usa _row_number se disponível, senão busca por ID
                return self.update_client(client)
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
                range='Clientes!A:DD',
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
            row_index = None
            # Preferir _row_number se enviado pelo formulário
            try:
                provided_row = client.get('_row_number')
                if provided_row:
                    row_index = int(str(provided_row))
                    print(f"🔍 [SERVICE] Usando _row_number fornecido: {row_index}")
            except Exception as e:
                print(f"⚠️ [SERVICE] _row_number inválido: {e}")
                row_index = None
            if not row_index or row_index <= 1:
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
                
                if len(row_data) < 82:
                    print(f"⚠️ [SERVICE] Linha tem menos colunas que esperado: {len(row_data)}")
                    
            except Exception as e:
                print(f"❌ [SERVICE] Erro ao preparar dados: {e}")
                return False
            
            # CORREÇÃO: Verificar se a linha atual na planilha precisa ser expandida
            print("🔧 [SERVICE] Verificando se linha atual precisa ser expandida...")
            try:
                # Buscar linha atual da planilha
                current_range = f'Clientes!A{row_index}:CH{row_index}'
                current_result = self.service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id,
                    range=current_range
                ).execute()
                
                current_row = current_result.get('values', [[]])[0] if current_result.get('values') else []
                print(f"🔍 [SERVICE] Linha atual na planilha tem {len(current_row)} colunas")
                
                if len(current_row) < 86:
                    print(f"🔧 [SERVICE] Expandindo linha de {len(current_row)} para 86 colunas...")
                    # Expandir a linha atual primeiro
                    expanded_row = current_row[:]
                    
                    # Se já tem o ID mas em posição errada, preservar
                    existing_id = client_id
                    if len(current_row) > 78 and current_row[78]:  # Se tinha ID na posição antiga
                        existing_id = current_row[78]
                    
                    # Expandir até 86 colunas
                    while len(expanded_row) < 86:
                        expanded_row.append('')
                    
                    # Colocar o ID na posição correta (índice 94)
                    expanded_row[94] = existing_id
                    
                    print(f"✅ [SERVICE] Linha expandida para {len(expanded_row)} colunas com ID '{existing_id}' no índice 94")
                    
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
            range_name = f'Clientes!A{row_index}:DD{row_index}'
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
                range='Clientes!A:DD'
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
            
            # Buscar o ID específico (verificando coluna atual e coluna legada 90/index 89)
            print(f"🔍 [SERVICE] ===== BUSCANDO ID '{search_id}' =====")
            found_ids = []  # Para debug - coletar todos os IDs encontrados
            
            for row_idx in range(1, len(values)):  # Pular cabeçalho
                row = values[row_idx]
                actual_row_number = row_idx + 1  # +1 porque é 1-indexed
                
                # Determinar onde buscar o ID baseado no tamanho da linha
                row_id = ''
                legacy_row_id = ''
                
                if len(row) <= 86:
                    # Para dados legados (86 colunas ou menos), ID está na posição 83
                    if 83 < len(row):
                        row_id = str(row[83]).strip()
                    if 78 < len(row):
                        legacy_row_id = str(row[78]).strip()
                else:
                    # Para dados novos (mais de 86 colunas), ID está na posição calculada
                    if id_column_index < len(row):
                        row_id = str(row[id_column_index]).strip()
                    if 83 < len(row):
                        legacy_row_id = str(row[83]).strip()

                # Coletar para debug
                if row_id:
                    found_ids.append(row_id)
                elif legacy_row_id:
                    found_ids.append(legacy_row_id)

                print(f"🔍 [SERVICE] Linha {actual_row_number}: ID_atual '{row_id}' | ID_legado '{legacy_row_id}' | busca '{search_id}'")
                if row_id == search_id or legacy_row_id == search_id:
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
            range_name = f'Clientes!A{row_index}:CH{row_index}'
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
            
            # Obter o sheetId correto da aba 'Clientes' (ou da aba definida no range)
            try:
                sheet_name = 'Clientes'
                if '!' in (self.range_name or ''):
                    sheet_name = (self.range_name.split('!')[0] or 'Clientes').strip()
                print(f"🔎 Resolvendo sheetId para a aba: '{sheet_name}'")
                spreadsheet = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
                sheet_id = None
                for sheet in spreadsheet.get('sheets', []):
                    props = sheet.get('properties', {})
                    if props.get('title') == sheet_name:
                        sheet_id = props.get('sheetId')
                        break
                if sheet_id is None:
                    print("❌ sheetId não encontrado; abortando deleção")
                    return False
                print(f"✅ sheetId resolvido: {sheet_id}")
            except Exception as sid_err:
                print(f"❌ Erro ao resolver sheetId: {sid_err}")
                return False
            
            # Deletar a linha da planilha
            request_body = {
                'requests': [
                    {
                        'deleteDimension': {
                            'range': {
                                'sheetId': sheet_id,
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

    def delete_client_by_row(self, row_index: int) -> bool:
        """Remove cliente pela linha (útil quando ID está em branco na planilha)"""
        try:
            if row_index <= 1:
                print(f"❌ Índice de linha inválido para deleção: {row_index}")
                return False

            # Resolver sheetId
            sheet_name = 'Clientes'
            if '!' in (self.range_name or ''):
                sheet_name = (self.range_name.split('!')[0] or 'Clientes').strip()
            spreadsheet = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
            sheet_id = None
            for sheet in spreadsheet.get('sheets', []):
                props = sheet.get('properties', {})
                if props.get('title') == sheet_name:
                    sheet_id = props.get('sheetId')
                    break
            if sheet_id is None:
                print("❌ sheetId não encontrado para deleção por linha")
                return False

            request_body = {
                'requests': [
                    {
                        'deleteDimension': {
                            'range': {
                                'sheetId': sheet_id,
                                'dimension': 'ROWS',
                                'startIndex': row_index - 1,
                                'endIndex': row_index
                            }
                        }
                    }
                ]
            }

            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=request_body
            ).execute()
            print(f"✅ Cliente deletado pela linha {row_index}")
            return True
        except Exception as e:
            print(f"❌ Erro ao deletar por linha: {e}")
            return False

    def get_headers(self) -> List[str]:
        """Retorna lista completa de cabeçalhos organizados por blocos - ATUALIZADA após remoções"""
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
            
            # Códigos dos Sistemas (Bloco 2) - CAMPOS MANTIDOS
            'CÓDIGO FORTES CT',                  # 19. Código no sistema Fortes Contábil
            'CÓDIGO FORTES FS',                  # 20. Código no sistema Fortes Fiscal
            'CÓDIGO FORTES PS',                  # 21. Código no sistema Fortes Pessoal
            'CÓDIGO DOMÍNIO',                    # 22. Código no sistema Domínio
            'SISTEMA UTILIZADO',                 # 23. Sistema principal em uso
            # REMOVIDO: 'MÓDULO SPED TRIER' - Campo não utilizado pelo sistema
            
            # Bloco 3: Quadro Societário
            'SÓCIO 1 NOME',                      # 24. Nome completo do sócio 1
            'SÓCIO 1 CPF',                       # 25. CPF do sócio 1
            'SÓCIO 1 DATA NASCIMENTO',           # 26. Data nascimento sócio 1
            'SÓCIO 1 ADMINISTRADOR',             # 27. É administrador? (SIM/NÃO)
            'SÓCIO 1 PARTICIPAÇÃO',              # 28. Percentual de participação
            'SÓCIO 1 RESPONSÁVEL LEGAL',         # 29. Responsável legal? (SIM/NÃO)
            
            # Bloco 4: Contatos
            'TELEFONE FIXO',                     # 30. Telefone comercial
            'TELEFONE CELULAR',                  # 31. Celular principal
            'WHATSAPP',                          # 32. Número do WhatsApp
            'EMAIL PRINCIPAL',                   # 33. Email principal da empresa
            'EMAIL SECUNDÁRIO',                  # 34. Email alternativo
            'RESPONSÁVEL IMEDIATO',              # 35. Contato direto na empresa
            'EMAILS DOS SÓCIOS',                 # 36. Emails dos sócios
            'CONTATO CONTADOR',                  # 37. Nome do contador atual
            'TELEFONE CONTADOR',                 # 38. Telefone do contador
            'EMAIL CONTADOR',                    # 39. Email do contador
            
            # Contatos Detalhados (até 5 contatos)
            'CONTATO_1_NOME',                    # 40. Nome do contato 1
            'CONTATO_1_CARGO',                   # 41. Cargo do contato 1
            'CONTATO_1_TELEFONE',                # 42. Telefone do contato 1
            'CONTATO_1_EMAIL',                   # 43. Email do contato 1
            'CONTATO_2_NOME',                    # 44. Nome do contato 2
            'CONTATO_2_CARGO',                   # 45. Cargo do contato 2
            'CONTATO_2_TELEFONE',                # 46. Telefone do contato 2
            'CONTATO_2_EMAIL',                   # 47. Email do contato 2
            'CONTATO_3_NOME',                    # 48. Nome do contato 3
            'CONTATO_3_CARGO',                   # 49. Cargo do contato 3
            'CONTATO_3_TELEFONE',                # 50. Telefone do contato 3
            'CONTATO_3_EMAIL',                   # 51. Email do contato 3
            'CONTATO_4_NOME',                    # 52. Nome do contato 4
            'CONTATO_4_CARGO',                   # 53. Cargo do contato 4
            'CONTATO_4_TELEFONE',                # 54. Telefone do contato 4
            'CONTATO_4_EMAIL',                   # 55. Email do contato 4
            'CONTATO_5_NOME',                    # 56. Nome do contato 5
            'CONTATO_5_CARGO',                   # 57. Cargo do contato 5
            'CONTATO_5_TELEFONE',                # 58. Telefone do contato 5
            'CONTATO_5_EMAIL',                   # 59. Email do contato 5
            
            # Bloco 5: Senhas e Credenciais (APENAS CAMPOS ESPECIFICADOS)
            'CPF/CNPJ SN',                       # 60. CPF/CNPJ Simples Nacional
            'CÓDIGO ACESSO SN',                  # 61. Código de acesso SN
            'ACESSO EMPWEB',                     # 62. Login eSocial/EmpWeb
            'SENHA EMPWEB',                      # 63. Senha eSocial/EmpWeb
            'ACESSO ISS',                        # 64. Login ISS municipal
            'ACESSO SEFIN',                      # 65. Login SEFIN estadual
            'ACESSO SEUMA',                      # 66. Login SEUMA ambiental
            'ACESSO SEMACE',                     # 67. Login SEMACE estadual
            'ACESSO IBAMA',                      # 68. Login IBAMA
            'ACESSO FAP/INSS',                   # 69. Login FAP/INSS
            'ACESSO CRF',                        # 70. Login CRF (farmácias)
            'SENHA SEMACE',                      # 71. Senha SEMACE estadual
            'ANVISA GESTOR',                     # 72. Login ANVISA gestor
            'ANVISA EMPRESA',                    # 73. Login ANVISA empresa
            
            # Bloco 6: Procurações (CORRIGIDO - alinhado com formulário)
            'PROCURAÇÃO RECEITA',                # 74. Tem procuração Receita? (SIM/NÃO)
            'DATA PROCURAÇÃO RECEITA',           # 75. Data da procuração Receita
            'PROCURAÇÃO DTe',                    # 76. Tem procuração DTe? (SIM/NÃO)
            'DATA PROCURAÇÃO DTe',               # 77. Data da procuração DTe
            'PROCURAÇÃO CAIXA',                  # 78. Tem procuração Caixa? (SIM/NÃO)
            'DATA PROCURAÇÃO CAIXA',             # 79. Data da procuração Caixa
            'PROCURAÇÃO EMP WEB',                # 80. Tem procuração Emp Web? (SIM/NÃO)
            'DATA PROCURAÇÃO EMP WEB',           # 81. Data da procuração Emp Web
            'PROCURAÇÃO DET',                    # 82. Tem procuração DET? (SIM/NÃO)
            'DATA PROCURAÇÃO DET',               # 83. Data da procuração DET
            'OUTRAS PROCURAÇÕES',                # 84. Outras procurações
            'OBSERVAÇÕES PROCURAÇÕES',           # 85. Obs sobre procurações
            
            # Bloco 7: Observações e Dados Adicionais
            'OBSERVAÇÕES GERAIS',                # 86. Observações livres
            'TAREFAS VINCULADAS',                # 87. Número de tarefas pendentes
            'DATA INÍCIO SERVIÇOS',              # 88. Data início (duplicate for compatibility)
            'STATUS DO CLIENTE',                 # 89. ATIVO, INATIVO, SUSPENSO
            'ÚLTIMA ATUALIZAÇÃO',                # 90. Timestamp última modificação
            'RESPONSÁVEL ATUALIZAÇÃO',           # 91. Quem fez a última alteração
            'PRIORIDADE',                        # 92. ALTA, NORMAL, BAIXA
            'TAGS/CATEGORIAS',                   # 93. Tags do cliente
            'HISTÓRICO DE ALTERAÇÕES',           # 94. Log de alterações
            
            # Campos internos do sistema
            'DONO/RESPONSÁVEL',                  # 95. Dono/Responsável
            'CLIENTE ATIVO',                     # 96. Cliente ativo? (SIM/NÃO)
            'DATA DE CRIAÇÃO',                   # 97. Data de criação do registro
            'ID',                                # 98. ID único do cliente
            'DOMÉSTICA',                         # 99. Indica se é doméstica (SIM/NÃO)
            'GERA ARQUIVO DO SPED',              # 100. Gera arquivo do SPED (SIM/NÃO)
        ]

    def ensure_correct_headers(self):
        """Garante que os cabeçalhos estejam na ordem correta"""
        try:
            print("🔧 Verificando cabeçalhos da planilha...")
            
            # Busca dados atuais
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Clientes!A1:DD1'
            ).execute()
            
            current_headers = result.get('values', [[]])[0] if result.get('values') else []
            correct_headers = self.get_headers()
            
            # Verifica se os cabeçalhos estão corretos
            headers_need_update = False
            if len(current_headers) != len(correct_headers):
                print(f"📊 Cabeçalhos têm tamanho diferente: atual={len(current_headers)}, esperado={len(correct_headers)}")
                headers_need_update = True
            else:
                for i, (current, correct) in enumerate(zip(current_headers, correct_headers)):
                    if current != correct:
                        print(f"📊 Diferença no índice {i}: '{current}' != '{correct}'")
                        headers_need_update = True
                        break
            
            if headers_need_update:
                print("🔧 Atualizando cabeçalhos da planilha...")
                # Atualizar cabeçalhos
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range='Clientes!A1:DD1',
                    valueInputOption='RAW',
                    body={'values': [correct_headers]}
                ).execute()
                print("✅ Cabeçalhos atualizados com sucesso!")
                return True
            else:
                print("✅ Cabeçalhos já estão corretos!")
                return True
                
        except Exception as e:
            print(f"❌ Erro ao verificar/atualizar cabeçalhos: {e}")
            return False

    def update_sheet_headers_for_removed_fields(self):
        """Atualiza especificamente os cabeçalhos removendo campos não utilizados"""
        try:
            print("🗑️ Atualizando planilha para remover campos não utilizados...")
            
            # Forçar atualização dos cabeçalhos
            correct_headers = self.get_headers()
            
            print(f"📊 Total de colunas após limpeza: {len(correct_headers)}")
            print("🔧 Campos removidos do Bloco 2:")
            print("   - Sistema Principal")
            print("   - Versão do Sistema") 
            print("   - Código Acesso Simples")
            print("   - CPF/CNPJ para Acesso")
            print("   - Portal Cliente Ativo")
            print("   - Integração Domínio")
            print("   - Sistema Onvio")
            print("   - Onvio Contábil")
            print("   - Onvio Fiscal")
            print("   - Onvio Pessoal")
            print("   - Módulo SPED Trier")
            
            # Atualizar cabeçalhos na planilha
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f'Clientes!A1:{chr(65 + len(correct_headers) - 1)}1',
                valueInputOption='RAW',
                body={'values': [correct_headers]}
            ).execute()
            
            print("✅ Planilha Google Sheets atualizada!")
            print(f"✅ Cabeçalhos reduzidos para {len(correct_headers)} colunas")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar planilha: {e}")
            return False
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Clientes!A1:DD1'
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
                    range='Clientes!A1:DD1',
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
        print("🔍 [SERVICE] ===== CLIENT_TO_ROW =====")
        print(f"🔍 [SERVICE] Cliente: {client.get('nomeEmpresa')}")
        print(f"🔍 [SERVICE] ID do cliente: '{client_id}' (tipo: {type(client_id)})")
        print("🔍 [SERVICE] ID ficará na coluna 'ID' conforme cabeçalho atual")

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
            client.get('dataInicioServicos', ''),             # 18. DATA INÍCIO DOS SERVIÇOS (CORRIGIDO)
            
            # Códigos dos Sistemas (Bloco 2)
            client.get('codFortesCt', ''),                    # 19. CÓDIGO FORTES CT
            client.get('codFortesFs', ''),                    # 20. CÓDIGO FORTES FS
            client.get('codFortesPs', ''),                    # 21. CÓDIGO FORTES PS
            client.get('codDominio', ''),                     # 22. CÓDIGO DOMÍNIO
            client.get('sistemaUtilizado', ''),               # 23. SISTEMA UTILIZADO
            
            # Bloco 3: Quadro Societário (compatibilidade total entre formatos novos e antigos)
            client.get('socio_1_nome', client.get('socio1_nome', client.get('socio1', ''))),     # 24. SÓCIO 1 NOME
            client.get('socio_1_cpf', client.get('socio1_cpf', '')),                            # 25. SÓCIO 1 CPF
            client.get('socio_1_data_nascimento', client.get('socio1_nascimento', '')),         # 26. SÓCIO 1 DATA NASCIMENTO
            'SIM' if client.get('socio_1_administrador', client.get('socio1_admin')) else 'NÃO', # 27. SÓCIO 1 ADMINISTRADOR
            client.get('socio_1_participacao', client.get('socio1_cotas', '')),                  # 28. SÓCIO 1 PARTICIPAÇÃO
            'SIM' if client.get('socio_1_resp_legal', client.get('socio1_resp_legal')) else 'NÃO', # 29. SÓCIO 1 RESPONSÁVEL LEGAL
            
            # Bloco 4: Contatos
            client.get('telefoneFixo', ''),                   # 30. TELEFONE FIXO
            client.get('telefoneCelular', ''),                # 31. TELEFONE CELULAR
            client.get('whatsapp', ''),                       # 32. WHATSAPP
            client.get('emailPrincipal', ''),                 # 33. EMAIL PRINCIPAL
            client.get('emailSecundario', ''),                # 34. EMAIL SECUNDÁRIO
            client.get('responsavelImediato', ''),            # 35. RESPONSÁVEL IMEDIATO
            client.get('emailsSocios', ''),                   # 36. EMAILS DOS SÓCIOS
            client.get('contatoContador', ''),                # 37. CONTATO CONTADOR
            client.get('telefoneContador', ''),               # 38. TELEFONE CONTADOR
            client.get('emailContador', ''),                  # 39. EMAIL CONTADOR
            
            # Contatos Detalhados (até 5 contatos)
            client.get('contato_1_nome', ''),                 # 40. CONTATO_1_NOME
            client.get('contato_1_cargo', ''),                # 41. CONTATO_1_CARGO
            client.get('contato_1_telefone', ''),             # 42. CONTATO_1_TELEFONE
            client.get('contato_1_email', ''),                # 43. CONTATO_1_EMAIL
            client.get('contato_2_nome', ''),                 # 44. CONTATO_2_NOME
            client.get('contato_2_cargo', ''),                # 45. CONTATO_2_CARGO
            client.get('contato_2_telefone', ''),             # 46. CONTATO_2_TELEFONE
            client.get('contato_2_email', ''),                # 47. CONTATO_2_EMAIL
            client.get('contato_3_nome', ''),                 # 48. CONTATO_3_NOME
            client.get('contato_3_cargo', ''),                # 49. CONTATO_3_CARGO
            client.get('contato_3_telefone', ''),             # 50. CONTATO_3_TELEFONE
            client.get('contato_3_email', ''),                # 51. CONTATO_3_EMAIL
            client.get('contato_4_nome', ''),                 # 52. CONTATO_4_NOME
            client.get('contato_4_cargo', ''),                # 53. CONTATO_4_CARGO
            client.get('contato_4_telefone', ''),             # 54. CONTATO_4_TELEFONE
            client.get('contato_4_email', ''),                # 55. CONTATO_4_EMAIL
            client.get('contato_5_nome', ''),                 # 56. CONTATO_5_NOME
            client.get('contato_5_cargo', ''),                # 57. CONTATO_5_CARGO
            client.get('contato_5_telefone', ''),             # 58. CONTATO_5_TELEFONE
            client.get('contato_5_email', ''),                # 59. CONTATO_5_EMAIL
            
            # Bloco 5: Senhas e Credenciais (APENAS CAMPOS ESPECIFICADOS)
            client.get('cpfCnpjSn', ''),                      # 60. CPF/CNPJ SN
            client.get('codigoAcessoSn', ''),                 # 61. CÓDIGO ACESSO SN
            client.get('acessoEmpWeb', ''),                   # 62. ACESSO EMPWEB
            client.get('senhaEmpWeb', ''),                    # 63. SENHA EMPWEB
            client.get('acessoIss', ''),                      # 64. ACESSO ISS
            client.get('acessoSefin', ''),                    # 65. ACESSO SEFIN
            client.get('acessoSeuma', ''),                    # 66. ACESSO SEUMA
            client.get('acessoSemace', ''),                   # 67. ACESSO SEMACE
            client.get('acessoIbama', ''),                    # 68. ACESSO IBAMA
            client.get('acessoFapInss', ''),                  # 69. ACESSO FAP/INSS
            client.get('acessoCrf', ''),                      # 70. ACESSO CRF
            client.get('senhaSemace', ''),                    # 71. SENHA SEMACE
            client.get('anvisaGestor', ''),                   # 72. ANVISA GESTOR
            client.get('anvisaEmpresa', ''),                  # 73. ANVISA EMPRESA
            
            # Bloco 6: Procurações (CORRIGIDO - alinhado com formulário)
            'SIM' if client.get('procReceita') else 'NÃO',   # 74. PROCURAÇÃO RECEITA (RFB)
            client.get('dataProcReceita', ''),                # 75. DATA PROCURAÇÃO RECEITA
            'SIM' if client.get('procDte') else 'NÃO',        # 76. PROCURAÇÃO DTe
            client.get('dataProcDte', ''),                    # 77. DATA PROCURAÇÃO DTe
            'SIM' if client.get('procCaixa') else 'NÃO',      # 78. PROCURAÇÃO CAIXA
            client.get('dataProcCaixa', ''),                  # 79. DATA PROCURAÇÃO CAIXA
            'SIM' if client.get('procEmpWeb') else 'NÃO',     # 80. PROCURAÇÃO EMP WEB
            client.get('dataProcEmpWeb', ''),                 # 81. DATA PROCURAÇÃO EMP WEB
            'SIM' if client.get('procDet') else 'NÃO',        # 82. PROCURAÇÃO DET
            client.get('dataProcDet', ''),                    # 83. DATA PROCURAÇÃO DET
            client.get('outrasProc', ''),                     # 84. OUTRAS PROCURAÇÕES
            client.get('obsProcuracoes', ''),                 # 85. OBSERVAÇÕES PROCURAÇÕES
            
            # Bloco 7: Observações e Dados Adicionais
            client.get('observacoesGerais', ''),              # 86. OBSERVAÇÕES GERAIS
            client.get('tarefasVinculadas', 0),               # 87. TAREFAS VINCULADAS
            client.get('dataInicioServicos', ''),             # 88. DATA INÍCIO SERVIÇOS (DUPLICAÇÃO REMOVIDA - já está no índice 18)
            client.get('statusCliente', 'ATIVO'),             # 89. STATUS DO CLIENTE
            client.get('ultimaAtualizacao', ''),              # 90. ÚLTIMA ATUALIZAÇÃO
            client.get('responsavelAtualizacao', ''),         # 91. RESPONSÁVEL ATUALIZAÇÃO
            client.get('prioridadeCliente', 'NORMAL'),        # 92. PRIORIDADE
            client.get('tagsCliente', ''),                    # 93. TAGS/CATEGORIAS
            client.get('historicoAlteracoes', ''),            # 94. HISTÓRICO DE ALTERAÇÕES
            # placeholders para manter comprimento; campos finais serão preenchidos por nome
            '',  # placeholder
            '',  # placeholder
        ]

        # CORREÇÃO: Garantir que a linha tenha o tamanho dos cabeçalhos
        headers = self.get_headers()
        expected_len = len(headers)
        while len(row_data) < expected_len:
            row_data.append('')

        # Mapear índices de cabeçalho para evitar desalinhamento nos campos finais
        hidx = {name: i for i, name in enumerate(headers)}

        # Preencher campos finais conforme cabeçalho oficial
        # DONO/RESPONSÁVEL (opcional)
        if 'DONO/RESPONSÁVEL' in hidx:
            row_data[hidx['DONO/RESPONSÁVEL']] = client.get('donoResp', '')
        # CLIENTE ATIVO
        if 'CLIENTE ATIVO' in hidx:
            row_data[hidx['CLIENTE ATIVO']] = 'SIM' if client.get('ativo', True) else 'NÃO'
        # DATA DE CRIAÇÃO
        if 'DATA DE CRIAÇÃO' in hidx:
            row_data[hidx['DATA DE CRIAÇÃO']] = client.get('criadoEm', '')
        # ID
        if 'ID' in hidx:
            row_data[hidx['ID']] = client.get('id', '')

    # Novos campos no final (não alteram índices anteriores), respeitando cabeçalhos
        try:
            import re
            doc = client.get('cnpj') or client.get('cpfCnpj') or ''
            digits = re.sub(r'\D', '', str(doc))
        except Exception:
            digits = ''

        domestica_val = (client.get('domestica') or '').strip().upper()
        if len(digits) == 11:
            # CPF completo: aceita valor enviado; default para 'NÃO' se vazio
            domestica_final = domestica_val if domestica_val in ['SIM', 'NÃO'] else 'NÃO'
        else:
            # CNPJ ou incompleto: força 'NÃO'
            domestica_final = 'NÃO'
        if 'DOMÉSTICA' in hidx:
            row_data[hidx['DOMÉSTICA']] = domestica_final

        gera_sped_val = (client.get('geraArquivoSped') or '').strip().upper()
        if 'GERA ARQUIVO DO SPED' in hidx:
            row_data[hidx['GERA ARQUIVO DO SPED']] = gera_sped_val if gera_sped_val in ['SIM', 'NÃO'] else ''

        # DEBUG: Verificar se o ID foi colocado corretamente
        if 'ID' in hidx:
            print(f"🔍 [SERVICE] ID na posição {hidx['ID']}: '{row_data[hidx['ID']]}' (deve ser '{client_id}')")
        print(f"✅ [SERVICE] Total de colunas na linha: {len(row_data)} (esperado {expected_len})")
        print("✅ [SERVICE] Linha preparada com cabeçalhos alinhados")

        return row_data
    
    def row_to_client(self, row: List) -> Dict:
        """Converte linha da planilha para dicionário do cliente - SIGEC organizado por blocos"""
        def safe_get(row_, index, default=''):
            try:
                return row_[index] if index < len(row_) and row_[index] else default
            except:
                return default

        def bool_from_text(text, default=False):
            if isinstance(text, bool):
                return text
            if isinstance(text, str):
                return text.upper() in ['SIM', 'TRUE', '1', 'VERDADEIRO', 'S', 'YES']
            return default

        # Mapear índices de cabeçalhos
        headers = self.get_headers()
        hidx = {name: i for i, name in enumerate(headers)}

        # ID: tentar posição atual pelo cabeçalho e legado antes de gerar temporário
        # Se a linha tem menos de 104 colunas, o ID provavelmente está na posição 83 (legado)
        if len(row) <= 86:
            # Para dados legados (86 colunas ou menos), ID está na posição 83
            id_atual = safe_get(row, 83)
            id_legado = safe_get(row, 78)
        else:
            # Para dados novos (mais de 86 colunas), ID está na posição calculada pelos headers
            id_atual = safe_get(row, hidx.get('ID', 103))
            id_legado = safe_get(row, 83)  # fallback para posição legado
        
        id_resolvido = id_atual or id_legado or ''

        result = {
            # Bloco 1: Informações da Pessoa Jurídica
            'nomeEmpresa': safe_get(row, 0),
            'razaoSocialReceita': safe_get(row, 1),
            'nomeFantasiaReceita': safe_get(row, 2),
            'cnpj': safe_get(row, 3),
            'perfil': safe_get(row, 4),
            'perfilCliente': safe_get(row, 4),
            'inscEst': safe_get(row, 5),
            'inscMun': safe_get(row, 6),
            'estado': safe_get(row, 7),
            'cidade': safe_get(row, 8),
            'regimeFederal': safe_get(row, 9),
            'regimeEstadual': safe_get(row, 10),
            'segmento': safe_get(row, 11),
            'atividade': safe_get(row, 12),

            # Compatibilidade com campos legados
            'tributacao': safe_get(row, 9),
            'cpfCnpj': safe_get(row, 3),

            # Bloco 2: Serviços Prestados pela Control
            'ct': bool_from_text(safe_get(row, 13)),
            'fs': bool_from_text(safe_get(row, 14)),
            'dp': bool_from_text(safe_get(row, 15)),
            'bpoFinanceiro': bool_from_text(safe_get(row, 16)),

            # Códigos dos Sistemas (Bloco 2)
            'codFortesCt': safe_get(row, 18),
            'codFortesFs': safe_get(row, 19),
            'codFortesPs': safe_get(row, 20),
            'codDominio': safe_get(row, 21),
            'sistemaUtilizado': safe_get(row, 22),

            # Bloco 3: Quadro Societário - MAPEAMENTO CORRIGIDO PARA TEMPLATE
            'socio_1_nome': safe_get(row, 23),
            'socio_1_cpf': safe_get(row, 24),
            'socio_1_data_nascimento': safe_get(row, 25),
            'socio_1_administrador': bool_from_text(safe_get(row, 26)),
            'socio_1_participacao': safe_get(row, 27),
            'socio_1_resp_legal': bool_from_text(safe_get(row, 28)),

            # Campos legados para compatibilidade total
            'socio1_nome': safe_get(row, 23),
            'socio1_cpf': safe_get(row, 24),
            'socio1_nascimento': safe_get(row, 25),
            'socio1_admin': bool_from_text(safe_get(row, 26)),
            'socio1_cotas': safe_get(row, 27),
            'socio1_resp_legal': bool_from_text(safe_get(row, 28)),
            'socio1': safe_get(row, 23),  # Nome do sócio 1
            'mesAnoInicio': safe_get(row, 17),

            # Bloco 4: Contatos
            'telefoneFixo': safe_get(row, 29),
            'telefoneCelular': safe_get(row, 30),
            'whatsapp': safe_get(row, 31),
            'emailPrincipal': safe_get(row, 32),
            'emailSecundario': safe_get(row, 33),
            'responsavelImediato': safe_get(row, 34),
            'emailsSocios': safe_get(row, 35),
            'contatoContador': safe_get(row, 36),
            'telefoneContador': safe_get(row, 37),
            'emailContador': safe_get(row, 38),

            # Campos legados para compatibilidade
            'emailsSocio': safe_get(row, 35),

            # Bloco 4: Contatos Detalhados (CORRIGIDO - convertendo índices 1-based para 0-based)
            'contato_1_nome': safe_get(row, 39),     # 40-1 = 39 (CONTATO_1_NOME)
            'contato_1_cargo': safe_get(row, 40),    # 41-1 = 40 (CONTATO_1_CARGO)
            'contato_1_telefone': safe_get(row, 41), # 42-1 = 41 (CONTATO_1_TELEFONE)
            'contato_1_email': safe_get(row, 42),    # 43-1 = 42 (CONTATO_1_EMAIL)
            'contato_2_nome': safe_get(row, 43),     # 44-1 = 43 (CONTATO_2_NOME)
            'contato_2_cargo': safe_get(row, 44),    # 45-1 = 44 (CONTATO_2_CARGO)
            'contato_2_telefone': safe_get(row, 45), # 46-1 = 45 (CONTATO_2_TELEFONE)
            'contato_2_email': safe_get(row, 46),    # 47-1 = 46 (CONTATO_2_EMAIL)
            'contato_3_nome': safe_get(row, 47),     # 48-1 = 47 (CONTATO_3_NOME)
            'contato_3_cargo': safe_get(row, 48),    # 49-1 = 48 (CONTATO_3_CARGO)
            'contato_3_telefone': safe_get(row, 49), # 50-1 = 49 (CONTATO_3_TELEFONE)
            'contato_3_email': safe_get(row, 50),    # 51-1 = 50 (CONTATO_3_EMAIL)
            'contato_4_nome': safe_get(row, 51),     # 52-1 = 51 (CONTATO_4_NOME)
            'contato_4_cargo': safe_get(row, 52),    # 53-1 = 52 (CONTATO_4_CARGO)
            'contato_4_telefone': safe_get(row, 53), # 54-1 = 53 (CONTATO_4_TELEFONE)
            'contato_4_email': safe_get(row, 54),    # 55-1 = 54 (CONTATO_4_EMAIL)
            'contato_5_nome': safe_get(row, 55),     # 56-1 = 55 (CONTATO_5_NOME)
            'contato_5_cargo': safe_get(row, 56),    # 57-1 = 56 (CONTATO_5_CARGO)
            'contato_5_telefone': safe_get(row, 57), # 58-1 = 57 (CONTATO_5_TELEFONE)
            'contato_5_email': safe_get(row, 58),    # 59-1 = 58 (CONTATO_5_EMAIL)

            # Bloco 5: Senhas e Credenciais (APENAS CAMPOS ESPECIFICADOS)
            'cpfCnpjSn': safe_get(row, 59),          # 60-1 = 59 (CPF/CNPJ SN)
            'codigoAcessoSn': safe_get(row, 60),     # 61-1 = 60 (CÓDIGO ACESSO SN)
            'acessoEmpWeb': safe_get(row, 61),       # 62-1 = 61 (ACESSO EMPWEB)
            'senhaEmpWeb': safe_get(row, 62),        # 63-1 = 62 (SENHA EMPWEB)
            'acessoIss': safe_get(row, 63),          # 64-1 = 63 (ACESSO ISS)
            'acessoSefin': safe_get(row, 64),        # 65-1 = 64 (ACESSO SEFIN)
            'acessoSeuma': safe_get(row, 65),        # 66-1 = 65 (ACESSO SEUMA)
            'acessoSemace': safe_get(row, 66),       # 67-1 = 66 (ACESSO SEMACE)
            'acessoIbama': safe_get(row, 67),        # 68-1 = 67 (ACESSO IBAMA)
            'acessoFapInss': safe_get(row, 68),      # 69-1 = 68 (ACESSO FAP/INSS)
            'acessoCrf': safe_get(row, 69),          # 70-1 = 69 (ACESSO CRF)
            'senhaSemace': safe_get(row, 70),        # 71-1 = 70 (SENHA SEMACE)
            'anvisaGestor': safe_get(row, 71),       # 72-1 = 71 (ANVISA GESTOR)
            'anvisaEmpresa': safe_get(row, 72),      # 73-1 = 72 (ANVISA EMPRESA)

            # Bloco 6: Procurações (CORRIGIDO - alinhado com formulário)
            'procReceita': bool_from_text(safe_get(row, 73)),     # 74-1 = 73 (PROCURAÇÃO RECEITA)
            'dataProcReceita': safe_get(row, 74),                 # 75-1 = 74 (DATA PROCURAÇÃO RECEITA)
            'procDte': bool_from_text(safe_get(row, 75)),         # 76-1 = 75 (PROCURAÇÃO DTe)
            'dataProcDte': safe_get(row, 76),                     # 77-1 = 76 (DATA PROCURAÇÃO DTe)
            'procCaixa': bool_from_text(safe_get(row, 77)),       # 78-1 = 77 (PROCURAÇÃO CAIXA)
            'dataProcCaixa': safe_get(row, 78),                   # 79-1 = 78 (DATA PROCURAÇÃO CAIXA)
            'procEmpWeb': bool_from_text(safe_get(row, 79)),      # 80-1 = 79 (PROCURAÇÃO EMP WEB)
            'dataProcEmpWeb': safe_get(row, 80),                  # 81-1 = 80 (DATA PROCURAÇÃO EMP WEB)
            'procDet': bool_from_text(safe_get(row, 81)),         # 82-1 = 81 (PROCURAÇÃO DET)
            'dataProcDet': safe_get(row, 82),                     # 83-1 = 82 (DATA PROCURAÇÃO DET)
            'outrasProc': safe_get(row, 83),                      # 84-1 = 83 (OUTRAS PROCURAÇÕES)
            'obsProcuracoes': safe_get(row, 84),                  # 85-1 = 84 (OBSERVAÇÕES PROCURAÇÕES)

            # Bloco 7: Observações e Dados Adicionais (CORRIGIDO - índices ajustados)
            'observacoesGerais': safe_get(row, 85),            # 86-1 = 85
            'tarefasVinculadas': int(safe_get(row, hidx.get('TAREFAS VINCULADAS', 86), 0)) if str(safe_get(row, hidx.get('TAREFAS VINCULADAS', 86), 0)).isdigit() else 0,
            'dataInicioServicos': safe_get(row, hidx.get('DATA INÍCIO SERVIÇOS', 87)),  # 88-1 = 87
            'statusCliente': safe_get(row, hidx.get('STATUS DO CLIENTE', 88), 'ATIVO'),
            'ultimaAtualizacao': safe_get(row, hidx.get('ÚLTIMA ATUALIZAÇÃO', 89)),
            'responsavelAtualizacao': safe_get(row, hidx.get('RESPONSÁVEL ATUALIZAÇÃO', 90)),
            'prioridadeCliente': safe_get(row, hidx.get('PRIORIDADE', 91), 'NORMAL'),
            'tagsCliente': safe_get(row, hidx.get('TAGS/CATEGORIAS', 92)),
            'historicoAlteracoes': safe_get(row, hidx.get('HISTÓRICO DE ALTERAÇÕES', 93)),

            # Campos internos do sistema (alinhados aos cabeçalhos - índices ajustados)
            'id': id_resolvido,
            'donoResp': safe_get(row, hidx.get('DONO/RESPONSÁVEL', 94)),
            'ativo': bool_from_text(safe_get(row, hidx.get('CLIENTE ATIVO', 95), 'SIM'), True),
            'criadoEm': safe_get(row, hidx.get('DATA DE CRIAÇÃO', 96), safe_get(row, hidx.get('RESERVADO 2', 84), datetime.now().isoformat())),
            'domestica': safe_get(row, hidx.get('DOMÉSTICA', 98)),
            'geraArquivoSped': safe_get(row, hidx.get('GERA ARQUIVO DO SPED', 99))
        }

        # DEBUG e VALIDAÇÃO do ID
        client_id = result.get('id', '')
        nome_empresa = result.get('nomeEmpresa', 'N/A')

        if not client_id or str(client_id).strip() == '':
            print(f"⚠️ [ROW_TO_CLIENT] Cliente '{nome_empresa}' sem ID! Gerando ID temporário...")
            safe_name = ''.join(c for c in nome_empresa[:3] if c.isalnum()).upper()
            timestamp_id = int(datetime.now().timestamp())
            temp_id = f"{safe_name}{timestamp_id}"
            result['id'] = temp_id
            print(f"⚠️ [ROW_TO_CLIENT] ID temporário gerado: '{temp_id}'")
        else:
            print(f"✅ [ROW_TO_CLIENT] Cliente '{nome_empresa}' com ID válido: '{client_id}' (origem: {'94' if id_atual else '89'})")

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
            
            def update_cell(self, row, col, value):
                """Simula gspread.update_cell()"""
                try:
                    # Converte número da coluna para letra (1=A, 2=B, etc.)
                    col_letter = chr(64 + col)  # 1=A, 2=B, etc.
                    range_name = f"{self.worksheet_name}!{col_letter}{row}"
                    
                    body = {'values': [[value]]}
                    result = self.service.spreadsheets().values().update(
                        spreadsheetId=self.spreadsheet_id,
                        range=range_name,
                        valueInputOption='USER_ENTERED',
                        body=body
                    ).execute()
                    return True
                except Exception as e:
                    print(f"❌ Erro ao atualizar célula {row},{col} da aba '{self.worksheet_name}': {e}")
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
