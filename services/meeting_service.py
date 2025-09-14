"""
Serviço para gerenciar atas de reunião usando Google Sheets
"""
import json
import re
from datetime import datetime
from services.google_sheets_service_account import GoogleSheetsServiceAccountService

class MeetingService:
    def __init__(self, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id
        self.worksheet_name = 'Atas_Reuniao'
        self.gs_service = GoogleSheetsServiceAccountService(spreadsheet_id)
        self._ensure_worksheet_exists()
    
    def _clean_html_content(self, html_content):
        """Remove tags HTML e converte para texto limpo mantendo formatação básica"""
        if not html_content:
            return ''
        
        # Converter quebras de linha HTML
        text = html_content.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
        text = text.replace('</p><p>', '\n\n').replace('<p>', '').replace('</p>', '\n')
        
        # Converter listas
        text = text.replace('<ul>', '').replace('</ul>', '\n')
        text = text.replace('<ol>', '').replace('</ol>', '\n')
        text = text.replace('<li>', '• ').replace('</li>', '\n')
        
        # Remover outras tags HTML mantendo o conteúdo
        text = re.sub(r'<[^>]+>', '', text)
        
        # Limpar entidades HTML
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        
        # Limpar espaços extras e quebras de linha duplas
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = text.strip()
        
        return text
    
    def _ensure_worksheet_exists(self):
        """Garante que a aba de atas existe e tem os cabeçalhos corretos"""
        try:
            # Verifica se a aba existe, se não, cria
            if not self.gs_service.worksheet_exists(self.worksheet_name):
                print(f"📋 Criando aba '{self.worksheet_name}' no Google Sheets...")
                self.gs_service.create_worksheet(self.worksheet_name)
            
            # Obtém worksheet para trabalhar com ela
            worksheet = self.gs_service.get_worksheet(self.worksheet_name)
            
            # Define os cabeçalhos corretos
            correct_headers = [
                'ID_Ata',
                'ID_Cliente', 
                'Nome_Cliente',
                'Data_Reuniao',
                'Horario',
                'Participantes',
                'Topicos_Discutidos',
                'Topicos_Formatados',
                'Decisoes_Tomadas',
                'Proximos_Passos',
                'Data_Criacao',
                'Hora_Criacao',
                'Usuario_Criacao',
                'Data_Atualizacao',
                'Hora_Atualizacao',
                'Usuario_Atualizacao'
            ]
            
            # Verifica se já existem cabeçalhos
            current_headers = worksheet.row_values(1) if worksheet.row_count > 0 else []
            
            # Se não há cabeçalhos ou estão incorretos, atualiza
            if not current_headers or current_headers != correct_headers:
                print(f"📋 {'Criando' if not current_headers else 'Atualizando'} cabeçalhos na aba '{self.worksheet_name}'...")
                
                # Usar a API direta para atualizar os cabeçalhos
                range_name = f"{self.worksheet_name}!A1:P1"
                try:
                    self.gs_service.service.spreadsheets().values().update(
                        spreadsheetId=self.gs_service.spreadsheet_id,
                        range=range_name,
                        valueInputOption='USER_ENTERED',
                        body={'values': [correct_headers]}
                    ).execute()
                    
                    print("✅ Cabeçalhos da planilha de Atas configurados corretamente")
                    print(f"📋 Cabeçalhos: {correct_headers}")
                except Exception as update_error:
                    print(f"❌ Erro ao atualizar cabeçalhos: {update_error}")
                    # Fallback: usar insert_row se update falhar
                    if not current_headers:
                        worksheet.insert_row(correct_headers, 1)
                        print("✅ Cabeçalhos inseridos usando fallback")
            else:
                print("✅ Cabeçalhos da aba de Atas já estão corretos")
                
        except Exception as e:
            print(f"❌ Erro ao configurar aba de atas: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def save_meeting(self, meeting_data, user_info=None):
        """Salva uma ata de reunião na planilha"""
        try:
            print(f"💾 Salvando ata de reunião para cliente: {meeting_data.get('client_name')}")
            
            # Gera ID único para a ata
            meeting_id = f"ATA_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Informações de auditoria
            now = datetime.now()
            current_date = now.strftime('%d/%m/%Y')  # Formato brasileiro
            current_time = now.strftime('%H:%M:%S')
            current_user = user_info.get('name', 'Sistema') if user_info else 'Sistema'
            
            # Limpar conteúdo HTML dos campos de texto (para busca/texto simples)
            topics_clean = self._clean_html_content(meeting_data.get('topics', ''))
            
            # Manter conteúdo original formatado para visualização
            topics_formatted = meeting_data.get('topics', '')
            
            # Prepara os dados para inserção na ordem correta dos cabeçalhos
            row_data = [
                meeting_id,                           # ID_Ata
                meeting_data.get('client_id', ''),    # ID_Cliente
                meeting_data.get('client_name', ''),  # Nome_Cliente
                meeting_data.get('date', ''),         # Data_Reuniao
                meeting_data.get('time', ''),         # Horario
                meeting_data.get('participants', ''), # Participantes
                topics_clean,                         # Topicos_Discutidos (HTML limpo)
                topics_formatted,                     # Topicos_Formatados (HTML original)
                '',                                   # Decisoes_Tomadas (vazio)
                '',                                   # Proximos_Passos (vazio)
                current_date,                         # Data_Criacao
                current_time,                         # Hora_Criacao
                current_user,                         # Usuario_Criacao
                '',                                   # Data_Atualizacao (vazio na criação)
                '',                                   # Hora_Atualizacao (vazio na criação)
                ''                                    # Usuario_Atualizacao (vazio na criação)
            ]
            
            print(f"📋 Dados da ata (limpos): {row_data}")
            
            # Obtém worksheet para adicionar a linha
            worksheet = self.gs_service.get_worksheet(self.worksheet_name)
            
            # Encontra a próxima linha disponível (após os cabeçalhos)
            current_row_count = worksheet.row_count
            next_row = current_row_count + 1
            
            print(f"📋 Inserindo ata na linha {next_row} (total atual: {current_row_count})")
            
            # Usar append em vez de insert_row para adicionar no final
            range_name = f"{self.worksheet_name}!A{next_row}:P{next_row}"
            body = {'values': [row_data]}
            
            result = self.gs_service.service.spreadsheets().values().update(
                spreadsheetId=self.gs_service.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            success = result.get('updatedRows', 0) > 0
            
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
                        'topics_formatted': row[7] if len(row) > 7 else row[6],  # Usar formatado se disponível
                        'decisions': row[8] if len(row) > 8 else '',
                        'next_steps': row[9] if len(row) > 9 else '',
                        'created_date': row[10] if len(row) > 10 else '',
                        'created_time': row[11] if len(row) > 11 else '',
                        'created_by': row[12] if len(row) > 12 else '',
                        'updated_date': row[13] if len(row) > 13 else '',
                        'updated_time': row[14] if len(row) > 14 else '',
                        'updated_by': row[15] if len(row) > 15 else ''
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
            # Obtém worksheet e busca todos os dados
            worksheet = self.gs_service.get_worksheet(self.worksheet_name)
            all_data = worksheet.get_all_values()
            
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
                        'created_date': row[9] if len(row) > 9 else '',
                        'created_time': row[10] if len(row) > 10 else '',
                        'created_by': row[11] if len(row) > 11 else ''
                    }
                    meetings.append(meeting)
            
            return sorted(meetings, key=lambda x: x.get('date', ''), reverse=True)
            
        except Exception as e:
            print(f"❌ Erro ao buscar todas as atas: {e}")
            return []
