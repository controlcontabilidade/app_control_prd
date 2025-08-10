"""
Serviço para gerenciar Segmentos e Atividades Principais
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from services.google_sheets_service_account import GoogleSheetsServiceAccountService

class SegmentoAtividadeService:
    """
    Serviço para gerenciar cadastros de Segmento e Atividade Principal
    Utiliza Google Sheets como backend de armazenamento
    """
    
    def __init__(self, spreadsheet_id=None):
        self.spreadsheet_id = spreadsheet_id or '1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s'
        self.sheets_service = GoogleSheetsServiceAccountService(self.spreadsheet_id)
        self.segmentos_worksheet = 'Segmentos'
        self.atividades_worksheet = 'Atividades'
        
        print(f"🏢 SegmentoAtividadeService inicializado")
        self._ensure_worksheets_exist()
    
    def _ensure_worksheets_exist(self):
        """Garante que as planilhas de Segmentos e Atividades existem"""
        try:
            # Verificar e criar aba de Segmentos
            if not self._worksheet_exists(self.segmentos_worksheet):
                print(f"📋 Criando aba '{self.segmentos_worksheet}' no Google Sheets...")
                self._create_segmentos_worksheet()
            else:
                print(f"✅ Aba '{self.segmentos_worksheet}' já existe")
            
            # Verificar e criar aba de Atividades
            if not self._worksheet_exists(self.atividades_worksheet):
                print(f"📋 Criando aba '{self.atividades_worksheet}' no Google Sheets...")
                self._create_atividades_worksheet()
            else:
                print(f"✅ Aba '{self.atividades_worksheet}' já existe")
                
        except Exception as e:
            print(f"❌ Erro ao verificar/criar planilhas: {e}")
    
    def _worksheet_exists(self, worksheet_name: str) -> bool:
        """Verifica se uma aba existe na planilha"""
        try:
            spreadsheet = self.sheets_service.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            worksheet_names = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
            return worksheet_name in worksheet_names
            
        except Exception as e:
            print(f"❌ Erro ao verificar existência da aba: {e}")
            return False
    
    def _create_segmentos_worksheet(self):
        """Cria a aba de Segmentos com cabeçalhos"""
        try:
            # Criar nova aba
            requests = [{
                'addSheet': {
                    'properties': {
                        'title': self.segmentos_worksheet,
                        'gridProperties': {
                            'rowCount': 1000,
                            'columnCount': 10
                        }
                    }
                }
            }]
            
            self.sheets_service.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
            # Adicionar cabeçalhos
            headers = [
                'ID',
                'Nome do Segmento',
                'Descrição',
                'Código',
                'Ativo',
                'Data de Criação',
                'Última Atualização',
                'Criado Por',
                'Observações',
                'Ordem de Exibição'
            ]
            
            self.sheets_service.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.segmentos_worksheet}!A1:J1',
                valueInputOption='USER_ENTERED',
                body={'values': [headers]}
            ).execute()
            
            print(f"✅ Aba '{self.segmentos_worksheet}' criada com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao criar aba de segmentos: {e}")
            raise
    
    def _create_atividades_worksheet(self):
        """Cria a aba de Atividades com cabeçalhos"""
        try:
            # Criar nova aba
            requests = [{
                'addSheet': {
                    'properties': {
                        'title': self.atividades_worksheet,
                        'gridProperties': {
                            'rowCount': 1000,
                            'columnCount': 12
                        }
                    }
                }
            }]
            
            self.sheets_service.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
            # Adicionar cabeçalhos
            headers = [
                'ID',
                'Nome da Atividade',
                'Código CNAE',
                'Descrição',
                'Segmento ID',
                'Segmento Nome',
                'Ativo',
                'Data de Criação',
                'Última Atualização',
                'Criado Por',
                'Observações',
                'Ordem de Exibição'
            ]
            
            self.sheets_service.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.atividades_worksheet}!A1:L1',
                valueInputOption='USER_ENTERED',
                body={'values': [headers]}
            ).execute()
            
            print(f"✅ Aba '{self.atividades_worksheet}' criada com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao criar aba de atividades: {e}")
            raise
    
    # ==================== MÉTODOS PARA SEGMENTOS ====================
    
    def get_segmentos(self) -> List[Dict]:
        """Busca todos os segmentos"""
        try:
            print(f"📋 Buscando segmentos na aba '{self.segmentos_worksheet}'...")
            
            result = self.sheets_service.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.segmentos_worksheet}!A:J'
            ).execute()
            
            rows = result.get('values', [])
            if not rows:
                print("⚠️ Nenhum segmento encontrado")
                return []
            
            headers = rows[0]
            segmentos = []
            
            for i, row in enumerate(rows[1:], start=2):
                if len(row) > 0 and row[0]:  # Se tem ID
                    segmento = self._row_to_segmento(headers, row, i)
                    if segmento:
                        segmentos.append(segmento)
            
            print(f"✅ {len(segmentos)} segmentos carregados")
            return segmentos
            
        except Exception as e:
            print(f"❌ Erro ao buscar segmentos: {e}")
            return []
    
    def get_segmento(self, segmento_id: str) -> Optional[Dict]:
        """Busca um segmento específico por ID"""
        try:
            print(f"🔍 Buscando segmento ID: {segmento_id}")
            
            segmentos = self.get_segmentos()
            for segmento in segmentos:
                if str(segmento.get('id')) == str(segmento_id):
                    print(f"✅ Segmento encontrado: {segmento.get('nome')}")
                    return segmento
            
            print(f"❌ Segmento ID '{segmento_id}' não encontrado")
            return None
            
        except Exception as e:
            print(f"❌ Erro ao buscar segmento: {e}")
            return None
    
    def save_segmento(self, segmento: Dict) -> bool:
        """Salva ou atualiza um segmento"""
        try:
            print(f"💾 Salvando segmento: {segmento.get('nome')}")
            
            segmento_id = segmento.get('id')
            if segmento_id and str(segmento_id).strip():
                # Atualizar existente
                return self._update_segmento(segmento)
            else:
                # Criar novo
                return self._create_segmento(segmento)
                
        except Exception as e:
            print(f"❌ Erro ao salvar segmento: {e}")
            return False
    
    def _create_segmento(self, segmento: Dict) -> bool:
        """Cria um novo segmento"""
        try:
            # Gerar ID único
            import random
            timestamp = int(datetime.now().timestamp())
            random_suffix = random.randint(100, 999)
            segmento['id'] = f"SEG{timestamp}{random_suffix}"
            
            # Adicionar timestamps
            segmento['dataCriacao'] = datetime.now().isoformat()
            segmento['ultimaAtualizacao'] = datetime.now().isoformat()
            
            # Converter para linha
            row_data = self._segmento_to_row(segmento)
            
            # Adicionar na planilha
            body = {'values': [row_data]}
            result = self.sheets_service.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.segmentos_worksheet}!A:J',
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            print(f"✅ Segmento criado: {segmento['id']}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar segmento: {e}")
            return False
    
    def _update_segmento(self, segmento: Dict) -> bool:
        """Atualiza um segmento existente"""
        try:
            # Encontrar linha do segmento
            row_index = self._find_segmento_row(segmento['id'])
            if row_index <= 0:
                print(f"❌ Segmento ID '{segmento['id']}' não encontrado para atualização")
                return False
            
            # Atualizar timestamp
            segmento['ultimaAtualizacao'] = datetime.now().isoformat()
            
            # Converter para linha
            row_data = self._segmento_to_row(segmento)
            
            # Atualizar na planilha
            body = {'values': [row_data]}
            result = self.sheets_service.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.segmentos_worksheet}!A{row_index}:J{row_index}',
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            print(f"✅ Segmento atualizado: {segmento['id']}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar segmento: {e}")
            return False
    
    def delete_segmento(self, segmento_id: str) -> bool:
        """Exclui um segmento (soft delete)"""
        try:
            print(f"🗑️ Excluindo segmento ID: {segmento_id}")
            
            # Buscar segmento
            segmento = self.get_segmento(segmento_id)
            if not segmento:
                return False
            
            # Marcar como inativo
            segmento['ativo'] = False
            segmento['ultimaAtualizacao'] = datetime.now().isoformat()
            
            return self._update_segmento(segmento)
            
        except Exception as e:
            print(f"❌ Erro ao excluir segmento: {e}")
            return False
    
    # ==================== MÉTODOS PARA ATIVIDADES ====================
    
    def get_atividades(self, segmento_id: str = None) -> List[Dict]:
        """Busca todas as atividades ou de um segmento específico"""
        try:
            print(f"📋 Buscando atividades na aba '{self.atividades_worksheet}'...")
            
            result = self.sheets_service.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.atividades_worksheet}!A:L'
            ).execute()
            
            rows = result.get('values', [])
            if not rows:
                print("⚠️ Nenhuma atividade encontrada")
                return []
            
            headers = rows[0]
            atividades = []
            
            for i, row in enumerate(rows[1:], start=2):
                if len(row) > 0 and row[0]:  # Se tem ID
                    atividade = self._row_to_atividade(headers, row, i)
                    if atividade:
                        # Filtrar por segmento se especificado
                        if segmento_id is None or str(atividade.get('segmentoId')) == str(segmento_id):
                            atividades.append(atividade)
            
            print(f"✅ {len(atividades)} atividades carregadas")
            return atividades
            
        except Exception as e:
            print(f"❌ Erro ao buscar atividades: {e}")
            return []
    
    def get_atividade(self, atividade_id: str) -> Optional[Dict]:
        """Busca uma atividade específica por ID"""
        try:
            print(f"🔍 Buscando atividade ID: {atividade_id}")
            
            atividades = self.get_atividades()
            for atividade in atividades:
                if str(atividade.get('id')) == str(atividade_id):
                    print(f"✅ Atividade encontrada: {atividade.get('nome')}")
                    return atividade
            
            print(f"❌ Atividade ID '{atividade_id}' não encontrada")
            return None
            
        except Exception as e:
            print(f"❌ Erro ao buscar atividade: {e}")
            return None
    
    def save_atividade(self, atividade: Dict) -> bool:
        """Salva ou atualiza uma atividade"""
        try:
            print(f"💾 Salvando atividade: {atividade.get('nome')}")
            
            atividade_id = atividade.get('id')
            if atividade_id and str(atividade_id).strip():
                # Atualizar existente
                return self._update_atividade(atividade)
            else:
                # Criar nova
                return self._create_atividade(atividade)
                
        except Exception as e:
            print(f"❌ Erro ao salvar atividade: {e}")
            return False
    
    def _create_atividade(self, atividade: Dict) -> bool:
        """Cria uma nova atividade"""
        try:
            # Gerar ID único
            import random
            timestamp = int(datetime.now().timestamp())
            random_suffix = random.randint(100, 999)
            atividade['id'] = f"ATV{timestamp}{random_suffix}"
            
            # Adicionar timestamps
            atividade['dataCriacao'] = datetime.now().isoformat()
            atividade['ultimaAtualizacao'] = datetime.now().isoformat()
            
            # Buscar nome do segmento se não fornecido
            if atividade.get('segmentoId') and not atividade.get('segmentoNome'):
                segmento = self.get_segmento(atividade['segmentoId'])
                if segmento:
                    atividade['segmentoNome'] = segmento.get('nome', '')
            
            # Converter para linha
            row_data = self._atividade_to_row(atividade)
            
            # Adicionar na planilha
            body = {'values': [row_data]}
            result = self.sheets_service.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.atividades_worksheet}!A:L',
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            print(f"✅ Atividade criada: {atividade['id']}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar atividade: {e}")
            return False
    
    def _update_atividade(self, atividade: Dict) -> bool:
        """Atualiza uma atividade existente"""
        try:
            # Encontrar linha da atividade
            row_index = self._find_atividade_row(atividade['id'])
            if row_index <= 0:
                print(f"❌ Atividade ID '{atividade['id']}' não encontrada para atualização")
                return False
            
            # Atualizar timestamp
            atividade['ultimaAtualizacao'] = datetime.now().isoformat()
            
            # Buscar nome do segmento se não fornecido
            if atividade.get('segmentoId') and not atividade.get('segmentoNome'):
                segmento = self.get_segmento(atividade['segmentoId'])
                if segmento:
                    atividade['segmentoNome'] = segmento.get('nome', '')
            
            # Converter para linha
            row_data = self._atividade_to_row(atividade)
            
            # Atualizar na planilha
            body = {'values': [row_data]}
            result = self.sheets_service.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.atividades_worksheet}!A{row_index}:L{row_index}',
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            print(f"✅ Atividade atualizada: {atividade['id']}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar atividade: {e}")
            return False
    
    def delete_atividade(self, atividade_id: str) -> bool:
        """Exclui uma atividade (soft delete)"""
        try:
            print(f"🗑️ Excluindo atividade ID: {atividade_id}")
            
            # Buscar atividade
            atividade = self.get_atividade(atividade_id)
            if not atividade:
                return False
            
            # Marcar como inativa
            atividade['ativo'] = False
            atividade['ultimaAtualizacao'] = datetime.now().isoformat()
            
            return self._update_atividade(atividade)
            
        except Exception as e:
            print(f"❌ Erro ao excluir atividade: {e}")
            return False
    
    # ==================== MÉTODOS AUXILIARES ====================
    
    def _row_to_segmento(self, headers: List[str], row: List[str], row_number: int) -> Optional[Dict]:
        """Converte linha da planilha para dict de segmento"""
        try:
            segmento = {}
            for i, header in enumerate(headers):
                value = row[i] if i < len(row) else ''
                
                if header == 'ID':
                    segmento['id'] = value
                elif header == 'Nome do Segmento':
                    segmento['nome'] = value
                elif header == 'Descrição':
                    segmento['descricao'] = value
                elif header == 'Código':
                    segmento['codigo'] = value
                elif header == 'Ativo':
                    segmento['ativo'] = str(value).lower() in ['true', '1', 'sim', 'ativo']
                elif header == 'Data de Criação':
                    segmento['dataCriacao'] = value
                elif header == 'Última Atualização':
                    segmento['ultimaAtualizacao'] = value
                elif header == 'Criado Por':
                    segmento['criadoPor'] = value
                elif header == 'Observações':
                    segmento['observacoes'] = value
                elif header == 'Ordem de Exibição':
                    segmento['ordemExibicao'] = int(value) if value and str(value).isdigit() else 0
            
            segmento['_row_number'] = row_number
            return segmento if segmento.get('id') else None
            
        except Exception as e:
            print(f"❌ Erro ao converter linha para segmento: {e}")
            return None
    
    def _segmento_to_row(self, segmento: Dict) -> List[str]:
        """Converte dict de segmento para linha da planilha"""
        return [
            str(segmento.get('id', '')),
            str(segmento.get('nome', '')),
            str(segmento.get('descricao', '')),
            str(segmento.get('codigo', '')),
            'TRUE' if segmento.get('ativo', True) else 'FALSE',
            str(segmento.get('dataCriacao', '')),
            str(segmento.get('ultimaAtualizacao', '')),
            str(segmento.get('criadoPor', '')),
            str(segmento.get('observacoes', '')),
            str(segmento.get('ordemExibicao', 0))
        ]
    
    def _row_to_atividade(self, headers: List[str], row: List[str], row_number: int) -> Optional[Dict]:
        """Converte linha da planilha para dict de atividade"""
        try:
            atividade = {}
            for i, header in enumerate(headers):
                value = row[i] if i < len(row) else ''
                
                if header == 'ID':
                    atividade['id'] = value
                elif header == 'Nome da Atividade':
                    atividade['nome'] = value
                elif header == 'Código CNAE':
                    atividade['codigoCnae'] = value
                elif header == 'Descrição':
                    atividade['descricao'] = value
                elif header == 'Segmento ID':
                    atividade['segmentoId'] = value
                elif header == 'Segmento Nome':
                    atividade['segmentoNome'] = value
                elif header == 'Ativo':
                    atividade['ativo'] = str(value).lower() in ['true', '1', 'sim', 'ativo']
                elif header == 'Data de Criação':
                    atividade['dataCriacao'] = value
                elif header == 'Última Atualização':
                    atividade['ultimaAtualizacao'] = value
                elif header == 'Criado Por':
                    atividade['criadoPor'] = value
                elif header == 'Observações':
                    atividade['observacoes'] = value
                elif header == 'Ordem de Exibição':
                    atividade['ordemExibicao'] = int(value) if value and str(value).isdigit() else 0
            
            atividade['_row_number'] = row_number
            return atividade if atividade.get('id') else None
            
        except Exception as e:
            print(f"❌ Erro ao converter linha para atividade: {e}")
            return None
    
    def _atividade_to_row(self, atividade: Dict) -> List[str]:
        """Converte dict de atividade para linha da planilha"""
        return [
            str(atividade.get('id', '')),
            str(atividade.get('nome', '')),
            str(atividade.get('codigoCnae', '')),
            str(atividade.get('descricao', '')),
            str(atividade.get('segmentoId', '')),
            str(atividade.get('segmentoNome', '')),
            'TRUE' if atividade.get('ativo', True) else 'FALSE',
            str(atividade.get('dataCriacao', '')),
            str(atividade.get('ultimaAtualizacao', '')),
            str(atividade.get('criadoPor', '')),
            str(atividade.get('observacoes', '')),
            str(atividade.get('ordemExibicao', 0))
        ]
    
    def _find_segmento_row(self, segmento_id: str) -> int:
        """Encontra a linha de um segmento específico"""
        try:
            result = self.sheets_service.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.segmentos_worksheet}!A:A'
            ).execute()
            
            rows = result.get('values', [])
            for i, row in enumerate(rows[1:], start=2):
                if len(row) > 0 and str(row[0]) == str(segmento_id):
                    return i
            
            return -1
            
        except Exception as e:
            print(f"❌ Erro ao encontrar linha do segmento: {e}")
            return -1
    
    def _find_atividade_row(self, atividade_id: str) -> int:
        """Encontra a linha de uma atividade específica"""
        try:
            result = self.sheets_service.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.atividades_worksheet}!A:A'
            ).execute()
            
            rows = result.get('values', [])
            for i, row in enumerate(rows[1:], start=2):
                if len(row) > 0 and str(row[0]) == str(atividade_id):
                    return i
            
            return -1
            
        except Exception as e:
            print(f"❌ Erro ao encontrar linha da atividade: {e}")
            return -1
    
    # ==================== MÉTODOS DE CONSULTA ====================
    
    def get_segmentos_ativos(self) -> List[Dict]:
        """Busca apenas segmentos ativos"""
        segmentos = self.get_segmentos()
        return [s for s in segmentos if s.get('ativo', True)]
    
    def get_atividades_ativas(self, segmento_id: str = None) -> List[Dict]:
        """Busca apenas atividades ativas"""
        atividades = self.get_atividades(segmento_id)
        return [a for a in atividades if a.get('ativo', True)]
    
    def search_segmentos(self, term: str) -> List[Dict]:
        """Busca segmentos por termo"""
        segmentos = self.get_segmentos_ativos()
        term_lower = term.lower()
        
        return [s for s in segmentos 
                if term_lower in s.get('nome', '').lower() 
                or term_lower in s.get('descricao', '').lower()
                or term_lower in s.get('codigo', '').lower()]
    
    def search_atividades(self, term: str, segmento_id: str = None) -> List[Dict]:
        """Busca atividades por termo"""
        atividades = self.get_atividades_ativas(segmento_id)
        term_lower = term.lower()
        
        return [a for a in atividades 
                if term_lower in a.get('nome', '').lower() 
                or term_lower in a.get('descricao', '').lower()
                or term_lower in a.get('codigoCnae', '').lower()]
