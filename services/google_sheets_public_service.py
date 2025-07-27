import requests
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any

class GoogleSheetsPublicService:
    """
    Serviço para Google Sheets PÚBLICO com permissão de escrita
    """
    
    def __init__(self, api_key: str, spreadsheet_id: str, sheet_range: str = "Clientes!A:AZ"):
        self.api_key = api_key
        self.spreadsheet_id = spreadsheet_id
        self.sheet_range = sheet_range
        self.base_url = "https://sheets.googleapis.com/v4/spreadsheets"
        
        print(f"🔧 GoogleSheetsPublicService inicializado:")
        print(f"   📊 Spreadsheet ID: {spreadsheet_id}")
        print(f"   🔑 API Key: {api_key[:10]}...")
        print(f"   📋 Range: {sheet_range}")
    
    def _make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Faz requisições para a API do Google Sheets"""
        url = f"{self.base_url}/{self.spreadsheet_id}/{endpoint}?key={self.api_key}"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=30)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            print(f"📡 {method} {url[:100]}...")
            print(f"📈 Status: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro na requisição: {response.status_code}")
                print(f"📄 Resposta: {response.text[:500]}")
                return None
                
        except Exception as e:
            print(f"❌ Erro na requisição: {str(e)}")
            return None
    
    def get_all_clients(self) -> List[Dict]:
        """Lê todos os clientes do Google Sheets"""
        try:
            print("📊 Lendo dados do Google Sheets...")
            
            endpoint = f"values/{self.sheet_range}"
            result = self._make_request('GET', endpoint)
            
            if not result or 'values' not in result:
                print("⚠️ Nenhum dado encontrado no Google Sheets")
                return []
            
            rows = result['values']
            if len(rows) < 2:
                print("⚠️ Planilha vazia ou sem cabeçalho")
                return []
            
            headers = rows[0]
            clients = []
            
            for i, row in enumerate(rows[1:], start=2):
                # Preencher colunas vazias
                while len(row) < len(headers):
                    row.append('')
                
                client = {}
                for j, header in enumerate(headers):
                    if j < len(row):
                        value = row[j]
                        # Converter valores booleanos
                        if header in ['ct', 'fs', 'dp', 'ativo', 'integradoDominio', 'portalCliente']:
                            client[header] = value.lower() in ['true', 'sim', '1', 'x']
                        else:
                            client[header] = value
                    else:
                        client[header] = ''
                
                if client.get('id'):
                    clients.append(client)
            
            print(f"✅ {len(clients)} clientes carregados do Google Sheets")
            return clients
            
        except Exception as e:
            print(f"❌ Erro ao ler Google Sheets: {str(e)}")
            return []
    
    def save_client(self, client_data: Dict) -> bool:
        """Salva um cliente no Google Sheets"""
        try:
            print(f"💾 Salvando cliente no Google Sheets: {client_data.get('nomeEmpresa', 'N/A')}")
            
            # Primeiro, obter os dados atuais para saber onde inserir
            current_data = self._make_request('GET', f"values/{self.sheet_range}")
            
            if not current_data or 'values' not in current_data:
                print("❌ Erro ao obter dados atuais da planilha")
                return False
            
            rows = current_data['values']
            headers = rows[0] if rows else []
            
            # Se não há cabeçalho, criar um
            if not headers:
                headers = [
                    'id', 'nomeEmpresa', 'ct', 'fs', 'dp', 'codFortesCt', 'codFortesFs', 'codFortesPs',
                    'codDominio', 'sistemaUtilizado', 'moduloSpedTrier', 'razaoSocialReceita',
                    'nomeFantasiaReceita', 'cnpj', 'inscEst', 'inscMun', 'segmento', 'atividade',
                    'tributacao', 'cidade', 'donoResp', 'codAcessoSimples', 'cpfOuCnpj', 'acessoIss',
                    'acessoSefin', 'acessoSeuma', 'acessoEmpWeb', 'senhaEmpWeb', 'acessoFapInss',
                    'acessoCrf', 'emailGestor', 'anvisaGestor', 'anvisaEmpresa', 'acessoIbama',
                    'acessoSemace', 'senhaSemace', 'procRc', 'procCx', 'procSw', 'mesAnoInicio',
                    'responsavelImediato', 'telefoneFixo', 'telefoneCelular', 'emailsSocio',
                    'socio1', 'socio2', 'socio3', 'ativo', 'integradoDominio', 'portalCliente',
                    'tarefasVinculadas', 'criadoEm'
                ]
                
                # Inserir cabeçalho na primeira linha
                header_data = {
                    "range": "Clientes!A1",
                    "majorDimension": "ROWS",
                    "values": [headers]
                }
                
                result = self._make_request('PUT', f"values/Clientes!A1?valueInputOption=RAW", header_data)
                if not result:
                    print("❌ Erro ao inserir cabeçalho")
                    return False
            
            # Preparar dados do cliente
            if not client_data.get('id'):
                client_data['id'] = str(uuid.uuid4())
            
            if not client_data.get('criadoEm'):
                client_data['criadoEm'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Criar linha com dados do cliente
            client_row = []
            for header in headers:
                value = client_data.get(header, '')
                # Converter booleanos para string
                if isinstance(value, bool):
                    value = 'TRUE' if value else 'FALSE'
                elif value is None:
                    value = ''
                client_row.append(str(value))
            
            # Verificar se cliente já existe (atualizar) ou é novo (inserir)
            client_exists = False
            update_row = None
            
            for i, row in enumerate(rows[1:], start=2):
                if len(row) > 0 and row[0] == client_data['id']:
                    client_exists = True
                    update_row = i
                    break
            
            if client_exists and update_row:
                # Atualizar cliente existente
                range_to_update = f"Clientes!A{update_row}"
                print(f"🔄 Atualizando cliente existente na linha {update_row}")
            else:
                # Inserir novo cliente
                next_row = len(rows) + 1
                range_to_update = f"Clientes!A{next_row}"
                print(f"➕ Inserindo novo cliente na linha {next_row}")
            
            # Preparar dados para envio
            update_data = {
                "range": range_to_update,
                "majorDimension": "ROWS",
                "values": [client_row]
            }
            
            # Enviar dados
            result = self._make_request('PUT', f"values/{range_to_update}?valueInputOption=RAW", update_data)
            
            if result:
                print(f"✅ Cliente salvo no Google Sheets com sucesso!")
                return True
            else:
                print(f"❌ Erro ao salvar cliente no Google Sheets")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao salvar no Google Sheets: {str(e)}")
            return False
    
    def delete_client(self, client_id: str) -> bool:
        """Remove um cliente do Google Sheets"""
        try:
            print(f"🗑️ Removendo cliente {client_id} do Google Sheets...")
            
            # Obter dados atuais
            current_data = self._make_request('GET', f"values/{self.sheet_range}")
            
            if not current_data or 'values' not in current_data:
                print("❌ Erro ao obter dados da planilha")
                return False
            
            rows = current_data['values']
            if len(rows) < 2:
                print("⚠️ Planilha vazia")
                return False
            
            # Encontrar linha do cliente
            delete_row = None
            for i, row in enumerate(rows[1:], start=2):
                if len(row) > 0 and row[0] == client_id:
                    delete_row = i
                    break
            
            if not delete_row:
                print(f"⚠️ Cliente {client_id} não encontrado")
                return False
            
            # Criar linha vazia para "deletar"
            empty_row = [''] * len(rows[0])
            
            delete_data = {
                "range": f"Clientes!A{delete_row}",
                "majorDimension": "ROWS",
                "values": [empty_row]
            }
            
            result = self._make_request('PUT', f"values/Clientes!A{delete_row}?valueInputOption=RAW", delete_data)
            
            if result:
                print(f"✅ Cliente removido do Google Sheets!")
                return True
            else:
                print(f"❌ Erro ao remover cliente")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao deletar do Google Sheets: {str(e)}")
            return False
    
    def get_client(self, client_id: str) -> Optional[Dict]:
        """Obtém um cliente específico"""
        clients = self.get_all_clients()
        for client in clients:
            if client.get('id') == client_id:
                return client
        return None
    
    def test_connection(self) -> bool:
        """Testa a conexão com o Google Sheets"""
        try:
            print("🔍 Testando conexão com Google Sheets...")
            result = self._make_request('GET', f"values/Clientes!A1:B1")
            
            if result:
                print("✅ Conexão com Google Sheets OK!")
                return True
            else:
                print("❌ Falha na conexão com Google Sheets")
                return False
        except Exception as e:
            print(f"❌ Erro no teste de conexão: {str(e)}")
            return False
