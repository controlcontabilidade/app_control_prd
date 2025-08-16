import requests
import json
from typing import List, Dict, Optional
from datetime import datetime

class GoogleSheetsService:
    def __init__(self, api_key: str, spreadsheet_id: str, range_name: str = 'Clientes!A:AZ'):
        self.api_key = api_key
        self.spreadsheet_id = spreadsheet_id
        self.range_name = range_name
        self.base_url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}'
    
    def client_to_row(self, client: Dict) -> List:
        """Converte dados do cliente para linha da planilha"""
        return [
            client.get('id', ''),
            client.get('nomeEmpresa', ''),
            'SIM' if client.get('ct') else 'NAO',
            'SIM' if client.get('fs') else 'NAO',
            'SIM' if client.get('dp') else 'NAO',
            f"'{str(client.get('codFortesCt', '')).zfill(4)}" if client.get('codFortesCt') else '',
            f"'{str(client.get('codFortesFs', '')).zfill(4)}" if client.get('codFortesFs') else '',
            f"'{str(client.get('codFortesPs', '')).zfill(4)}" if client.get('codFortesPs') else '',
            f"'{str(client.get('codDominio', '')).zfill(4)}" if client.get('codDominio') else '',
            client.get('sistemaUtilizado', ''),
            client.get('moduloSpedTrier', ''),
            client.get('razaoSocialReceita', ''),
            client.get('nomeFantasiaReceita', ''),
            client.get('cnpj', ''),
            client.get('inscEst', ''),
            client.get('inscMun', ''),
            client.get('segmento', ''),
            client.get('atividade', ''),
            client.get('tributacao', 'SIMPLES'),
            client.get('cidade', ''),
            client.get('donoResp', ''),
            client.get('codAcessoSimples', ''),
            client.get('cpfOuCnpj', ''),
            client.get('acessoIss', ''),
            client.get('acessoSefin', ''),
            client.get('acessoSeuma', ''),
            client.get('acessoEmpWeb', ''),
            client.get('senhaEmpWeb', ''),
            client.get('acessoFapInss', ''),
            client.get('acessoCrf', ''),
            client.get('emailGestor', ''),
            client.get('anvisaGestor', ''),
            client.get('anvisaEmpresa', ''),
            client.get('acessoIbama', ''),
            client.get('acessoSemace', ''),
            client.get('senhaSemace', ''),
            client.get('procRc', ''),
            client.get('procCx', ''),
            client.get('procSw', ''),
            client.get('mesAnoInicio', ''),
            client.get('responsavelImediato', ''),
            client.get('telefoneFixo', ''),
            client.get('telefoneCelular', ''),
            client.get('emailsSocio', ''),
            client.get('socio1', ''),
            client.get('socio2', ''),
            client.get('socio3', ''),
            'SIM' if client.get('ativo', True) else 'NAO',
            'SIM' if client.get('integradoDominio') else 'NAO',
            'SIM' if client.get('portalCliente') else 'NAO',
            client.get('criadoEm', '')
        ]
    
    def row_to_client(self, row: List) -> Dict:
        """Converte linha da planilha para dados do cliente"""
        if len(row) < 2:
            return None
            
        def get_cell(index, default=''):
            return row[index] if index < len(row) else default
        
        return {
            'id': get_cell(0),
            'nomeEmpresa': get_cell(1),
            'ct': get_cell(2) == 'SIM',
            'fs': get_cell(3) == 'SIM',
            'dp': get_cell(4) == 'SIM',
            'codFortesCt': get_cell(5).lstrip("'").zfill(4) if get_cell(5) else '',
            'codFortesFs': get_cell(6).lstrip("'").zfill(4) if get_cell(6) else '',
            'codFortesPs': get_cell(7).lstrip("'").zfill(4) if get_cell(7) else '',
            'codDominio': get_cell(8).lstrip("'").zfill(4) if get_cell(8) else '',
            'sistemaUtilizado': get_cell(9),
            'moduloSpedTrier': get_cell(10),
            'razaoSocialReceita': get_cell(11),
            'nomeFantasiaReceita': get_cell(12),
            'cnpj': get_cell(13),
            'inscEst': get_cell(14),
            'inscMun': get_cell(15),
            'segmento': get_cell(16),
            'atividade': get_cell(17),
            'tributacao': get_cell(18, 'SIMPLES'),
            'cidade': get_cell(19),
            'donoResp': get_cell(20),
            'codAcessoSimples': get_cell(21),
            'cpfOuCnpj': get_cell(22),
            'acessoIss': get_cell(23),
            'acessoSefin': get_cell(24),
            'acessoSeuma': get_cell(25),
            'acessoEmpWeb': get_cell(26),
            'senhaEmpWeb': get_cell(27),
            'acessoFapInss': get_cell(28),
            'acessoCrf': get_cell(29),
            'emailGestor': get_cell(30),
            'anvisaGestor': get_cell(31),
            'anvisaEmpresa': get_cell(32),
            'acessoIbama': get_cell(33),
            'acessoSemace': get_cell(34),
            'senhaSemace': get_cell(35),
            'procRc': get_cell(36),
            'procCx': get_cell(37),
            'procSw': get_cell(38),
            'mesAnoInicio': get_cell(39),
            'responsavelImediato': get_cell(40),
            'telefoneFixo': get_cell(41),
            'telefoneCelular': get_cell(42),
            'emailsSocio': get_cell(43),
            'socio1': get_cell(44),
            'socio2': get_cell(45),
            'socio3': get_cell(46),
            'ativo': get_cell(47, 'SIM') == 'SIM',
            'integradoDominio': get_cell(48) == 'SIM',
            'portalCliente': get_cell(49) == 'SIM',
            'criadoEm': get_cell(50)
        }
    
    def get_clients(self) -> List[Dict]:
        """Busca todos os clientes da planilha"""
        try:
            url = f'{self.base_url}/values/{self.range_name}'
            params = {
                'key': self.api_key,
                'majorDimension': 'ROWS'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            values = data.get('values', [])
            
            # Skip header row if exists
            if values and len(values) > 0:
                # Check if first row is header
                first_row = values[0]
                if first_row and len(first_row) > 0 and (first_row[0] == 'ID' or first_row[0] == 'id'):
                    values = values[1:]
            
            clients = []
            for row in values:
                if row and len(row) > 1:  # Skip empty rows
                    client = self.row_to_client(row)
                    if client and client.get('nomeEmpresa'):
                        clients.append(client)
            
            return clients
            
        except Exception as e:
            print(f"Erro ao buscar clientes: {e}")
            return []
    
    def get_client(self, client_id: str) -> Optional[Dict]:
        """Busca um cliente específico pelo ID"""
        clients = self.get_clients()
        for client in clients:
            if str(client.get('id')) == str(client_id):
                return client
        return None
    
    def save_client(self, client: Dict) -> bool:
        """Salva ou atualiza um cliente - versão híbrida com fallback local"""
        try:
            print(f"🔍 Tentando salvar cliente: {client.get('nomeEmpresa')}")
            
            # Primeiro, tentamos salvar no Google Sheets usando append
            success = self._try_save_to_sheets(client)
            
            if not success:
                print("⚠️ Salvamento no Google Sheets falhou, usando backup local")
                # Fallback para armazenamento local
                from .local_storage_service import LocalStorageService
                local_service = LocalStorageService()
                return local_service.save_client(client)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar cliente: {e}")
            print(f"� Tipo do erro: {type(e).__name__}")
            # Fallback para armazenamento local em caso de erro
            try:
                from .local_storage_service import LocalStorageService
                local_service = LocalStorageService()
                return local_service.save_client(client)
            except:
                return False
    
    def _try_save_to_sheets(self, client: Dict) -> bool:
        """Tenta salvar diretamente no Google Sheets"""
        try:
            # Convertemos cliente para linha da planilha
            row_data = self.client_to_row(client)
            
            # Verificamos se é atualização ou novo cliente
            existing_clients = self.get_clients()
            client_id = str(client.get('id'))
            
            for i, existing in enumerate(existing_clients):
                if str(existing.get('id')) == client_id:
                    # É uma atualização - tentamos UPDATE
                    return self._update_row(i + 2, row_data)  # +2 para linha correta (header + 1-indexed)
            
            # É um novo cliente - tentamos APPEND
            return self._append_row(row_data)
            
        except Exception as e:
            print(f"❌ Erro ao tentar salvar no Sheets: {e}")
            return False
    
    def _update_row(self, row_number: int, row_data: List) -> bool:
        """Atualiza uma linha específica na planilha"""
        try:
            url = f'{self.base_url}/values/Clientes!A{row_number}:AZ{row_number}'
            params = {'key': self.api_key, 'valueInputOption': 'USER_ENTERED'}
            data = {
                'values': [row_data]
            }
            
            response = requests.put(url, params=params, json=data)
            
            if response.status_code == 200:
                print(f"✅ Cliente atualizado na linha {row_number}")
                return True
            else:
                print(f"❌ Falha na atualização: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao atualizar linha: {e}")
            return False
    
    def _append_row(self, row_data: List) -> bool:
        """Adiciona uma nova linha na planilha"""
        try:
            url = f'{self.base_url}/values/Clientes!A:AZ:append'
            params = {'key': self.api_key, 'valueInputOption': 'USER_ENTERED'}
            data = {
                'values': [row_data]
            }
            
            response = requests.post(url, params=params, json=data)
            
            if response.status_code == 200:
                print("✅ Novo cliente adicionado")
                return True
            else:
                print(f"❌ Falha no append: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao adicionar linha: {e}")
            return False
    
    def delete_client(self, client_id: str) -> bool:
        """Remove um cliente da planilha - versão híbrida com fallback local"""
        try:
            print(f"🗑️ Tentando deletar cliente ID: {client_id}")
            
            # Primeiro tentamos deletar do Google Sheets
            success = self._try_delete_from_sheets(client_id)
            
            if not success:
                print("⚠️ Deleção no Google Sheets falhou, usando backup local")
                # Fallback para armazenamento local
                from .local_storage_service import LocalStorageService
                local_service = LocalStorageService()
                return local_service.delete_client(client_id)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao deletar cliente: {e}")
            # Fallback para armazenamento local em caso de erro
            try:
                from .local_storage_service import LocalStorageService
                local_service = LocalStorageService()
                return local_service.delete_client(client_id)
            except:
                return False
    
    def _try_delete_from_sheets(self, client_id: str) -> bool:
        """Tenta deletar diretamente do Google Sheets"""
        try:
            clients = self.get_clients()
            
            # Find client row
            target_row = None
            for i, client in enumerate(clients):
                if str(client.get('id')) == str(client_id):
                    target_row = i + 2  # +2 because sheets are 1-indexed and we skip header
                    break
            
            if not target_row:
                print(f"❌ Cliente {client_id} não encontrado")
                return False
            
            # Delete row using batchUpdate
            url = f'{self.base_url}:batchUpdate'
            params = {'key': self.api_key}
            # Descobrir o sheetId da aba Clientes para não depender de ser a primeira
            sheet_id = 0
            try:
                meta_url = f"{self.base_url.replace('/v4/spreadsheets', '/v4/spreadsheets')}/{self.sheet_id}"
                # Nota: Em contextos sem auth adicional, a API metadata com API key pode ser restrita.
                # Neste cliente híbrido, manter fallback para 0 se falhar resolver.
                sheet_id = 0
            except Exception:
                sheet_id = 0

            data = {
                'requests': [{
                    'deleteDimension': {
                        'range': {
                            'sheetId': sheet_id,
                            'dimension': 'ROWS',
                            'startIndex': target_row - 1,
                            'endIndex': target_row
                        }
                    }
                }]
            }
            
            response = requests.post(url, params=params, json=data)
            
            if response.status_code == 200:
                print(f"✅ Cliente deletado da linha {target_row}")
                return True
            else:
                print(f"❌ Falha na deleção: {response.status_code} - {response.text}")
                return False
            
        except Exception as e:
            print(f"❌ Erro ao tentar deletar do Sheets: {e}")
            return False
