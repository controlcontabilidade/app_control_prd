import os
import json
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
                credentials_info = json.loads(service_account_json)
                credentials = Credentials.from_service_account_info(
                    credentials_info, scopes=self.scopes
                )
            else:
                # Fallback para arquivo local (desenvolvimento)
                current_dir = os.path.dirname(os.path.dirname(__file__))
                credentials_file = os.path.join(current_dir, 'service-account-key.json')
                print(f"� Procurando credenciais em: {credentials_file}")
                
                if not os.path.exists(credentials_file):
                    raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {credentials_file}")
                    
                credentials = Credentials.from_service_account_file(
                    credentials_file, scopes=self.scopes
                )
            
            print("🔐 Autenticando com Service Account...")
            self.service = build('sheets', 'v4', credentials=credentials)
            print("✅ Autenticação Service Account concluída!")
            
        except Exception as e:
            print(f"❌ Erro na autenticação Service Account: {e}")
            raise
    
    def save_client(self, client: Dict) -> bool:
        """Salva ou atualiza cliente no Google Sheets"""
        try:
            print(f"🔍 [SERVICE] Processando cliente '{client.get('nomeEmpresa')}'...")
            print(f"🔍 [SERVICE] ID do cliente: {client.get('id')}")
            print(f"🔍 [SERVICE] Dados recebidos: {list(client.keys())}")
            
            # Se tem ID, é uma atualização
            if client.get('id'):
                print("🔍 [SERVICE] Tipo: ATUALIZAÇÃO")
                return self.update_client(client)
            else:
                print("🔍 [SERVICE] Tipo: NOVO CLIENTE")
                # Gerar ID se não existir
                client['id'] = str(int(datetime.now().timestamp()))
                client['criadoEm'] = datetime.now().isoformat()
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
        """Atualiza cliente existente na planilha"""
        try:
            print(f"✏️ [SERVICE] Atualizando cliente ID: {client.get('id')}")
            
            # Validação básica
            if not client.get('id'):
                print("❌ [SERVICE] ID do cliente é obrigatório para atualização")
                return False
                
            if not client.get('nomeEmpresa'):
                print("❌ [SERVICE] Nome da empresa é obrigatório")
                return False
            
            # Buscar a linha do cliente
            print("🔍 [SERVICE] Buscando linha do cliente...")
            row_index = self.find_client_row(client.get('id'))
            print(f"🔍 [SERVICE] Linha encontrada: {row_index}")
            
            if row_index == -1:
                print("⚠️ [SERVICE] Cliente não encontrado, adicionando como novo...")
                return self.add_new_client(client)
            
            # Atualizar dados do cliente (manter criadoEm original se não existir)
            if not client.get('criadoEm'):
                print("🔍 [SERVICE] Buscando criadoEm original...")
                try:
                    existing_client = self.get_client(client.get('id'))
                    if existing_client:
                        client['criadoEm'] = existing_client.get('criadoEm', datetime.now().isoformat())
                        print(f"🔍 [SERVICE] CriadoEm encontrado: {client['criadoEm']}")
                    else:
                        client['criadoEm'] = datetime.now().isoformat()
                        print(f"🔍 [SERVICE] Usando criadoEm atual: {client['criadoEm']}")
                except Exception as e:
                    print(f"⚠️ [SERVICE] Erro ao buscar criadoEm original: {e}")
                    client['criadoEm'] = datetime.now().isoformat()
            
            # Preparar dados para atualização
            print("🔍 [SERVICE] Convertendo cliente para linha...")
            try:
                row_data = self.client_to_row(client)
                print(f"🔍 [SERVICE] Linha preparada com {len(row_data)} colunas")
                
                if len(row_data) < 55:
                    print(f"⚠️ [SERVICE] Linha tem menos colunas que esperado: {len(row_data)}")
                    
            except Exception as e:
                print(f"❌ [SERVICE] Erro ao converter cliente para linha: {e}")
                return False
            
            range_name = f'Clientes!A{row_index}:CZ{row_index}'
            print(f"🔍 [SERVICE] Range para atualização: {range_name}")
            
            body = {'values': [row_data]}
            
            print("🔍 [SERVICE] Enviando atualização para Google Sheets...")
            try:
                result = self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption='USER_ENTERED',
                    body=body
                ).execute()
                
                print(f"✅ [SERVICE] Cliente atualizado na linha {row_index}")
                print(f"🔍 [SERVICE] Resultado: {result.get('updatedCells', 0)} células atualizadas")
                return True
                
            except Exception as api_error:
                print(f"❌ [SERVICE] Erro na API do Google Sheets durante atualização: {api_error}")
                if "RATE_LIMIT_EXCEEDED" in str(api_error):
                    print("⚠️ Rate limit excedido durante atualização")
                return False
            
        except Exception as e:
            print(f"❌ [SERVICE] Erro geral ao atualizar cliente: {e}")
            import traceback
            print(f"❌ [SERVICE] Traceback: {traceback.format_exc()}")
            return False
    
    def find_client_row(self, client_id: str) -> int:
        """Encontra a linha do cliente na planilha - MÉTODO MELHORADO"""
        try:
            print(f"🔍 [SERVICE] Buscando linha para cliente ID: '{client_id}'")
            
            if not client_id or str(client_id).strip() == '':
                print("⚠️ [SERVICE] ID do cliente está vazio!")
                return -1
            
            # Normalizar o ID para busca
            search_id = str(client_id).strip()
            print(f"🔍 [SERVICE] ID normalizado para busca: '{search_id}'")
            
            # Buscar todos os dados para ter mais controle
            try:
                result = self.service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id,
                    range='Clientes!A1:CZ'  # Buscar todos os dados
                ).execute()
            except Exception as api_error:
                print(f"❌ [SERVICE] Erro na API do Google Sheets: {api_error}")
                if "RATE_LIMIT_EXCEEDED" in str(api_error):
                    print("⚠️ Rate limit excedido. Aguardando e tentando novamente...")
                    import time
                    time.sleep(2)  # Aguardar 2 segundos
                    return self._find_client_fallback(client_id)
                raise api_error
            
            values = result.get('values', [])
            print(f"🔍 [SERVICE] Planilha tem {len(values)} linhas no total")
            
            if len(values) <= 1:  # Só header ou vazio
                print("⚠️ [SERVICE] Planilha vazia ou só com cabeçalho")
                return -1
            
            # Encontrar a coluna do ID - deve ser coluna 90 (índice 89)
            headers = values[0] if values else []
            id_column_index = -1
            
            # Procurar pela coluna 'ID' ou 'id'
            for i, header in enumerate(headers):
                if str(header).strip().upper() == 'ID':
                    id_column_index = i
                    print(f"🔍 [SERVICE] Coluna ID encontrada no índice {i}")
                    break
            
            if id_column_index == -1:
                # Assumir que é a última coluna (padrão SIGEC)
                id_column_index = 89  # Posição padrão do ID no SIGEC
                print(f"🔍 [SERVICE] Usando posição padrão do ID: índice {id_column_index}")
            
            # Percorrer as linhas procurando o ID
            for row_num, row in enumerate(values[1:], start=2):  # Start from row 2 (skip header)
                if len(row) > id_column_index:
                    row_id = str(row[id_column_index]).strip()
                    print(f"🔍 [SERVICE] Linha {row_num}: ID '{row_id}' vs busca '{search_id}'")
                    
                    if row_id == search_id:
                        print(f"✅ [SERVICE] Cliente encontrado na linha {row_num}")
                        return row_num
                else:
                    print(f"🔍 [SERVICE] Linha {row_num}: sem coluna ID (só {len(row)} colunas)")
            
            print(f"⚠️ [SERVICE] Cliente ID '{search_id}' não encontrado na planilha")
            return -1  # Não encontrado
            
        except Exception as e:
            print(f"❌ [SERVICE] Erro ao buscar linha do cliente: {e}")
            import traceback
            print(f"❌ [SERVICE] Traceback: {traceback.format_exc()}")
            return -1
            
    def _find_client_fallback(self, client_id: str) -> int:
        """Método alternativo para encontrar cliente em caso de problemas com a API"""
        try:
            print(f"🔍 [SERVICE] Usando busca alternativa para ID: {client_id}")
            
            # Buscar todos os dados da planilha (limitado)
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Clientes!A1:CZ100'  # Limitando a 100 linhas para evitar rate limit
            ).execute()
            
            values = result.get('values', [])
            
            for i, row in enumerate(values):
                if i == 0:  # Pular cabeçalho
                    continue
                    
                if len(row) >= 90:  # Garantir que tem a coluna ID (posição 89, 0-indexed)
                    row_id = str(row[89]).strip() if len(row) > 89 else ''
                    if row_id == str(client_id).strip():
                        print(f"✅ [SERVICE] Cliente encontrado na linha {i + 1} (busca alternativa)")
                        return i + 1
            
            print(f"⚠️ [SERVICE] Cliente não encontrado na busca alternativa")
            return -1
            
        except Exception as e:
            print(f"❌ [SERVICE] Erro na busca alternativa: {e}")
            return -1
            import traceback
            print(f"❌ [SERVICE] Traceback: {traceback.format_exc()}")
            return -1
    
    def get_clients(self) -> List[Dict]:
        """Busca clientes da planilha"""
        try:
            print("📊 Buscando clientes do Google Sheets...")
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=self.range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                print("📝 Nenhum cliente encontrado na planilha")
                return []
            
            clients = []
            for i, row in enumerate(values[1:], 2):  # Skip header, start from row 2
                if len(row) > 0 and row[0]:  # Check if first column (ID) has value
                    client = self.row_to_client(row)
                    client['_row_number'] = i  # Store row number for updates/deletes
                    clients.append(client)
            
            print(f"📊 {len(clients)} clientes carregados do Google Sheets")
            return clients
            
        except Exception as e:
            print(f"❌ Erro ao buscar clientes: {e}")
            # Se é erro de rate limit, retorna lista vazia em vez de falhar
            if "RATE_LIMIT_EXCEEDED" in str(e):
                print("⚠️ Rate limit excedido. Aguarde 1 minuto antes de tentar novamente.")
            return []
    
    def get_client(self, client_id: str) -> Optional[Dict]:
        """Busca cliente específico"""
        try:
            print(f"🔍 [SERVICE] Buscando cliente específico: {client_id}")
            # Usar find_client_row diretamente em vez de carregar todos os clientes
            row_index = self.find_client_row(client_id)
            if row_index == -1:
                print(f"⚠️ [SERVICE] Cliente {client_id} não encontrado")
                return None
            
            # Buscar apenas a linha específica
            range_name = f"Clientes!A{row_index}:BC{row_index}"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if values and len(values[0]) > 0:
                client = self.row_to_client(values[0])
                client['_row_number'] = row_index
                print(f"✅ [SERVICE] Cliente {client_id} encontrado na linha {row_index}")
                return client
            
            return None
            
        except Exception as e:
            print(f"❌ [SERVICE] Erro ao buscar cliente {client_id}: {e}")
            if "RATE_LIMIT_EXCEEDED" in str(e):
                print("⚠️ Rate limit excedido. Operação cancelada.")
            return None
    
    def delete_client(self, client_id: str) -> bool:
        """Remove cliente da planilha (exclusão real)"""
        try:
            print(f"🗑️ Deletando cliente ID: {client_id}")
            
            # Buscar a linha do cliente
            row_index = self.find_client_row(client_id)
            if row_index == -1:
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
    
    def update_client(self, client: Dict) -> bool:
        """Atualiza cliente existente"""
        try:
            if not client.get('_row_number'):
                # Se não tem número da linha, tenta encontrar pela ID
                existing_client = self.get_client(client.get('id'))
                if not existing_client:
                    print(f"⚠️ [SERVICE] Cliente {client.get('id')} não encontrado para atualização")
                    return False  # Retorna False em vez de criar loop infinito
                client['_row_number'] = existing_client['_row_number']
            
            row_data = self.client_to_row(client)
            range_name = f"Clientes!A{client['_row_number']}:BC{client['_row_number']}"
            
            body = {'values': [row_data]}
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            print(f"✅ Cliente atualizado! Células atualizadas: {result.get('updatedCells', 0)}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar cliente: {e}")
            return False
    
    def get_headers(self) -> List[str]:
        """Retorna os cabeçalhos das colunas na ordem correta conforme SIGEC"""
        return [
            # Bloco 1: Informações da Pessoa Jurídica (13 campos obrigatórios)
            'NOME DA EMPRESA',                    # 1. Obrigatório
            'RAZÃO SOCIAL NA RECEITA',            # 2. Obrigatório
            'NOME FANTASIA NA RECEITA',           # 3. Opcional
            'CNPJ',                              # 4. Obrigatório
            'PERFIL',                            # 5. Obrigatório (MEI, ME, EPP, NORMAL)
            'INSCRIÇÃO ESTADUAL',                # 6. Opcional
            'INSCRIÇÃO MUNICIPAL',               # 7. Opcional
            'ESTADO',                            # 8. Obrigatório
            'CIDADE',                            # 9. Obrigatório
            'REGIME FEDERAL',                    # 10. Obrigatório (SIMPLES, PRESUMIDO, REAL)
            'REGIME ESTADUAL',                   # 11. Opcional
            'SEGMENTO',                          # 12. Obrigatório
            'ATIVIDADE',                         # 13. Obrigatório
            
            # Bloco 2: Serviços Prestados pela Control
            'SERVIÇO CT',                        # 14. Contabilidade (SIM/NÃO)
            'SERVIÇO FS',                        # 15. Fiscal (SIM/NÃO)
            'SERVIÇO DP',                        # 16. Departamento Pessoal (SIM/NÃO)
            'SERVIÇO BPO FINANCEIRO',            # 17. BPO Financeiro (SIM/NÃO)
            'RESPONSÁVEL PELOS SERVIÇOS',        # 18. Nome do responsável
            'DATA INÍCIO DOS SERVIÇOS',          # 19. Data de início
            
            # Códigos dos Sistemas (Bloco 2)
            'CÓDIGO FORTES CT',                  # 20. Código Fortes Contabilidade
            'CÓDIGO FORTES FS',                  # 21. Código Fortes Fiscal
            'CÓDIGO FORTES PS',                  # 22. Código Fortes Folha
            'CÓDIGO DOMÍNIO',                    # 23. Código sistema Domínio
            'SISTEMA UTILIZADO',                 # 24. Sistema principal
            'MÓDULO SPED TRIER',                 # 25. Módulo SPED
            
            # Bloco 3: Quadro Societário (campos base + dinâmicos)
            'SÓCIO 1 NOME',                      # 26. Nome do sócio 1
            'SÓCIO 1 CPF',                       # 27. CPF do sócio 1
            'SÓCIO 1 DATA NASCIMENTO',           # 28. Data nascimento sócio 1
            'SÓCIO 1 ADMINISTRADOR',             # 29. É administrador? (SIM/NÃO)
            'SÓCIO 1 COTAS',                     # 30. Quantidade de cotas
            'SÓCIO 1 RESPONSÁVEL LEGAL',         # 31. É responsável legal? (SIM/NÃO)
            
            # Bloco 4: Contatos
            'TELEFONE FIXO',                     # 32. Telefone fixo da empresa
            'TELEFONE CELULAR',                  # 33. Telefone celular
            'WHATSAPP',                          # 34. WhatsApp
            'EMAIL PRINCIPAL',                   # 35. Email principal (obrigatório)
            'EMAIL SECUNDÁRIO',                  # 36. Email secundário
            'RESPONSÁVEL IMEDIATO',              # 37. Nome do responsável
            'EMAILS DOS SÓCIOS',                 # 38. Lista de emails dos sócios
            'CONTATO CONTADOR',                  # 39. Nome do contador responsável
            'TELEFONE CONTADOR',                 # 40. Telefone do contador
            'EMAIL CONTADOR',                    # 41. Email do contador
            
            # Bloco 5: Sistemas e Acessos
            'SISTEMA PRINCIPAL',                 # 42. Sistema principal utilizado
            'VERSÃO DO SISTEMA',                 # 43. Versão do sistema
            'CÓDIGO ACESSO SIMPLES NACIONAL',    # 44. Código acesso SN
            'CPF/CNPJ PARA ACESSO',             # 45. CPF/CNPJ usado nos acessos
            'PORTAL CLIENTE ATIVO',              # 46. Portal ativo? (SIM/NÃO)
            'INTEGRAÇÃO DOMÍNIO',                # 47. Integrado? (SIM/NÃO)
            'SISTEMA ONVIO',                     # 48. Usa Onvio? (SIM/NÃO)
            
            # Bloco 6: Senhas e Credenciais
            'ACESSO ISS',                        # 49. Login ISS
            'SENHA ISS',                         # 50. Senha ISS
            'ACESSO SEFIN',                      # 51. Login SEFIN
            'SENHA SEFIN',                       # 52. Senha SEFIN
            'ACESSO SEUMA',                      # 53. Login SEUMA
            'SENHA SEUMA',                       # 54. Senha SEUMA
            'ACESSO EMPWEB',                     # 55. Login EmpWeb
            'SENHA EMPWEB',                      # 56. Senha EmpWeb
            'ACESSO FAP/INSS',                   # 57. Login FAP/INSS
            'SENHA FAP/INSS',                    # 58. Senha FAP/INSS
            'ACESSO CRF',                        # 59. Login CRF
            'SENHA CRF',                         # 60. Senha CRF
            'EMAIL GESTOR',                      # 61. Email do gestor
            'SENHA EMAIL GESTOR',                # 62. Senha email gestor
            'ANVISA GESTOR',                     # 63. Login ANVISA Gestor
            'ANVISA EMPRESA',                    # 64. Login ANVISA Empresa
            'ACESSO IBAMA',                      # 65. Login IBAMA
            'SENHA IBAMA',                       # 66. Senha IBAMA
            'ACESSO SEMACE',                     # 67. Login SEMACE
            'SENHA SEMACE',                      # 68. Senha SEMACE
            
            # Bloco 7: Procurações
            'PROCURAÇÃO RFB',                    # 69. Tem proc. RFB? (SIM/NÃO)
            'DATA PROCURAÇÃO RFB',               # 70. Data da procuração RFB
            'PROCURAÇÃO RECEITA ESTADUAL',       # 71. Tem proc. RC? (SIM/NÃO)
            'DATA PROCURAÇÃO RC',                # 72. Data da procuração RC
            'PROCURAÇÃO CAIXA ECONÔMICA',        # 73. Tem proc. CX? (SIM/NÃO)
            'DATA PROCURAÇÃO CX',                # 74. Data da procuração CX
            'PROCURAÇÃO PREVIDÊNCIA SOCIAL',     # 75. Tem proc. SW? (SIM/NÃO)
            'DATA PROCURAÇÃO SW',                # 76. Data da procuração SW
            'PROCURAÇÃO MUNICIPAL',              # 77. Tem proc. Municipal? (SIM/NÃO)
            'DATA PROCURAÇÃO MUNICIPAL',         # 78. Data da procuração Municipal
            'OUTRAS PROCURAÇÕES',                # 79. Outras procurações
            'OBSERVAÇÕES PROCURAÇÕES',           # 80. Observações das procurações
            
            # Bloco 8: Observações e Dados Adicionais
            'OBSERVAÇÕES GERAIS',                # 81. Observações gerais
            'TAREFAS VINCULADAS',                # 82. Número de tarefas
            'DATA INÍCIO SERVIÇOS',              # 83. Data início serviços
            'STATUS DO CLIENTE',                 # 84. Status (ATIVO, INATIVO, etc.)
            'ÚLTIMA ATUALIZAÇÃO',                # 85. Timestamp última atualização
            'RESPONSÁVEL ATUALIZAÇÃO',           # 86. Usuário que atualizou
            'PRIORIDADE',                        # 87. Prioridade (NORMAL, ALTA, etc.)
            'TAGS/CATEGORIAS',                   # 88. Tags do cliente
            'HISTÓRICO DE ALTERAÇÕES',           # 89. Log de alterações
            
            # Campos internos do sistema
            'ID',                                # 90. ID único do cliente
            'CLIENTE ATIVO',                     # 91. Cliente ativo? (SIM/NÃO)
            'DATA DE CRIAÇÃO',                   # 92. Data de criação do registro
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
            if "RATE_LIMIT_EXCEEDED" in str(e):
                print("⚠️ Rate limit excedido na verificação de cabeçalhos - Continuando mesmo assim")
                # Não falhar por causa do rate limit na inicialização
                return
            else:
                print(f"❌ Erro ao verificar/atualizar cabeçalhos: {e}")
                # Não fazer raise para não quebrar a inicialização

    def client_to_row(self, client: Dict) -> List:
        """Converte cliente para linha da planilha - SIGEC organizado por blocos"""
        return [
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
            client.get('responsavelServicos', ''),            # 18. RESPONSÁVEL PELOS SERVIÇOS
            client.get('dataInicioServicos', ''),             # 19. DATA INÍCIO DOS SERVIÇOS
            
            # Códigos dos Sistemas (Bloco 2)
            client.get('codFortesCt', ''),                    # 20. CÓDIGO FORTES CT
            client.get('codFortesFs', ''),                    # 21. CÓDIGO FORTES FS
            client.get('codFortesPs', ''),                    # 22. CÓDIGO FORTES PS
            client.get('codDominio', ''),                     # 23. CÓDIGO DOMÍNIO
            client.get('sistemaUtilizado', ''),               # 24. SISTEMA UTILIZADO
            client.get('moduloSpedTrier', ''),                # 25. MÓDULO SPED TRIER
            
            # Bloco 3: Quadro Societário (campos base + dinâmicos)
            client.get('socio1_nome', client.get('socio1', '')),     # 26. SÓCIO 1 NOME
            client.get('socio1_cpf', ''),                            # 27. SÓCIO 1 CPF
            client.get('socio1_nascimento', ''),                     # 28. SÓCIO 1 DATA NASCIMENTO
            'SIM' if client.get('socio1_admin') else 'NÃO',         # 29. SÓCIO 1 ADMINISTRADOR
            client.get('socio1_cotas', ''),                          # 30. SÓCIO 1 COTAS
            'SIM' if client.get('socio1_resp_legal') else 'NÃO',     # 31. SÓCIO 1 RESPONSÁVEL LEGAL
            
            # Bloco 4: Contatos
            client.get('telefoneFixo', ''),                   # 32. TELEFONE FIXO
            client.get('telefoneCelular', ''),                # 33. TELEFONE CELULAR
            client.get('whatsapp', ''),                       # 34. WHATSAPP
            client.get('emailPrincipal', ''),                 # 35. EMAIL PRINCIPAL
            client.get('emailSecundario', ''),                # 36. EMAIL SECUNDÁRIO
            client.get('responsavelImediato', ''),            # 37. RESPONSÁVEL IMEDIATO
            client.get('emailsSocios', ''),                   # 38. EMAILS DOS SÓCIOS
            client.get('contatoContador', ''),                # 39. CONTATO CONTADOR
            client.get('telefoneContador', ''),               # 40. TELEFONE CONTADOR
            client.get('emailContador', ''),                  # 41. EMAIL CONTADOR
            
            # Bloco 5: Sistemas e Acessos
            client.get('sistemaPrincipal', ''),               # 42. SISTEMA PRINCIPAL
            client.get('versaoSistema', ''),                  # 43. VERSÃO DO SISTEMA
            client.get('codAcessoSimples', ''),               # 44. CÓDIGO ACESSO SIMPLES NACIONAL
            client.get('cpfCnpjAcesso', ''),                  # 45. CPF/CNPJ PARA ACESSO
            'SIM' if client.get('portalClienteAtivo') else 'NÃO',    # 46. PORTAL CLIENTE ATIVO
            'SIM' if client.get('integracaoDominio') else 'NÃO',     # 47. INTEGRAÇÃO DOMÍNIO
            'SIM' if client.get('sistemaOnvio') else 'NÃO',          # 48. SISTEMA ONVIO
            
            # Bloco 6: Senhas e Credenciais
            client.get('acessoIss', ''),                      # 49. ACESSO ISS
            client.get('senhaIss', ''),                       # 50. SENHA ISS
            client.get('acessoSefin', ''),                    # 51. ACESSO SEFIN
            client.get('senhaSefin', ''),                     # 52. SENHA SEFIN
            client.get('acessoSeuma', ''),                    # 53. ACESSO SEUMA
            client.get('senhaSeuma', ''),                     # 54. SENHA SEUMA
            client.get('acessoEmpWeb', ''),                   # 55. ACESSO EMPWEB
            client.get('senhaEmpWeb', ''),                    # 56. SENHA EMPWEB
            client.get('acessoFapInss', ''),                  # 57. ACESSO FAP/INSS
            client.get('senhaFapInss', ''),                   # 58. SENHA FAP/INSS
            client.get('acessoCrf', ''),                      # 59. ACESSO CRF
            client.get('senhaCrf', ''),                       # 60. SENHA CRF
            client.get('emailGestor', ''),                    # 61. EMAIL GESTOR
            client.get('senhaEmailGestor', ''),               # 62. SENHA EMAIL GESTOR
            client.get('anvisaGestor', ''),                   # 63. ANVISA GESTOR
            client.get('anvisaEmpresa', ''),                  # 64. ANVISA EMPRESA
            client.get('acessoIbama', ''),                    # 65. ACESSO IBAMA
            client.get('senhaIbama', ''),                     # 66. SENHA IBAMA
            client.get('acessoSemace', ''),                   # 67. ACESSO SEMACE
            client.get('senhaSemace', ''),                    # 68. SENHA SEMACE
            
            # Bloco 7: Procurações
            'SIM' if client.get('procRfb') else 'NÃO',        # 69. PROCURAÇÃO RFB
            client.get('procRfbData', ''),                    # 70. DATA PROCURAÇÃO RFB
            'SIM' if client.get('procRc') else 'NÃO',         # 71. PROCURAÇÃO RECEITA ESTADUAL
            client.get('procRcData', ''),                     # 72. DATA PROCURAÇÃO RC
            'SIM' if client.get('procCx') else 'NÃO',         # 73. PROCURAÇÃO CAIXA ECONÔMICA
            client.get('procCxData', ''),                     # 74. DATA PROCURAÇÃO CX
            'SIM' if client.get('procSw') else 'NÃO',         # 75. PROCURAÇÃO PREVIDÊNCIA SOCIAL
            client.get('procSwData', ''),                     # 76. DATA PROCURAÇÃO SW
            'SIM' if client.get('procMunicipal') else 'NÃO',  # 77. PROCURAÇÃO MUNICIPAL
            client.get('procMunicipalData', ''),              # 78. DATA PROCURAÇÃO MUNICIPAL
            client.get('outrasProc', ''),                     # 79. OUTRAS PROCURAÇÕES
            client.get('obsProcuracoes', ''),                 # 80. OBSERVAÇÕES PROCURAÇÕES
            
            # Bloco 8: Observações e Dados Adicionais
            client.get('observacoesGerais', ''),              # 81. OBSERVAÇÕES GERAIS
            client.get('tarefasVinculadas', 0),               # 82. TAREFAS VINCULADAS
            client.get('dataInicioServicos', ''),             # 83. DATA INÍCIO SERVIÇOS
            client.get('statusCliente', 'ATIVO'),             # 84. STATUS DO CLIENTE
            client.get('ultimaAtualizacao', ''),              # 85. ÚLTIMA ATUALIZAÇÃO
            client.get('responsavelAtualizacao', ''),         # 86. RESPONSÁVEL ATUALIZAÇÃO
            client.get('prioridadeCliente', 'NORMAL'),        # 87. PRIORIDADE
            client.get('tagsCliente', ''),                    # 88. TAGS/CATEGORIAS
            client.get('historicoAlteracoes', ''),            # 89. HISTÓRICO DE ALTERAÇÕES
            
            # Campos internos do sistema
            client.get('id', ''),                             # 90. ID
            'SIM' if client.get('ativo', True) else 'NÃO',    # 91. CLIENTE ATIVO
            client.get('criadoEm', datetime.now().isoformat()) # 92. DATA DE CRIAÇÃO
        ]
    
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
        
        return {
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
            'responsavelServicos': safe_get(row, 17),           # 18. RESPONSÁVEL PELOS SERVIÇOS
            'dataInicioServicos': safe_get(row, 18),            # 19. DATA INÍCIO DOS SERVIÇOS
            
            # Códigos dos Sistemas (Bloco 2)
            'codFortesCt': safe_get(row, 19),                   # 20. CÓDIGO FORTES CT
            'codFortesFs': safe_get(row, 20),                   # 21. CÓDIGO FORTES FS
            'codFortesPs': safe_get(row, 21),                   # 22. CÓDIGO FORTES PS
            'codDominio': safe_get(row, 22),                    # 23. CÓDIGO DOMÍNIO
            'sistemaUtilizado': safe_get(row, 23),              # 24. SISTEMA UTILIZADO
            'moduloSpedTrier': safe_get(row, 24),               # 25. MÓDULO SPED TRIER
            
            # Bloco 3: Quadro Societário
            'socio1_nome': safe_get(row, 25),                   # 26. SÓCIO 1 NOME
            'socio1_cpf': safe_get(row, 26),                    # 27. SÓCIO 1 CPF
            'socio1_nascimento': safe_get(row, 27),             # 28. SÓCIO 1 DATA NASCIMENTO
            'socio1_admin': bool_from_text(safe_get(row, 28)),  # 29. SÓCIO 1 ADMINISTRADOR
            'socio1_cotas': safe_get(row, 29),                  # 30. SÓCIO 1 COTAS
            'socio1_resp_legal': bool_from_text(safe_get(row, 30)), # 31. SÓCIO 1 RESPONSÁVEL LEGAL
            
            # Campos legados para compatibilidade
            'socio1': safe_get(row, 25),                        # Alias para socio1_nome
            'donoResp': safe_get(row, 17),                      # Alias para responsavelServicos
            'mesAnoInicio': safe_get(row, 18),                  # Alias para dataInicioServicos
            
            # Bloco 4: Contatos
            'telefoneFixo': safe_get(row, 31),                  # 32. TELEFONE FIXO
            'telefoneCelular': safe_get(row, 32),               # 33. TELEFONE CELULAR
            'whatsapp': safe_get(row, 33),                      # 34. WHATSAPP
            'emailPrincipal': safe_get(row, 34),                # 35. EMAIL PRINCIPAL
            'emailSecundario': safe_get(row, 35),               # 36. EMAIL SECUNDÁRIO
            'responsavelImediato': safe_get(row, 36),           # 37. RESPONSÁVEL IMEDIATO
            'emailsSocios': safe_get(row, 37),                  # 38. EMAILS DOS SÓCIOS
            'contatoContador': safe_get(row, 38),               # 39. CONTATO CONTADOR
            'telefoneContador': safe_get(row, 39),              # 40. TELEFONE CONTADOR
            'emailContador': safe_get(row, 40),                 # 41. EMAIL CONTADOR
            
            # Campos legados para compatibilidade
            'emailsSocio': safe_get(row, 37),                   # Alias para emailsSocios
            
            # Bloco 5: Sistemas e Acessos
            'sistemaPrincipal': safe_get(row, 41),              # 42. SISTEMA PRINCIPAL
            'versaoSistema': safe_get(row, 42),                 # 43. VERSÃO DO SISTEMA
            'codAcessoSimples': safe_get(row, 43),              # 44. CÓDIGO ACESSO SIMPLES NACIONAL
            'cpfCnpjAcesso': safe_get(row, 44),                 # 45. CPF/CNPJ PARA ACESSO
            'portalClienteAtivo': bool_from_text(safe_get(row, 45)), # 46. PORTAL CLIENTE ATIVO
            'integracaoDominio': bool_from_text(safe_get(row, 46)),  # 47. INTEGRAÇÃO DOMÍNIO
            'sistemaOnvio': bool_from_text(safe_get(row, 47)),  # 48. SISTEMA ONVIO
            
            # Campos legados para compatibilidade
            'portalCliente': bool_from_text(safe_get(row, 45)), # Alias para portalClienteAtivo
            'integradoDominio': bool_from_text(safe_get(row, 46)), # Alias para integracaoDominio
            'onvio': bool_from_text(safe_get(row, 47)),         # Alias para sistemaOnvio
            
            # Bloco 6: Senhas e Credenciais
            'acessoIss': safe_get(row, 48),                     # 49. ACESSO ISS
            'senhaIss': safe_get(row, 49),                      # 50. SENHA ISS
            'acessoSefin': safe_get(row, 50),                   # 51. ACESSO SEFIN
            'senhaSefin': safe_get(row, 51),                    # 52. SENHA SEFIN
            'acessoSeuma': safe_get(row, 52),                   # 53. ACESSO SEUMA
            'senhaSeuma': safe_get(row, 53),                    # 54. SENHA SEUMA
            'acessoEmpWeb': safe_get(row, 54),                  # 55. ACESSO EMPWEB
            'senhaEmpWeb': safe_get(row, 55),                   # 56. SENHA EMPWEB
            'acessoFapInss': safe_get(row, 56),                 # 57. ACESSO FAP/INSS
            'senhaFapInss': safe_get(row, 57),                  # 58. SENHA FAP/INSS
            'acessoCrf': safe_get(row, 58),                     # 59. ACESSO CRF
            'senhaCrf': safe_get(row, 59),                      # 60. SENHA CRF
            'emailGestor': safe_get(row, 60),                   # 61. EMAIL GESTOR
            'senhaEmailGestor': safe_get(row, 61),              # 62. SENHA EMAIL GESTOR
            'anvisaGestor': safe_get(row, 62),                  # 63. ANVISA GESTOR
            'anvisaEmpresa': safe_get(row, 63),                 # 64. ANVISA EMPRESA
            'acessoIbama': safe_get(row, 64),                   # 65. ACESSO IBAMA
            'senhaIbama': safe_get(row, 65),                    # 66. SENHA IBAMA
            'acessoSemace': safe_get(row, 66),                  # 67. ACESSO SEMACE
            'senhaSemace': safe_get(row, 67),                   # 68. SENHA SEMACE
            
            # Bloco 7: Procurações
            'procRfb': bool_from_text(safe_get(row, 68)),       # 69. PROCURAÇÃO RFB
            'procRfbData': safe_get(row, 69),                   # 70. DATA PROCURAÇÃO RFB
            'procRc': bool_from_text(safe_get(row, 70)),        # 71. PROCURAÇÃO RECEITA ESTADUAL
            'procRcData': safe_get(row, 71),                    # 72. DATA PROCURAÇÃO RC
            'procCx': bool_from_text(safe_get(row, 72)),        # 73. PROCURAÇÃO CAIXA ECONÔMICA
            'procCxData': safe_get(row, 73),                    # 74. DATA PROCURAÇÃO CX
            'procSw': bool_from_text(safe_get(row, 74)),        # 75. PROCURAÇÃO PREVIDÊNCIA SOCIAL
            'procSwData': safe_get(row, 75),                    # 76. DATA PROCURAÇÃO SW
            'procMunicipal': bool_from_text(safe_get(row, 76)), # 77. PROCURAÇÃO MUNICIPAL
            'procMunicipalData': safe_get(row, 77),             # 78. DATA PROCURAÇÃO MUNICIPAL
            'outrasProc': safe_get(row, 78),                    # 79. OUTRAS PROCURAÇÕES
            'obsProcuracoes': safe_get(row, 79),                # 80. OBSERVAÇÕES PROCURAÇÕES
            
            # Bloco 8: Observações e Dados Adicionais
            'observacoesGerais': safe_get(row, 80),             # 81. OBSERVAÇÕES GERAIS
            'tarefasVinculadas': int(safe_get(row, 81, 0)) if str(safe_get(row, 81, 0)).isdigit() else 0, # 82. TAREFAS VINCULADAS
            'statusCliente': safe_get(row, 83, 'ATIVO'),        # 84. STATUS DO CLIENTE
            'ultimaAtualizacao': safe_get(row, 84),             # 85. ÚLTIMA ATUALIZAÇÃO
            'responsavelAtualizacao': safe_get(row, 85),        # 86. RESPONSÁVEL ATUALIZAÇÃO
            'prioridadeCliente': safe_get(row, 86, 'NORMAL'),   # 87. PRIORIDADE
            'tagsCliente': safe_get(row, 87),                   # 88. TAGS/CATEGORIAS
            'historicoAlteracoes': safe_get(row, 88),           # 89. HISTÓRICO DE ALTERAÇÕES
            
            # Campos internos do sistema
            'id': safe_get(row, 89),                            # 90. ID
            'ativo': bool_from_text(safe_get(row, 90, 'SIM'), True), # 91. CLIENTE ATIVO
            'criadoEm': safe_get(row, 91, datetime.now().isoformat()) # 92. DATA DE CRIAÇÃO
        }

    def get_all_values(self):
        """Retorna todos os valores da planilha no range especificado"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=self.range_name
            ).execute()
            
            return result.get('values', [])
        except Exception as e:
            print(f"❌ Erro ao buscar valores: {e}")
            return []

    def update_range(self, range_name: str, values: list):
        """Atualiza um range específico na planilha"""
        try:
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return True
        except Exception as e:
            print(f"❌ Erro ao atualizar range: {e}")
            return False

    def append_row(self, values: list):
        """Adiciona uma nova linha ao final da planilha"""
        try:
            body = {
                'values': [values]
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=self.range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            return True
        except Exception as e:
            print(f"❌ Erro ao adicionar linha: {e}")
            return False

    def get_worksheet(self, worksheet_name: str):
        """Retorna uma instância de worksheet para trabalhar com abas específicas"""
        return GoogleSheetsWorksheet(self.service, self.spreadsheet_id, worksheet_name)
    
    def create_worksheet(self, worksheet_name: str, rows: int = 1000, cols: int = 26):
        """Cria uma nova aba na planilha"""
        try:
            body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': worksheet_name,
                            'gridProperties': {
                                'rowCount': rows,
                                'columnCount': cols
                            }
                        }
                    }
                }]
            }
            
            result = self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()
            
            print(f"✅ Aba '{worksheet_name}' criada com sucesso!")
            return True
            
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"⚠️ Aba '{worksheet_name}' já existe")
                return True
            else:
                print(f"❌ Erro ao criar aba '{worksheet_name}': {e}")
                return False
    
    def worksheet_exists(self, worksheet_name: str) -> bool:
        """Verifica se uma aba existe na planilha"""
        try:
            result = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            sheets = result.get('sheets', [])
            for sheet in sheets:
                if sheet['properties']['title'] == worksheet_name:
                    return True
            return False
            
        except Exception as e:
            print(f"❌ Erro ao verificar aba '{worksheet_name}': {e}")
            return False


class GoogleSheetsWorksheet:
    """Classe para trabalhar com uma aba específica do Google Sheets"""
    
    def __init__(self, service, spreadsheet_id: str, worksheet_name: str):
        self.service = service
        self.spreadsheet_id = spreadsheet_id
        self.worksheet_name = worksheet_name
        self.range_name = f"{worksheet_name}!A:Z"
    
    @property
    def row_count(self):
        """Retorna o número de linhas com dados"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=self.range_name
            ).execute()
            
            values = result.get('values', [])
            return len(values)
        except:
            return 0
    
    def row_values(self, row_number: int):
        """Retorna os valores de uma linha específica"""
        try:
            range_name = f"{self.worksheet_name}!{row_number}:{row_number}"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            return values[0] if values else []
        except:
            return []
    
    def get_all_values(self):
        """Retorna todos os valores da aba"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=self.range_name
            ).execute()
            
            return result.get('values', [])
        except Exception as e:
            print(f"❌ Erro ao buscar valores da aba '{self.worksheet_name}': {e}")
            return []
    
    def insert_row(self, values, row_number=None):
        """Insere uma linha na aba"""
        try:
            if row_number is None:
                # Adiciona no final
                current_rows = self.row_count
                row_number = current_rows + 1
            
            range_name = f"{self.worksheet_name}!A{row_number}"
            body = {
                'values': [values]
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return True
        except Exception as e:
            print(f"❌ Erro ao inserir linha: {e}")
            return False
    
    def update_cell(self, row, col, value):
        """Atualiza uma célula específica"""
        try:
            # Converte número da coluna para letra
            col_letter = chr(65 + col - 1)  # A=65
            range_name = f"{self.worksheet_name}!{col_letter}{row}"
            
            body = {
                'values': [[value]]
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return True
        except Exception as e:
            print(f"❌ Erro ao atualizar célula: {e}")
            return False
