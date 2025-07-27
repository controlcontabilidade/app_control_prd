"""
Serviço para gerenciar atas de reunião usando Google Sheets
"""
import json
from datetime import datetime
from services.google_sheets_service_account import GoogleSheetsServiceAccountService

class MeetingService:
    def __init__(self, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id
        self.worksheet_name = 'Atas_Reuniao'
        self.gs_service = GoogleSheetsServiceAccountService(spreadsheet_id)
        self._ensure_worksheet_exists()
    
    def _ensure_worksheet_exists(self):
        """Garante que a aba de atas existe e tem os cabeçalhos corretos"""
        try:
            # Verifica se a aba existe, se não, cria
            if not self.gs_service.worksheet_exists(self.worksheet_name):
                print(f"📋 Criando aba '{self.worksheet_name}' no Google Sheets...")
                self.gs_service.create_worksheet(self.worksheet_name)
            
            # Obtém worksheet para trabalhar com ela
            worksheet = self.gs_service.get_worksheet(self.worksheet_name)
            
            # Verifica se já existem cabeçalhos
            headers = worksheet.row_values(1) if worksheet.row_count > 0 else []
            
            if not headers:
                print(f"📋 Adicionando cabeçalhos na aba '{self.worksheet_name}'...")
                # Cria os cabeçalhos se a planilha estiver vazia
                headers = [
                    'ID_Ata',
                    'ID_Cliente', 
                    'Nome_Cliente',
                    'Data_Reuniao',
                    'Horario',
                    'Participantes',
                    'Topicos_Discutidos',
                    'Decisoes_Tomadas',
                    'Proximos_Passos',
                    'Data_Criacao'
                ]
                
                # Adiciona os cabeçalhos
                worksheet.insert_row(headers, 1)
                print("✅ Cabeçalhos da planilha de Atas criados")
                
        except Exception as e:
            print(f"❌ Erro ao configurar aba de atas: {e}")
            raise
    
    def save_meeting(self, meeting_data):
        """Salva uma ata de reunião na planilha"""
        try:
            print(f"💾 Salvando ata de reunião para cliente: {meeting_data.get('client_name')}")
            
            # Gera ID único para a ata
            meeting_id = f"ATA_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Prepara os dados para inserção
            row_data = [
                meeting_id,
                meeting_data.get('client_id', ''),
                meeting_data.get('client_name', ''),
                meeting_data.get('date', ''),
                meeting_data.get('time', ''),
                meeting_data.get('participants', ''),
                meeting_data.get('topics', ''),
                meeting_data.get('decisions', ''),
                meeting_data.get('next_steps', ''),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
            
            print(f"📋 Dados da ata: {row_data}")
            
            # Obtém worksheet para adicionar a linha
            worksheet = self.gs_service.get_worksheet(self.worksheet_name)
            
            # Adiciona a nova linha
            success = worksheet.insert_row(row_data)
            
            if success:
                print(f"✅ Ata {meeting_id} salva com sucesso!")
                return meeting_id
            else:
                print(f"❌ Erro ao salvar ata {meeting_id}")
                return None
                
        except Exception as e:
            print(f"❌ Erro detalhado ao salvar ata: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_client_meetings(self, client_id):
        """Busca todas as atas de um cliente específico"""
        try:
            print(f"🔍 Buscando atas para cliente ID: {client_id}")
            
            # Obtém worksheet e busca todos os dados
            worksheet = self.gs_service.get_worksheet(self.worksheet_name)
            all_data = worksheet.get_all_values()
            
            if not all_data or len(all_data) <= 1:
                print("📋 Nenhuma ata encontrada")
                return []
            
            # Pula a linha de cabeçalho
            headers = all_data[0]
            rows = all_data[1:]
            
            client_meetings = []
            for row in rows:
                if len(row) >= 10 and row[1] == str(client_id):  # ID_Cliente
                    meeting = {
                        'id': row[0],
                        'client_id': row[1],
                        'client_name': row[2],
                        'date': row[3],
                        'time': row[4],
                        'participants': row[5],
                        'topics': row[6],
                        'decisions': row[7],
                        'next_steps': row[8],
                        'created_at': row[9] if len(row) > 9 else ''
                    }
                    client_meetings.append(meeting)
            
            print(f"📊 Encontradas {len(client_meetings)} atas para o cliente")
            return sorted(client_meetings, key=lambda x: x.get('date', ''), reverse=True)
            
        except Exception as e:
            print(f"❌ Erro ao buscar atas do cliente: {e}")
            return []
    
    def get_all_meetings(self):
        """Busca todas as atas de reunião"""
        try:
            all_data = self.gs_service.get_all_values()
            
            if not all_data or len(all_data) <= 1:
                return []
            
            # Pula a linha de cabeçalho
            headers = all_data[0]
            rows = all_data[1:]
            
            meetings = []
            for row in rows:
                if len(row) >= 10:
                    meeting = {
                        'id': row[0],
                        'client_id': row[1],
                        'client_name': row[2],
                        'date': row[3],
                        'time': row[4],
                        'participants': row[5],
                        'topics': row[6],
                        'decisions': row[7],
                        'next_steps': row[8],
                        'created_at': row[9] if len(row) > 9 else ''
                    }
                    meetings.append(meeting)
            
            return sorted(meetings, key=lambda x: x.get('date', ''), reverse=True)
            
        except Exception as e:
            print(f"❌ Erro ao buscar todas as atas: {e}")
            return []
