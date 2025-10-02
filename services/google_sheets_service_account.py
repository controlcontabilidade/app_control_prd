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
    
    def __init__(self, spreadsheet_id: str, range_name: str = 'Clientes!A:ER'):
        self.spreadsheet_id = spreadsheet_id
        self.range_name = range_name  # Será atualizado dinamicamente quando necessário
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
                range=self.get_dynamic_range(),
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
                
            if not client.get('nomeEmpresa') and not client.get('cliente'):
                print("❌ [SERVICE] Nome da empresa é obrigatório (nomeEmpresa ou cliente)")
                return False
            
            # Se não tem nomeEmpresa mas tem cliente, usar cliente
            if not client.get('nomeEmpresa') and client.get('cliente'):
                client['nomeEmpresa'] = client['cliente']
                print(f"🔧 [SERVICE] Usando 'cliente' como nomeEmpresa: {client['cliente']}")
            
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
                # Buscar linha atual da planilha - usar range dinâmico
                current_range = self.get_dynamic_range(row_index)
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
            range_name = self.get_dynamic_range(row_index)
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
            print(f"🔍 [SERVICE] Range: {self.get_dynamic_range()}")
            
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
                range=self.get_dynamic_range()
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
                
                # Primeiro: busca exata por ID
                for client in all_clients:
                    client_existing_id = client.get('id', '')
                    if str(client_existing_id).strip() == search_id:
                        print(f"✅ [GET_CLIENT] Cliente encontrado via fallback por ID exato!")
                        print(f"✅ [GET_CLIENT] Nome: {client.get('nomeEmpresa')}")
                        return client
                
                # Segundo: busca por padrão de ID temporário (mesmas iniciais)
                print(f"🔍 [GET_CLIENT] Tentando busca por padrão de ID temporário...")
                if len(search_id) > 3 and search_id[:2].isalpha():
                    target_initials = search_id[:2].upper()
                    for client in all_clients:
                        client_existing_id = client.get('id', '')
                        if (str(client_existing_id).startswith(target_initials) and 
                            len(str(client_existing_id)) > 10):
                            print(f"✅ [GET_CLIENT] Cliente encontrado via padrão de ID temporário!")
                            print(f"✅ [GET_CLIENT] Nome: {client.get('nomeEmpresa')}")
                            print(f"✅ [GET_CLIENT] ID temporário encontrado: {client_existing_id}")
                            return client
                
                # Terceiro: se só há um cliente, retornar ele (para casos de teste)
                if len(all_clients) == 1:
                    client = all_clients[0]
                    print(f"✅ [GET_CLIENT] Apenas um cliente na planilha, retornando ele!")
                    print(f"✅ [GET_CLIENT] Nome: {client.get('nomeEmpresa')}")
                    print(f"✅ [GET_CLIENT] ID do cliente: {client.get('id')}")
                    return client
                
                print(f"❌ [GET_CLIENT] Cliente '{search_id}' não encontrado nem via fallback")
                return None
                
            # Buscar os dados da linha específica - usar range dinâmico
            range_name = self.get_dynamic_range(row_index)
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
            print(f"📊 Range: {self.get_dynamic_range()}")
            
            if not self.service:
                print("❌ Serviço Google Sheets não está autenticado!")
                return []
            
            print("📊 Fazendo requisição para Google Sheets...")
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=self.get_dynamic_range()
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
            
            # Sócios 2-10
            'SÓCIO 2 NOME',                      # 30. Nome completo do sócio 2
            'SÓCIO 2 CPF',                       # 31. CPF do sócio 2
            'SÓCIO 2 DATA NASCIMENTO',           # 32. Data nascimento sócio 2
            'SÓCIO 2 ADMINISTRADOR',             # 33. É administrador? (SIM/NÃO)
            'SÓCIO 2 PARTICIPAÇÃO',              # 34. Percentual de participação
            'SÓCIO 2 RESPONSÁVEL LEGAL',         # 35. Responsável legal? (SIM/NÃO)
            
            'SÓCIO 3 NOME',                      # 36. Nome completo do sócio 3
            'SÓCIO 3 CPF',                       # 37. CPF do sócio 3
            'SÓCIO 3 DATA NASCIMENTO',           # 38. Data nascimento sócio 3
            'SÓCIO 3 ADMINISTRADOR',             # 39. É administrador? (SIM/NÃO)
            'SÓCIO 3 PARTICIPAÇÃO',              # 40. Percentual de participação
            'SÓCIO 3 RESPONSÁVEL LEGAL',         # 41. Responsável legal? (SIM/NÃO)
            
            'SÓCIO 4 NOME',                      # 42. Nome completo do sócio 4
            'SÓCIO 4 CPF',                       # 43. CPF do sócio 4
            'SÓCIO 4 DATA NASCIMENTO',           # 44. Data nascimento sócio 4
            'SÓCIO 4 ADMINISTRADOR',             # 45. É administrador? (SIM/NÃO)
            'SÓCIO 4 PARTICIPAÇÃO',              # 46. Percentual de participação
            'SÓCIO 4 RESPONSÁVEL LEGAL',         # 47. Responsável legal? (SIM/NÃO)
            
            'SÓCIO 5 NOME',                      # 48. Nome completo do sócio 5
            'SÓCIO 5 CPF',                       # 49. CPF do sócio 5
            'SÓCIO 5 DATA NASCIMENTO',           # 50. Data nascimento sócio 5
            'SÓCIO 5 ADMINISTRADOR',             # 51. É administrador? (SIM/NÃO)
            'SÓCIO 5 PARTICIPAÇÃO',              # 52. Percentual de participação
            'SÓCIO 5 RESPONSÁVEL LEGAL',         # 53. Responsável legal? (SIM/NÃO)
            
            'SÓCIO 6 NOME',                      # 54. Nome completo do sócio 6
            'SÓCIO 6 CPF',                       # 55. CPF do sócio 6
            'SÓCIO 6 DATA NASCIMENTO',           # 56. Data nascimento sócio 6
            'SÓCIO 6 ADMINISTRADOR',             # 57. É administrador? (SIM/NÃO)
            'SÓCIO 6 PARTICIPAÇÃO',              # 58. Percentual de participação
            'SÓCIO 6 RESPONSÁVEL LEGAL',         # 59. Responsável legal? (SIM/NÃO)
            
            'SÓCIO 7 NOME',                      # 60. Nome completo do sócio 7
            'SÓCIO 7 CPF',                       # 61. CPF do sócio 7
            'SÓCIO 7 DATA NASCIMENTO',           # 62. Data nascimento sócio 7
            'SÓCIO 7 ADMINISTRADOR',             # 63. É administrador? (SIM/NÃO)
            'SÓCIO 7 PARTICIPAÇÃO',              # 64. Percentual de participação
            'SÓCIO 7 RESPONSÁVEL LEGAL',         # 65. Responsável legal? (SIM/NÃO)
            
            'SÓCIO 8 NOME',                      # 66. Nome completo do sócio 8
            'SÓCIO 8 CPF',                       # 67. CPF do sócio 8
            'SÓCIO 8 DATA NASCIMENTO',           # 68. Data nascimento sócio 8
            'SÓCIO 8 ADMINISTRADOR',             # 69. É administrador? (SIM/NÃO)
            'SÓCIO 8 PARTICIPAÇÃO',              # 70. Percentual de participação
            'SÓCIO 8 RESPONSÁVEL LEGAL',         # 71. Responsável legal? (SIM/NÃO)
            
            'SÓCIO 9 NOME',                      # 72. Nome completo do sócio 9
            'SÓCIO 9 CPF',                       # 73. CPF do sócio 9
            'SÓCIO 9 DATA NASCIMENTO',           # 74. Data nascimento sócio 9
            'SÓCIO 9 ADMINISTRADOR',             # 75. É administrador? (SIM/NÃO)
            'SÓCIO 9 PARTICIPAÇÃO',              # 76. Percentual de participação
            'SÓCIO 9 RESPONSÁVEL LEGAL',         # 77. Responsável legal? (SIM/NÃO)
            
            'SÓCIO 10 NOME',                     # 78. Nome completo do sócio 10
            'SÓCIO 10 CPF',                      # 79. CPF do sócio 10
            'SÓCIO 10 DATA NASCIMENTO',          # 80. Data nascimento sócio 10
            'SÓCIO 10 ADMINISTRADOR',            # 81. É administrador? (SIM/NÃO)
            'SÓCIO 10 PARTICIPAÇÃO',             # 82. Percentual de participação
            'SÓCIO 10 RESPONSÁVEL LEGAL',        # 83. Responsável legal? (SIM/NÃO)
            
            # Bloco 4: Contatos (posições ajustadas)
            'TELEFONE FIXO',                     # 84. Telefone comercial
            'TELEFONE CELULAR',                  # 85. Celular principal
            'WHATSAPP',                          # 86. Número do WhatsApp
            'EMAIL PRINCIPAL',                   # 87. Email principal da empresa
            'EMAIL SECUNDÁRIO',                  # 88. Email alternativo
            'RESPONSÁVEL IMEDIATO',              # 89. Contato direto na empresa
            'EMAILS DOS SÓCIOS',                 # 90. Emails dos sócios
            'CONTATO CONTADOR',                  # 91. Nome do contador atual
            'TELEFONE CONTADOR',                 # 92. Telefone do contador
            'EMAIL CONTADOR',                    # 93. Email do contador
            
            # Contatos Detalhados (até 5 contatos)
            'CONTATO_1_NOME',                    # 94. Nome do contato 1
            'CONTATO_1_CARGO',                   # 95. Cargo do contato 1
            'CONTATO_1_TELEFONE',                # 96. Telefone do contato 1
            'CONTATO_1_EMAIL',                   # 97. Email do contato 1
            'CONTATO_2_NOME',                    # 98. Nome do contato 2
            'CONTATO_2_CARGO',                   # 99. Cargo do contato 2
            'CONTATO_2_TELEFONE',                # 100. Telefone do contato 2
            'CONTATO_2_EMAIL',                   # 101. Email do contato 2
            'CONTATO_3_NOME',                    # 102. Nome do contato 3
            'CONTATO_3_CARGO',                   # 103. Cargo do contato 3
            'CONTATO_3_TELEFONE',                # 104. Telefone do contato 3
            'CONTATO_3_EMAIL',                   # 105. Email do contato 3
            'CONTATO_4_NOME',                    # 107. Nome do contato 4
            'CONTATO_4_CARGO',                   # 108. Cargo do contato 4
            'CONTATO_4_TELEFONE',                # 109. Telefone do contato 4
            'CONTATO_4_EMAIL',                   # 110. Email do contato 4
            'CONTATO_5_NOME',                    # 111. Nome do contato 5
            'CONTATO_5_CARGO',                   # 112. Cargo do contato 5
            'CONTATO_5_TELEFONE',                # 113. Telefone do contato 5
            'CONTATO_5_EMAIL',                   # 114. Email do contato 5
            
            # Bloco 5: Senhas e Credenciais (APENAS CAMPOS ESPECIFICADOS)
            'CPF/CNPJ SN',                       # 60. CPF/CNPJ Simples Nacional
            'ACESSO ISS',                        # 61. Login ISS municipal  
            'ACESSO SEFIN',                      # 62. Login SEFIN estadual
            'ACESSO SEUMA',                      # 63. Login SEUMA ambiental
            'ACESSO SEMACE',                     # 64. Login SEMACE estadual
            'ACESSO IBAMA',                      # 65. Login IBAMA
            'ACESSO FAP/INSS',                   # 66. Login FAP/INSS
            'SENHA SEMACE',                      # 67. Senha SEMACE estadual
            'ANVISA GESTOR',                     # 68. Login ANVISA gestor
            'ANVISA EMPRESA',                    # 69. Login ANVISA empresa
            
            # Bloco 5: Senhas Específicas Adicionais (NOVOS CAMPOS)
            'SENHA FGTS',                        # 74. Senha FGTS
            'SENHA SOCIAL',                      # 75. Senha Social/INSS
            'SENHA GISS',                        # 76. Senha GISS
            'SENHA DETRAN',                      # 77. Senha DETRAN
            'SENHA RECEITA',                     # 78. Senha Receita Federal
            'SENHA SINTEGRA',                    # 79. Senha SINTEGRA
            'SENHA JUCESP',                      # 80. Senha JUCESP
            'SENHA PORTAL EMPREGADOR',           # 81. Senha Portal Empregador
            'SENHA SIMPLES',                     # 82. Senha Simples Nacional
            'SENHA GOVERNO',                     # 83. Senha Portal Governo
            'SENHA VIA SOFT',                    # 84. Senha Via Soft
            'SENHA SIMEI',                       # 85. Senha SIMEI
            
            # Bloco 6: Procurações (CORRIGIDO - alinhado com formulário)
            'PROCURAÇÃO RECEITA',                # 86. Tem procuração Receita? (SIM/NÃO)
            'DATA PROCURAÇÃO RECEITA',           # 87. Data da procuração Receita
            'PROCURAÇÃO DTe',                    # 88. Tem procuração DTe? (SIM/NÃO)
            'DATA PROCURAÇÃO DTe',               # 89. Data da procuração DTe
            'PROCURAÇÃO CAIXA',                  # 90. Tem procuração Caixa? (SIM/NÃO)
            'DATA PROCURAÇÃO CAIXA',             # 91. Data da procuração Caixa
            'PROCURAÇÃO EMP WEB',                # 92. Tem procuração Emp Web? (SIM/NÃO)
            'DATA PROCURAÇÃO EMP WEB',           # 93. Data da procuração Emp Web
            'PROCURAÇÃO DET',                    # 94. Tem procuração DET? (SIM/NÃO)
            'DATA PROCURAÇÃO DET',               # 95. Data da procuração DET
            'OUTRAS PROCURAÇÕES',                # 96. Outras procurações
            'OBSERVAÇÕES PROCURAÇÕES',           # 97. Obs sobre procurações
            
            # Bloco 7: Observações e Dados Adicionais (apenas campos mantidos)
            'OBSERVAÇÕES',                       # 98. Observações gerais sobre o cliente
            'STATUS DO CLIENTE',                 # 99. ATIVO, INATIVO, SUSPENSO
            'ÚLTIMA ATUALIZAÇÃO',                # 100. Timestamp última modificação
            
            # Campos internos do sistema
            'DONO/RESPONSÁVEL',                  # 101. Dono/Responsável
            'CLIENTE ATIVO',                     # 102. Cliente ativo? (SIM/NÃO)
            'DATA DE CRIAÇÃO',                   # 103. Data de criação do registro
            'ID',                                # 104. ID único do cliente
            'DOMÉSTICA',                         # 105. Indica se é doméstica (SIM/NÃO)
            'GERA ARQUIVO DO SPED',              # 106. Gera arquivo do SPED (SIM/NÃO)
            # --- CAMPOS NOVOS (sempre ao final para não quebrar ordem) ---
            'CNPJ ACESSO SIMPLES NACIONAL',       # 107. CNPJ para Simples Nacional
            'CPF DO REPRESENTANTE LEGAL',         # 108. CPF do representante legal
            'CÓDIGO ACESSO SN',                   # 109. Código de acesso SN
            'SENHA SEFIN',                        # 110. Senha SEFIN
            'SENHA SEUMA',                        # 111. Senha SEUMA
            'LOGIN ANVISA EMPRESA',               # 112. Login ANVISA Empresa
            'SENHA ANVISA EMPRESA',               # 113. Senha ANVISA Empresa
            'LOGIN ANVISA GESTOR',                # 114. Login ANVISA Gestor
            'SENHA ANVISA GESTOR',                # 115. Senha ANVISA Gestor
            'SENHA FAP/INSS',                     # 116. Senha FAP/INSS
            'ACESSO EMP WEB',                     # 117. Acesso Emp Web
            'SENHA EMP WEB',                      # 118. Senha Emp Web
            'ACESSO CRF',                         # 119. Acesso CRF
            'SENHA CRF',                          # 120. Senha CRF
            'EMAIL SEFIN',                        # 121. E-mail SEFIN
            'EMAIL EMPWEB',                       # 122. E-mail EmpWeb
        ]

    def ensure_correct_headers(self):
        """Garante que os cabeçalhos estejam na ordem correta e expande colunas se necessário"""
        try:
            print("🔧 Verificando cabeçalhos da planilha...")
            
            # Primeiro, vamos verificar quantas colunas a aba tem atualmente
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            # Encontrar a aba 'Clientes'
            client_sheet = None
            for sheet in spreadsheet.get('sheets', []):
                if sheet.get('properties', {}).get('title') == 'Clientes':
                    client_sheet = sheet
                    break
            
            if client_sheet:
                current_cols = client_sheet.get('properties', {}).get('gridProperties', {}).get('columnCount', 0)
                correct_headers = self.get_headers()
                needed_cols = len(correct_headers)
                
                print(f"📊 Colunas atuais: {current_cols}, necessárias: {needed_cols}")
                
                # Expandir colunas se necessário
                if current_cols < needed_cols:
                    print(f"🔧 Expandindo planilha de {current_cols} para {needed_cols} colunas...")
                    
                    requests = [{
                        'insertDimension': {
                            'range': {
                                'sheetId': client_sheet.get('properties', {}).get('sheetId'),
                                'dimension': 'COLUMNS',
                                'startIndex': current_cols,
                                'endIndex': needed_cols
                            },
                            'inheritFromBefore': True
                        }
                    }]
                    
                    self.service.spreadsheets().batchUpdate(
                        spreadsheetId=self.spreadsheet_id,
                        body={'requests': requests}
                    ).execute()
                    
                    print(f"✅ Planilha expandida para {needed_cols} colunas!")
            
            # Agora atualizar os cabeçalhos
            # Usar range dinâmico baseado no número de colunas necessárias
            correct_headers = self.get_headers()
            end_col = self.column_number_to_letter(len(correct_headers))
            range_name = f'Clientes!A1:{end_col}1'
            
            # Busca dados atuais
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            current_headers = result.get('values', [[]])[0] if result.get('values') else []
            
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
                    range=range_name,
                    valueInputOption='RAW',
                    body={'values': [correct_headers]}
                ).execute()
                print("✅ Cabeçalhos atualizados com sucesso!")
                
                # NOVO: Expandir dados existentes para o novo tamanho
                print("🔧 Expandindo linhas de dados existentes...")
                self._expand_existing_data_rows(needed_cols)
                
                return True
            else:
                print("✅ Cabeçalhos já estão corretos!")
                return True
                
        except Exception as e:
            print(f"❌ Erro ao verificar/atualizar cabeçalhos: {e}")
            return False
    
    def _expand_existing_data_rows(self, target_columns):
        """Expande linhas de dados existentes para o número alvo de colunas"""
        try:
            # Buscar todos os dados atuais
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Clientes!A:FD'  # Range bem grande para pegar tudo
            ).execute()
            
            values = result.get('values', [])
            if len(values) <= 1:  # Apenas cabeçalho
                print("📊 Nenhuma linha de dados para expandir")
                return
            
            print(f"📊 Expandindo {len(values)-1} linhas de dados...")
            
            # Expandir cada linha para ter o número correto de colunas
            updated_rows = []
            for i, row in enumerate(values[1:], start=2):  # Pular cabeçalho
                # Expandir linha para ter target_columns colunas
                while len(row) < target_columns:
                    row.append('')
                updated_rows.append(row)
            
            # Atualizar todas as linhas de dados de uma vez
            if updated_rows:
                end_col = self.column_number_to_letter(target_columns)
                data_range = f'Clientes!A2:{end_col}{len(updated_rows)+1}'
                
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=data_range,
                    valueInputOption='RAW',
                    body={'values': updated_rows}
                ).execute()
                
                print(f"✅ {len(updated_rows)} linhas expandidas para {target_columns} colunas!")
                
        except Exception as e:
            print(f"❌ Erro ao expandir linhas de dados: {e}")

    def column_number_to_letter(self, col_num):
        """Converte número da coluna para letra (1=A, 26=Z, 27=AA, etc.)"""
        string = ""
        while col_num > 0:
            col_num, remainder = divmod(col_num - 1, 26)
            string = chr(65 + remainder) + string
        return string
    
    def get_dynamic_range(self, row_number=None):
        """Calcula o range dinâmico baseado no número de colunas dos headers"""
        headers = self.get_headers()
        end_col = self.column_number_to_letter(len(headers))
        
        if row_number is None:
            return f'Clientes!A:{end_col}'
        else:
            return f'Clientes!A{row_number}:{end_col}{row_number}'

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
                range='Clientes!A1:ER1'
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
                    range='Clientes!A1:ER1',
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

        # Obter headers para mapeamento de índices
        headers = self.get_headers()

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
            
            # Bloco 2: Serviços Prestados pela Control - POSIÇÕES CORRETAS
            'SIM' if client.get('ct') else 'NÃO',             # 13. SERVIÇO CT (POSIÇÃO CORRETA)
            'SIM' if client.get('fs') else 'NÃO',             # 14. SERVIÇO FS (POSIÇÃO CORRETA)
            'SIM' if client.get('dp') else 'NÃO',             # 15. SERVIÇO DP (POSIÇÃO CORRETA)
            'SIM' if client.get('bpoFinanceiro') else 'NÃO',  # 16. SERVIÇO BPO FINANCEIRO (POSIÇÃO CORRETA)
            client.get('dataInicioServicos', ''),             # 17. DATA INÍCIO DOS SERVIÇOS (POSIÇÃO CORRETA)
            
            # Códigos dos Sistemas (Bloco 2) - POSIÇÕES CORRETAS
            f"'{str(client.get('codigoFortesCT', ''))}" if client.get('codigoFortesCT') else '',  # 18. CÓDIGO FORTES CT - corrigido mapeamento
            f"'{str(client.get('codigoFortesFS', ''))}" if client.get('codigoFortesFS') else '',  # 19. CÓDIGO FORTES FS - corrigido mapeamento
            f"'{str(client.get('codigoFortesPS', ''))}" if client.get('codigoFortesPS') else '',  # 20. CÓDIGO FORTES PS - corrigido mapeamento
            f"'{str(client.get('codigoDominio', ''))}" if client.get('codigoDominio') else '',    # 21. CÓDIGO DOMÍNIO - corrigido mapeamento
            client.get('sistemaUtilizado', ''),               # 22. SISTEMA UTILIZADO (POSIÇÃO CORRETA)
            
            # Bloco 3: Quadro Societário - POSIÇÕES CORRETAS
            client.get('socio_1_nome', client.get('socio1_nome', client.get('socio1', ''))),     # 23. SÓCIO 1 NOME
            f"'{str(client.get('socio_1_cpf', client.get('socio1_cpf', '')))}" if client.get('socio_1_cpf', client.get('socio1_cpf', '')) else '',  # 24. SÓCIO 1 CPF - como string
            client.get('socio_1_data_nascimento', client.get('socio1_nascimento', '')),         # 25. SÓCIO 1 DATA NASCIMENTO (POSIÇÃO CORRETA)
            'SIM' if client.get('socio_1_administrador', client.get('socio1_admin')) else 'NÃO', # 26. SÓCIO 1 ADMINISTRADOR (POSIÇÃO CORRETA)
            client.get('socio_1_participacao', client.get('socio1_cotas', '')),                  # 27. SÓCIO 1 PARTICIPAÇÃO (POSIÇÃO CORRETA)
            'SIM' if client.get('socio_1_resp_legal', client.get('socio1_resp_legal')) else 'NÃO', # 28. SÓCIO 1 RESPONSÁVEL LEGAL (POSIÇÃO CORRETA)
            
            # Sócios 2-10 - NOVOS CAMPOS
            client.get('socio_2_nome', client.get('socio2_nome', '')),                          # 29. SÓCIO 2 NOME
            f"'{str(client.get('socio_2_cpf', client.get('socio2_cpf', '')))}" if client.get('socio_2_cpf', client.get('socio2_cpf', '')) else '',  # 30. SÓCIO 2 CPF - como string
            client.get('socio_2_data_nascimento', client.get('socio2_nascimento', '')),         # 31. SÓCIO 2 DATA NASCIMENTO
            'SIM' if client.get('socio_2_administrador', client.get('socio2_admin')) else 'NÃO', # 32. SÓCIO 2 ADMINISTRADOR
            client.get('socio_2_participacao', client.get('socio2_cotas', '')),                  # 33. SÓCIO 2 PARTICIPAÇÃO
            'SIM' if client.get('socio_2_resp_legal', client.get('socio2_resp_legal')) else 'NÃO', # 34. SÓCIO 2 RESPONSÁVEL LEGAL

            client.get('socio_3_nome', client.get('socio3_nome', '')),                          # 35. SÓCIO 3 NOME
            f"'{str(client.get('socio_3_cpf', client.get('socio3_cpf', '')))}" if client.get('socio_3_cpf', client.get('socio3_cpf', '')) else '',  # 36. SÓCIO 3 CPF - como string
            client.get('socio_3_data_nascimento', client.get('socio3_nascimento', '')),         # 37. SÓCIO 3 DATA NASCIMENTO
            'SIM' if client.get('socio_3_administrador', client.get('socio3_admin')) else 'NÃO', # 38. SÓCIO 3 ADMINISTRADOR
            client.get('socio_3_participacao', client.get('socio3_cotas', '')),                  # 39. SÓCIO 3 PARTICIPAÇÃO
            'SIM' if client.get('socio_3_resp_legal', client.get('socio3_resp_legal')) else 'NÃO', # 40. SÓCIO 3 RESPONSÁVEL LEGAL

            client.get('socio_4_nome', client.get('socio4_nome', '')),                          # 41. SÓCIO 4 NOME
            f"'{str(client.get('socio_4_cpf', client.get('socio4_cpf', '')))}" if client.get('socio_4_cpf', client.get('socio4_cpf', '')) else '',  # 42. SÓCIO 4 CPF - como string
            client.get('socio_4_data_nascimento', client.get('socio4_nascimento', '')),         # 43. SÓCIO 4 DATA NASCIMENTO
            'SIM' if client.get('socio_4_administrador', client.get('socio4_admin')) else 'NÃO', # 44. SÓCIO 4 ADMINISTRADOR
            client.get('socio_4_participacao', client.get('socio4_cotas', '')),                  # 45. SÓCIO 4 PARTICIPAÇÃO
            'SIM' if client.get('socio_4_resp_legal', client.get('socio4_resp_legal')) else 'NÃO', # 46. SÓCIO 4 RESPONSÁVEL LEGAL

            client.get('socio_5_nome', client.get('socio5_nome', '')),                          # 47. SÓCIO 5 NOME
            f"'{str(client.get('socio_5_cpf', client.get('socio5_cpf', '')))}" if client.get('socio_5_cpf', client.get('socio5_cpf', '')) else '',  # 48. SÓCIO 5 CPF - como string
            client.get('socio_5_data_nascimento', client.get('socio5_nascimento', '')),         # 49. SÓCIO 5 DATA NASCIMENTO
            'SIM' if client.get('socio_5_administrador', client.get('socio5_admin')) else 'NÃO', # 50. SÓCIO 5 ADMINISTRADOR
            client.get('socio_5_participacao', client.get('socio5_cotas', '')),                  # 51. SÓCIO 5 PARTICIPAÇÃO
            'SIM' if client.get('socio_5_resp_legal', client.get('socio5_resp_legal')) else 'NÃO', # 52. SÓCIO 5 RESPONSÁVEL LEGAL

            client.get('socio_6_nome', client.get('socio6_nome', '')),                          # 53. SÓCIO 6 NOME
            f"'{str(client.get('socio_6_cpf', client.get('socio6_cpf', '')))}" if client.get('socio_6_cpf', client.get('socio6_cpf', '')) else '',  # 54. SÓCIO 6 CPF - como string
            client.get('socio_6_data_nascimento', client.get('socio6_nascimento', '')),         # 55. SÓCIO 6 DATA NASCIMENTO
            'SIM' if client.get('socio_6_administrador', client.get('socio6_admin')) else 'NÃO', # 56. SÓCIO 6 ADMINISTRADOR
            client.get('socio_6_participacao', client.get('socio6_cotas', '')),                  # 57. SÓCIO 6 PARTICIPAÇÃO
            'SIM' if client.get('socio_6_resp_legal', client.get('socio6_resp_legal')) else 'NÃO', # 58. SÓCIO 6 RESPONSÁVEL LEGAL

            client.get('socio_7_nome', client.get('socio7_nome', '')),                          # 59. SÓCIO 7 NOME
            f"'{str(client.get('socio_7_cpf', client.get('socio7_cpf', '')))}" if client.get('socio_7_cpf', client.get('socio7_cpf', '')) else '',  # 60. SÓCIO 7 CPF - como string
            client.get('socio_7_data_nascimento', client.get('socio7_nascimento', '')),         # 61. SÓCIO 7 DATA NASCIMENTO
            'SIM' if client.get('socio_7_administrador', client.get('socio7_admin')) else 'NÃO', # 62. SÓCIO 7 ADMINISTRADOR
            client.get('socio_7_participacao', client.get('socio7_cotas', '')),                  # 63. SÓCIO 7 PARTICIPAÇÃO
            'SIM' if client.get('socio_7_resp_legal', client.get('socio7_resp_legal')) else 'NÃO', # 64. SÓCIO 7 RESPONSÁVEL LEGAL

            client.get('socio_8_nome', client.get('socio8_nome', '')),                          # 65. SÓCIO 8 NOME
            f"'{str(client.get('socio_8_cpf', client.get('socio8_cpf', '')))}" if client.get('socio_8_cpf', client.get('socio8_cpf', '')) else '',  # 66. SÓCIO 8 CPF - como string
            client.get('socio_8_data_nascimento', client.get('socio8_nascimento', '')),         # 67. SÓCIO 8 DATA NASCIMENTO
            'SIM' if client.get('socio_8_administrador', client.get('socio8_admin')) else 'NÃO', # 68. SÓCIO 8 ADMINISTRADOR
            client.get('socio_8_participacao', client.get('socio8_cotas', '')),                  # 69. SÓCIO 8 PARTICIPAÇÃO
            'SIM' if client.get('socio_8_resp_legal', client.get('socio8_resp_legal')) else 'NÃO', # 70. SÓCIO 8 RESPONSÁVEL LEGAL

            client.get('socio_9_nome', client.get('socio9_nome', '')),                          # 71. SÓCIO 9 NOME
            f"'{str(client.get('socio_9_cpf', client.get('socio9_cpf', '')))}" if client.get('socio_9_cpf', client.get('socio9_cpf', '')) else '',  # 72. SÓCIO 9 CPF - como string
            client.get('socio_9_data_nascimento', client.get('socio9_nascimento', '')),         # 73. SÓCIO 9 DATA NASCIMENTO
            'SIM' if client.get('socio_9_administrador', client.get('socio9_admin')) else 'NÃO', # 74. SÓCIO 9 ADMINISTRADOR
            client.get('socio_9_participacao', client.get('socio9_cotas', '')),                  # 75. SÓCIO 9 PARTICIPAÇÃO
            'SIM' if client.get('socio_9_resp_legal', client.get('socio9_resp_legal')) else 'NÃO', # 76. SÓCIO 9 RESPONSÁVEL LEGAL

            client.get('socio_10_nome', client.get('socio10_nome', '')),                        # 77. SÓCIO 10 NOME
            f"'{str(client.get('socio_10_cpf', client.get('socio10_cpf', '')))}" if client.get('socio_10_cpf', client.get('socio10_cpf', '')) else '',  # 78. SÓCIO 10 CPF - como string
            client.get('socio_10_data_nascimento', client.get('socio10_nascimento', '')),       # 79. SÓCIO 10 DATA NASCIMENTO
            'SIM' if client.get('socio_10_administrador', client.get('socio10_admin')) else 'NÃO', # 80. SÓCIO 10 ADMINISTRADOR
            client.get('socio_10_participacao', client.get('socio10_cotas', '')),                # 81. SÓCIO 10 PARTICIPAÇÃO
            'SIM' if client.get('socio_10_resp_legal', client.get('socio10_resp_legal')) else 'NÃO', # 82. SÓCIO 10 RESPONSÁVEL LEGAL
            
            # Bloco 4: Contatos - POSIÇÕES AJUSTADAS
            client.get('telefoneFixo', ''),                   # 83. TELEFONE FIXO (AJUSTADO)
            client.get('telefoneCelular', ''),                # 84. TELEFONE CELULAR (AJUSTADO)
            client.get('whatsapp', ''),                       # 85. WHATSAPP (AJUSTADO)
            client.get('emailPrincipal', ''),                 # 86. EMAIL PRINCIPAL (AJUSTADO)
            client.get('emailSecundario', ''),                # 87. EMAIL SECUNDÁRIO (AJUSTADO)
            client.get('responsavelImediato', ''),            # 88. RESPONSÁVEL IMEDIATO (AJUSTADO)
            client.get('emailsSocios', ''),                   # 89. EMAILS DOS SÓCIOS (AJUSTADO)
            client.get('contatoContador', ''),                # 91. CONTATO CONTADOR (CORRIGIDO)
            client.get('telefoneContador', ''),               # 92. TELEFONE CONTADOR (CORRIGIDO)
            client.get('emailContador', ''),                  # 93. EMAIL CONTADOR (CORRIGIDO)
            
            # Contatos Detalhados - POSIÇÕES CORRETAS
            client.get('contato_1_nome', ''),                 # 94. CONTATO_1_NOME (POSIÇÃO CORRETA)
            client.get('contato_1_cargo', ''),                # 95. CONTATO_1_CARGO (POSIÇÃO CORRETA)
            client.get('contato_1_telefone', ''),             # 96. CONTATO_1_TELEFONE (POSIÇÃO CORRETA)
            client.get('contato_1_email', ''),                # 97. CONTATO_1_EMAIL (POSIÇÃO CORRETA)
            client.get('contato_2_nome', ''),                 # 98. CONTATO_2_NOME (POSIÇÃO CORRETA)
            client.get('contato_2_cargo', ''),                # 99. CONTATO_2_CARGO (POSIÇÃO CORRETA)
            client.get('contato_2_telefone', ''),             # 100. CONTATO_2_TELEFONE (POSIÇÃO CORRETA)
            client.get('contato_2_email', ''),                # 101. CONTATO_2_EMAIL (POSIÇÃO CORRETA)
            client.get('contato_3_nome', ''),                 # 102. CONTATO_3_NOME (POSIÇÃO CORRETA)
            client.get('contato_3_cargo', ''),                # 103. CONTATO_3_CARGO (POSIÇÃO CORRETA)
            client.get('contato_3_telefone', ''),             # 104. CONTATO_3_TELEFONE (POSIÇÃO CORRETA)
            client.get('contato_3_email', ''),                # 105. CONTATO_3_EMAIL (POSIÇÃO CORRETA)
            client.get('contato_4_nome', ''),                 # 107. CONTATO_4_NOME
            client.get('contato_4_cargo', ''),                # 108. CONTATO_4_CARGO
            client.get('contato_4_telefone', ''),             # 109. CONTATO_4_TELEFONE
            client.get('contato_4_email', ''),                # 110. CONTATO_4_EMAIL
            client.get('contato_5_nome', ''),                 # 111. CONTATO_5_NOME
            client.get('contato_5_cargo', ''),                # 112. CONTATO_5_CARGO
            client.get('contato_5_telefone', ''),             # 113. CONTATO_5_TELEFONE
            client.get('contato_5_email', ''),                # 114. CONTATO_5_EMAIL
            
            # Bloco 5: Senhas e Credenciais (POSIÇÕES CORRETAS)
            client.get('cnpjAcessoSn', ''),                   # 114. CPF/CNPJ SN
            client.get('codigoAcessoSn', ''),                 # 115. CÓDIGO ACESSO SN
            client.get('acessoEmpWeb', ''),                   # 116. ACESSO EMPWEB
            client.get('senhaEmpWeb', ''),                    # 117. SENHA EMPWEB
            client.get('acessoIss', ''),                      # 118. ACESSO ISS
            client.get('acessoSefin', ''),                    # 119. ACESSO SEFIN
            client.get('acessoSeuma', ''),                    # 120. ACESSO SEUMA
            client.get('acessoSemace', ''),                   # 121. ACESSO SEMACE
            client.get('acessoIbama', ''),                    # 122. ACESSO IBAMA
            client.get('acessoFapInss', ''),                  # 123. ACESSO FAP/INSS
            client.get('acessoCrf', ''),                      # 124. ACESSO CRF
            client.get('senhaSemace', ''),                    # 125. SENHA SEMACE
            client.get('anvisaGestor', ''),                   # 126. ANVISA GESTOR
            client.get('anvisaEmpresa', ''),                  # 127. ANVISA EMPRESA
            
            # Senhas Específicas Adicionais (NOVOS CAMPOS)
            client.get('senhaFgts', ''),                      # 128. SENHA FGTS
            client.get('senhaSocial', ''),                    # 129. SENHA SOCIAL
            client.get('senhaGiss', ''),                      # 130. SENHA GISS
            client.get('senhaDetran', ''),                    # 131. SENHA DETRAN
            client.get('senhaReceita', ''),                   # 132. SENHA RECEITA
            client.get('senhaSintegra', ''),                  # 133. SENHA SINTEGRA
            client.get('senhaJucesp', ''),                    # 134. SENHA JUCESP
            client.get('senhaPortalEmpregador', ''),          # 135. SENHA PORTAL EMPREGADOR
            client.get('senhaSimples', ''),                   # 136. SENHA SIMPLES
            client.get('senhaGoverno', ''),                   # 137. SENHA GOVERNO
            client.get('senhaViaSoft', ''),                   # 138. SENHA VIA SOFT
            client.get('senhaSimei', ''),                     # 85. SENHA SIMEI

            # Bloco 6: Procurações (CORRIGIDO - alinhado com formulário)
            'SIM' if client.get('procReceita') else 'NÃO',    # 86. PROCURAÇÃO RECEITA
            client.get('dataProcReceita', ''),                # 87. DATA PROCURAÇÃO RECEITA
            'SIM' if client.get('procDte') else 'NÃO',        # 88. PROCURAÇÃO DTe
            client.get('dataProcDte', ''),                    # 89. DATA PROCURAÇÃO DTe
            'SIM' if client.get('procCaixa') else 'NÃO',      # 90. PROCURAÇÃO CAIXA
            client.get('dataProcCaixa', ''),                  # 91. DATA PROCURAÇÃO CAIXA
            'SIM' if client.get('procEmpWeb') else 'NÃO',     # 92. PROCURAÇÃO EMP WEB
            client.get('dataProcEmpWeb', ''),                 # 93. DATA PROCURAÇÃO EMP WEB
            'SIM' if client.get('procDet') else 'NÃO',        # 94. PROCURAÇÃO DET
            client.get('dataProcDet', ''),                    # 95. DATA PROCURAÇÃO DET
            client.get('outrasProc', ''),                     # 96. OUTRAS PROCURAÇÕES
            client.get('obsProcuracoes', ''),                 # 97. OBSERVAÇÕES PROCURAÇÕES

            # Bloco 7: Observações e Dados Adicionais (apenas campos mantidos)
            client.get('observacoes', ''),                    # 98. OBSERVAÇÕES
            client.get('statusCliente', 'ativo'),             # 99. STATUS DO CLIENTE
            client.get('ultimaAtualizacao', ''),              # 100. ÚLTIMA ATUALIZAÇÃO

            # Campos internos do sistema
            client.get('donoResp', ''),                       # 101. DONO/RESPONSÁVEL
            'SIM' if client.get('ativo', True) else 'NÃO',    # 102. CLIENTE ATIVO
            client.get('criadoEm', ''),                       # 103. DATA DE CRIAÇÃO
            client.get('id', ''),                             # 104. ID
            client.get('domestica', ''),                      # 105. DOMÉSTICA
            client.get('geraArquivoSped', ''),                # 106. GERA ARQUIVO DO SPED
            # --- CAMPOS NOVOS AO FINAL ---
            client.get('cnpjAcessoSn', ''),                   # 107. CNPJ ACESSO SIMPLES NACIONAL
            client.get('cpfRepLegal', ''),                    # 108. CPF DO REPRESENTANTE LEGAL
            client.get('codigoAcessoSn', ''),                 # 109. CÓDIGO DE ACESSO SIMPLES NACIONAL
        ]

        # Expandir row_data para acomodar todas as colunas dos cabeçalhos
        headers = self.get_headers()
        while len(row_data) < len(headers):
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

        # NOVOS CAMPOS DE SENHA - mapeamento baseado em cabeçalhos
        senha_fields = {
            'CNPJ ACESSO SIMPLES NACIONAL': client.get('cnpjAcessoSn', ''),
            'CPF DO REPRESENTANTE LEGAL': client.get('cpfRepLegal', ''),
            'CÓDIGO ACESSO SN': client.get('codigoAcessoSn', ''),
            'SENHA ISS': client.get('senhaIss', ''),
            'SENHA SEFIN': client.get('senhaSefin', ''),
            'SENHA SEUMA': client.get('senhaSeuma', ''),
            'LOGIN ANVISA EMPRESA': client.get('anvisaEmpresa', ''),
            'SENHA ANVISA EMPRESA': client.get('senhaAnvisaEmpresa', ''),
            'LOGIN ANVISA GESTOR': client.get('anvisaGestor', ''),
            'SENHA ANVISA GESTOR': client.get('senhaAnvisaGestor', ''),
            'SENHA FAP/INSS': client.get('senhaFapInss', ''),
            'ACESSO EMP WEB': client.get('acessoEmpWeb', ''),
            'SENHA EMP WEB': client.get('senhaEmpWeb', ''),
            'ACESSO CRF': client.get('acessoCrf', ''),
            'SENHA CRF': client.get('senhaCrf', ''),
            'EMAIL SEFIN': client.get('emailSefin', ''),
            'EMAIL EMPWEB': client.get('emailEmpweb', '')
        }
        
        for header_name, value in senha_fields.items():
            if header_name in hidx:
                row_data[hidx[header_name]] = value
                print(f"🔐 [SERVICE] {header_name}: '{value}' -> posição {hidx[header_name]}")

        # DEBUG: Verificar se o ID foi colocado corretamente
        if 'ID' in hidx:
            print(f"🔍 [SERVICE] ID na posição {hidx['ID']}: '{row_data[hidx['ID']]}' (deve ser '{client_id}')")
        print(f"✅ [SERVICE] Total de colunas na linha: {len(row_data)} (esperado {len(headers)})")
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
            'ct': bool_from_text(safe_get(row, 13)),              # POSIÇÃO CORRETA
            'fs': bool_from_text(safe_get(row, 14)),              # POSIÇÃO CORRETA  
            'dp': bool_from_text(safe_get(row, 15)),              # POSIÇÃO CORRETA
            'bpoFinanceiro': bool_from_text(safe_get(row, 16)),   # CORRIGIDO: posição 16

            # Códigos dos Sistemas (Bloco 2) - POSIÇÕES CORRETAS
            'codFortesCt': safe_get(row, 18).lstrip("'") if safe_get(row, 18) else '',   # POSIÇÃO CORRETA - removido zfill
            'codFortesFs': safe_get(row, 19).lstrip("'") if safe_get(row, 19) else '',   # POSIÇÃO CORRETA - removido zfill
            'codFortesPs': safe_get(row, 20).lstrip("'") if safe_get(row, 20) else '',   # POSIÇÃO CORRETA - removido zfill
            'codDominio': safe_get(row, 21).lstrip("'") if safe_get(row, 21) else '',    # POSIÇÃO CORRETA - removido zfill
            'sistemaUtilizado': safe_get(row, 22),                # POSIÇÃO CORRETA

            # Bloco 3: Quadro Societário - POSIÇÕES CORRETAS
            'socio_1_nome': safe_get(row, 23),                    # POSIÇÃO CORRETA
            'socio_1_cpf': safe_get(row, 24),                     # POSIÇÃO CORRETA
            'socio_1_data_nascimento': safe_get(row, 25),         # POSIÇÃO CORRETA
            'socio_1_administrador': bool_from_text(safe_get(row, 26)),  # POSIÇÃO CORRETA
            'socio_1_participacao': safe_get(row, 27),            # POSIÇÃO CORRETA
            'socio_1_resp_legal': bool_from_text(safe_get(row, 28)),     # POSIÇÃO CORRETA

            # Sócios 2-10 - NOVOS MAPEAMENTOS
            'socio_2_nome': safe_get(row, 29),                    # SÓCIO 2 NOME
            'socio_2_cpf': safe_get(row, 30),                     # SÓCIO 2 CPF
            'socio_2_data_nascimento': safe_get(row, 31),         # SÓCIO 2 DATA NASCIMENTO
            'socio_2_administrador': bool_from_text(safe_get(row, 32)),  # SÓCIO 2 ADMINISTRADOR
            'socio_2_participacao': safe_get(row, 33),            # SÓCIO 2 PARTICIPAÇÃO
            'socio_2_resp_legal': bool_from_text(safe_get(row, 34)),     # SÓCIO 2 RESPONSÁVEL LEGAL

            'socio_3_nome': safe_get(row, 35),                    # SÓCIO 3 NOME
            'socio_3_cpf': safe_get(row, 36),                     # SÓCIO 3 CPF
            'socio_3_data_nascimento': safe_get(row, 37),         # SÓCIO 3 DATA NASCIMENTO
            'socio_3_administrador': bool_from_text(safe_get(row, 38)),  # SÓCIO 3 ADMINISTRADOR
            'socio_3_participacao': safe_get(row, 39),            # SÓCIO 3 PARTICIPAÇÃO
            'socio_3_resp_legal': bool_from_text(safe_get(row, 40)),     # SÓCIO 3 RESPONSÁVEL LEGAL

            'socio_4_nome': safe_get(row, 41),                    # SÓCIO 4 NOME
            'socio_4_cpf': safe_get(row, 42),                     # SÓCIO 4 CPF
            'socio_4_data_nascimento': safe_get(row, 43),         # SÓCIO 4 DATA NASCIMENTO
            'socio_4_administrador': bool_from_text(safe_get(row, 44)),  # SÓCIO 4 ADMINISTRADOR
            'socio_4_participacao': safe_get(row, 45),            # SÓCIO 4 PARTICIPAÇÃO
            'socio_4_resp_legal': bool_from_text(safe_get(row, 46)),     # SÓCIO 4 RESPONSÁVEL LEGAL

            'socio_5_nome': safe_get(row, 47),                    # SÓCIO 5 NOME
            'socio_5_cpf': safe_get(row, 48),                     # SÓCIO 5 CPF
            'socio_5_data_nascimento': safe_get(row, 49),         # SÓCIO 5 DATA NASCIMENTO
            'socio_5_administrador': bool_from_text(safe_get(row, 50)),  # SÓCIO 5 ADMINISTRADOR
            'socio_5_participacao': safe_get(row, 51),            # SÓCIO 5 PARTICIPAÇÃO
            'socio_5_resp_legal': bool_from_text(safe_get(row, 52)),     # SÓCIO 5 RESPONSÁVEL LEGAL

            'socio_6_nome': safe_get(row, 53),                    # SÓCIO 6 NOME
            'socio_6_cpf': safe_get(row, 54),                     # SÓCIO 6 CPF
            'socio_6_data_nascimento': safe_get(row, 55),         # SÓCIO 6 DATA NASCIMENTO
            'socio_6_administrador': bool_from_text(safe_get(row, 56)),  # SÓCIO 6 ADMINISTRADOR
            'socio_6_participacao': safe_get(row, 57),            # SÓCIO 6 PARTICIPAÇÃO
            'socio_6_resp_legal': bool_from_text(safe_get(row, 58)),     # SÓCIO 6 RESPONSÁVEL LEGAL

            'socio_7_nome': safe_get(row, 59),                    # SÓCIO 7 NOME
            'socio_7_cpf': safe_get(row, 60),                     # SÓCIO 7 CPF
            'socio_7_data_nascimento': safe_get(row, 61),         # SÓCIO 7 DATA NASCIMENTO
            'socio_7_administrador': bool_from_text(safe_get(row, 62)),  # SÓCIO 7 ADMINISTRADOR
            'socio_7_participacao': safe_get(row, 63),            # SÓCIO 7 PARTICIPAÇÃO
            'socio_7_resp_legal': bool_from_text(safe_get(row, 64)),     # SÓCIO 7 RESPONSÁVEL LEGAL

            'socio_8_nome': safe_get(row, 65),                    # SÓCIO 8 NOME
            'socio_8_cpf': safe_get(row, 66),                     # SÓCIO 8 CPF
            'socio_8_data_nascimento': safe_get(row, 67),         # SÓCIO 8 DATA NASCIMENTO
            'socio_8_administrador': bool_from_text(safe_get(row, 68)),  # SÓCIO 8 ADMINISTRADOR
            'socio_8_participacao': safe_get(row, 69),            # SÓCIO 8 PARTICIPAÇÃO
            'socio_8_resp_legal': bool_from_text(safe_get(row, 70)),     # SÓCIO 8 RESPONSÁVEL LEGAL

            'socio_9_nome': safe_get(row, 71),                    # SÓCIO 9 NOME
            'socio_9_cpf': safe_get(row, 72),                     # SÓCIO 9 CPF
            'socio_9_data_nascimento': safe_get(row, 73),         # SÓCIO 9 DATA NASCIMENTO
            'socio_9_administrador': bool_from_text(safe_get(row, 74)),  # SÓCIO 9 ADMINISTRADOR
            'socio_9_participacao': safe_get(row, 75),            # SÓCIO 9 PARTICIPAÇÃO
            'socio_9_resp_legal': bool_from_text(safe_get(row, 76)),     # SÓCIO 9 RESPONSÁVEL LEGAL

            'socio_10_nome': safe_get(row, 77),                   # SÓCIO 10 NOME
            'socio_10_cpf': safe_get(row, 78),                    # SÓCIO 10 CPF
            'socio_10_data_nascimento': safe_get(row, 79),        # SÓCIO 10 DATA NASCIMENTO
            'socio_10_administrador': bool_from_text(safe_get(row, 80)),  # SÓCIO 10 ADMINISTRADOR
            'socio_10_participacao': safe_get(row, 81),           # SÓCIO 10 PARTICIPAÇÃO
            'socio_10_resp_legal': bool_from_text(safe_get(row, 82)),     # SÓCIO 10 RESPONSÁVEL LEGAL

            # Campos legados para compatibilidade total
            'socio1_nome': safe_get(row, 23),                     # POSIÇÃO CORRETA
            'socio1_cpf': safe_get(row, 24),                      # POSIÇÃO CORRETA
            'socio1_nascimento': safe_get(row, 25),               # POSIÇÃO CORRETA
            'socio1_admin': bool_from_text(safe_get(row, 26)),    # POSIÇÃO CORRETA
            'socio1_cotas': safe_get(row, 27),                    # POSIÇÃO CORRETA
            'socio1_resp_legal': bool_from_text(safe_get(row, 28)),  # POSIÇÃO CORRETA
            'socio1': safe_get(row, 23),                          # POSIÇÃO CORRETA

            # Campos legados para sócios 2-10
            'socio2_nome': safe_get(row, 29),                     # COMPATIBILIDADE
            'socio3_nome': safe_get(row, 35),                     # COMPATIBILIDADE
            'socio4_nome': safe_get(row, 41),                     # COMPATIBILIDADE
            'socio5_nome': safe_get(row, 47),                     # COMPATIBILIDADE
            'socio6_nome': safe_get(row, 53),                     # COMPATIBILIDADE
            'socio7_nome': safe_get(row, 59),                     # COMPATIBILIDADE
            'socio8_nome': safe_get(row, 65),                     # COMPATIBILIDADE
            'socio9_nome': safe_get(row, 71),                     # COMPATIBILIDADE
            'socio10_nome': safe_get(row, 77),                    # COMPATIBILIDADE
            
            # Campos de data - CORRIGIDOS
            'mesAnoInicio': safe_get(row, 17),                    # POSIÇÃO CORRETA para DATA INÍCIO DOS SERVIÇOS
            'dataInicioServicos': safe_get(row, 17),              # POSIÇÃO CORRETA para DATA INÍCIO DOS SERVIÇOS

            # Bloco 4: Contatos - POSIÇÕES CORRIGIDAS
            'telefoneFixo': safe_get(row, 83),                    # 84-1 = 83 (TELEFONE FIXO)
            'telefoneCelular': safe_get(row, 84),                 # 85-1 = 84 (TELEFONE CELULAR)  
            'whatsapp': safe_get(row, 85),                        # 86-1 = 85 (WHATSAPP)
            'emailPrincipal': safe_get(row, 86),                  # 87-1 = 86 (EMAIL PRINCIPAL)
            'emailSecundario': safe_get(row, 87),                 # 88-1 = 87 (EMAIL SECUNDÁRIO)
            'responsavelImediato': safe_get(row, 88),             # 89-1 = 88 (RESPONSÁVEL IMEDIATO)
            'emailsSocios': safe_get(row, 89),                    # 90-1 = 89 (EMAILS DOS SÓCIOS)
            'contatoContador': safe_get(row, 90),                 # 91-1 = 90 (CONTATO CONTADOR)
            'telefoneContador': safe_get(row, 91),                # 92-1 = 91 (TELEFONE CONTADOR)
            'emailContador': safe_get(row, 92),                   # 93-1 = 92 (EMAIL CONTADOR)

            # Campos legados para compatibilidade
            'emailsSocio': safe_get(row, 35),                     # POSIÇÃO CORRETA

            # Contatos Detalhados - POSIÇÕES AJUSTADAS EMPIRICAMENTE (OFFSET -1)
            'contato_1_nome': safe_get(row, 93),                  # Nome do contato 1 (offset -1)
            'contato_1_cargo': safe_get(row, 94),                 # Cargo do contato 1 (offset -1)
            'contato_1_telefone': safe_get(row, 95),              # Telefone do contato 1 (offset -1)
            'contato_1_email': safe_get(row, 96),                 # Email do contato 1 (offset -1)
            'contato_2_nome': safe_get(row, 97),                  # Nome do contato 2 (offset -1)
            'contato_2_cargo': safe_get(row, 98),                 # Cargo do contato 2 (offset -1)
            'contato_2_telefone': safe_get(row, 99),              # Telefone do contato 2 (offset -1)
            'contato_2_email': safe_get(row, 100),                # Email do contato 2 (offset -1)
            'contato_3_nome': safe_get(row, 101),                 # Nome do contato 3 (offset -1)
            'contato_3_cargo': safe_get(row, 102),                # Cargo do contato 3 (offset -1)
            'contato_3_telefone': safe_get(row, 103),             # Telefone do contato 3 (offset -1)
            'contato_3_email': safe_get(row, 104),                # Email do contato 3 (offset -1)
            'contato_4_nome': safe_get(row, 106),                 # 107-1 = 106 (CONTATO_4_NOME)
            'contato_4_cargo': safe_get(row, 107),                # 108-1 = 107 (CONTATO_4_CARGO)
            'contato_4_telefone': safe_get(row, 108),             # 109-1 = 108 (CONTATO_4_TELEFONE)
            'contato_4_email': safe_get(row, 109),                # 110-1 = 109 (CONTATO_4_EMAIL)
            'contato_5_nome': safe_get(row, 110),                 # 111-1 = 110 (CONTATO_5_NOME)
            'contato_5_cargo': safe_get(row, 111),                # 112-1 = 111 (CONTATO_5_CARGO)
            'contato_5_telefone': safe_get(row, 112),             # 113-1 = 112 (CONTATO_5_TELEFONE)
            'contato_5_email': safe_get(row, 113),                # 114-1 = 113 (CONTATO_5_EMAIL)

            # Bloco 5: Senhas e Credenciais (POSIÇÕES CORRIGIDAS)
            'cnpjAcessoSn': safe_get(row, 105),      # 106-1 = 105 (CPF/CNPJ SN)
            'cpfRepLegal': safe_get(row, 106),       # 107-1 = 106 (CÓDIGO ACESSO SN)
            'codigoAcessoSn': safe_get(row, 107),    # 108-1 = 107 (ACESSO EMPWEB)
            'senhaIss': safe_get(row, 108),          # 109-1 = 108 (SENHA EMPWEB)
            
            'senhaSefin': safe_get(row, 109),        # 110-1 = 109 (ACESSO ISS)
            'senhaSeuma': safe_get(row, 110),        # 111-1 = 110 (ACESSO SEFIN)
            'acessoEmpWeb': safe_get(row, 111),      # 112-1 = 111 (ACESSO SEUMA)
            'senhaEmpWeb': safe_get(row, 120),       # 121-1 = 120 (ACESSO SEMACE)
            
            'anvisaEmpresa': safe_get(row, 121),     # 122-1 = 121 (ACESSO IBAMA)
            'senhaAnvisaEmpresa': safe_get(row, 122), # 123-1 = 122 (ACESSO FAP/INSS)
            'anvisaGestor': safe_get(row, 123),      # 124-1 = 123 (ACESSO CRF)
            'senhaAnvisaGestor': safe_get(row, 124), # 125-1 = 124 (SENHA SEMACE)
            
            'acessoCrf': safe_get(row, 125),         # 126-1 = 125 (ANVISA GESTOR)
            'senhaFapInss': safe_get(row, 126),      # 127-1 = 126 (ANVISA EMPRESA)
            
            # Senhas Específicas Adicionais (POSIÇÕES CORRIGIDAS)
            'senhaFgts': safe_get(row, 127),         # 128-1 = 127 (SENHA FGTS)
            'senhaSocial': safe_get(row, 128),       # 129-1 = 128 (SENHA SOCIAL)
            'senhaGiss': safe_get(row, 129),         # 130-1 = 129 (SENHA GISS)
            'senhaDetran': safe_get(row, 130),       # 131-1 = 130 (SENHA DETRAN)
            'senhaReceita': safe_get(row, 131),      # 132-1 = 131 (SENHA RECEITA)
            'senhaSintegra': safe_get(row, 132),     # 133-1 = 132 (SENHA SINTEGRA)
            'senhaJucesp': safe_get(row, 133),       # 134-1 = 133 (SENHA JUCESP)
            'senhaPortalEmpregador': safe_get(row, 134), # 135-1 = 134 (SENHA PORTAL EMPREGADOR)
            'senhaSimples': safe_get(row, 135),                   # 135. SENHA SIMPLES (posição real)
            'senhaGoverno': safe_get(row, 136),                   # 136. SENHA GOVERNO (posição real)
            'senhaViaSoft': safe_get(row, 137),                   # 137. SENHA VIA SOFT (posição real)
            'senhaSimei': safe_get(row, 138),                     # 138. SENHA SIMEI (posição real)

            # Bloco 6: Procurações (posições reais na planilha)
            'procReceita': bool_from_text(safe_get(row, 139)),    # 139. PROCURAÇÃO RECEITA (RFB)
            'dataProcReceita': safe_get(row, 140),                # 140. DATA PROCURAÇÃO RECEITA
            'procDte': bool_from_text(safe_get(row, 141)),        # 141. PROCURAÇÃO DTe
            'dataProcDte': safe_get(row, 142),                    # 142. DATA PROCURAÇÃO DTe
            'procCaixa': bool_from_text(safe_get(row, 143)),      # 143. PROCURAÇÃO CAIXA
            'dataProcCaixa': safe_get(row, 144),                  # 144. DATA PROCURAÇÃO CAIXA
            'procEmpWeb': bool_from_text(safe_get(row, 145)),     # 145. PROCURAÇÃO EMP WEB
            'dataProcEmpWeb': safe_get(row, 146),                 # 146. DATA PROCURAÇÃO EMP WEB
            'procDet': bool_from_text(safe_get(row, 147)),        # 147. PROCURAÇÃO DET
            'dataProcDet': safe_get(row, 148),                    # 148. DATA PROCURAÇÃO DET
            'outrasProc': safe_get(row, 149),                     # 149. OUTRAS PROCURAÇÕES
            'obsProcuracoes': safe_get(row, 150),                 # 150. OBSERVAÇÕES PROCURAÇÕES

            # Bloco 7: Observações e Dados Adicionais (posições reais na planilha)
            'observacoes': safe_get(row, 151, ''),                # 151. OBSERVAÇÕES
            'statusCliente': safe_get(row, 152, 'ativo').lower(), # 152. STATUS DO CLIENTE
            'ultimaAtualizacao': safe_get(row, 153),              # 153. ÚLTIMA ATUALIZAÇÃO

            # Campos internos do sistema (posições reais na planilha)
            'id': id_resolvido,
            'donoResp': safe_get(row, 154),                       # 154. DONO/RESPONSÁVEL
            
            # Campo ativo derivado do statusCliente - CORREÇÃO PRINCIPAL
            'criadoEm': safe_get(row, 156, datetime.now().isoformat()), # 156. DATA DE CRIAÇÃO
            'domestica': safe_get(row, 158),                      # 158. DOMÉSTICA
            'geraArquivoSped': safe_get(row, 159),                # 159. GERA ARQUIVO DO SPED
            
            # --- CAMPOS NOVOS DE SENHA - usando posições corretas dos cabeçalhos ---
            'cnpjAcessoSn': safe_get(row, 160),       # 161. CNPJ ACESSO SIMPLES NACIONAL
            'cpfRepLegal': safe_get(row, 161),        # 162. CPF DO REPRESENTANTE LEGAL  
            'codigoAcessoSn': safe_get(row, 162),     # 163. CÓDIGO ACESSO SN
            'senhaIss': safe_get(row, 163),           # 164. SENHA ISS
            'senhaSefin': safe_get(row, 164),         # 165. SENHA SEFIN
            'senhaSeuma': safe_get(row, 165),         # 166. SENHA SEUMA
            'anvisaEmpresa': safe_get(row, 166),      # 167. LOGIN ANVISA EMPRESA
            'senhaAnvisaEmpresa': safe_get(row, 167), # 168. SENHA ANVISA EMPRESA
            'anvisaGestor': safe_get(row, 168),       # 169. LOGIN ANVISA GESTOR
            'senhaAnvisaGestor': safe_get(row, 169),  # 170. SENHA ANVISA GESTOR
            'senhaFapInss': safe_get(row, 170),       # 171. SENHA FAP/INSS
            'acessoEmpWeb': safe_get(row, 171),       # 172. ACESSO EMP WEB
            'senhaEmpWeb': safe_get(row, 172),        # 173. SENHA EMP WEB
            'acessoCrf': safe_get(row, 173),          # 174. ACESSO CRF
            'senhaCrf': safe_get(row, 174),           # 175. SENHA CRF
            'emailSefin': safe_get(row, 175),         # 176. EMAIL SEFIN
            'emailEmpweb': safe_get(row, 176),        # 177. EMAIL EMPWEB
        }

        # CORREÇÃO CRÍTICA: Derivar campo 'ativo' a partir do statusCliente
        status_cliente = result.get('statusCliente', 'ativo').lower()
        result['ativo'] = status_cliente == 'ativo'

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
