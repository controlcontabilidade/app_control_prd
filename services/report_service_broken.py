"""
Serviço para gerenciar relatórios do Power BI no sistema SIGEC
"""
from services.google_sheets_service_account import GoogleSheetsServiceAccountService
from datetime import datetime
import logging

class ReportService:
    def __init__(self, spreadsheet_id=None):
        self.spreadsheet_id = spreadsheet_id or '1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s'
        self.sheets_service = GoogleSheetsServiceAccountService(self.spreadsheet_id)
        self.worksheet_name = 'Relatorios'
    
    def _ensure_worksheet_exists(self):
        """Garante que a planilha de relatórios existe com os cabeçalhos corretos"""
        try:
            # Tenta obter a planilha
            worksheet = self.sheets_service.get_worksheet(self.worksheet_name)
            
            # Verifica se já tem cabeçalhos
            headers = worksheet.row_values(1)
            expected_headers = ['ID', 'Nome', 'Descricao', 'Link', 'Ativo', 'Ordem', 'Data_Criacao', 'Criado_Por']
            
            if not headers or headers != expected_headers:
                # Adiciona os cabeçalhos
                worksheet.update('A1:H1', [expected_headers])
                print(f"✅ Cabeçalhos da planilha {self.worksheet_name} configurados")
            
        except Exception as e:
            # Se a planilha não existe, cria uma nova
            try:
                self.sheets_service.create_worksheet(self.worksheet_name, 1000, 8)
                worksheet = self.sheets_service.get_worksheet(self.worksheet_name)
                
                # Adiciona cabeçalhos
                headers = ['ID', 'Nome', 'Descricao', 'Link', 'Ativo', 'Ordem', 'Data_Criacao', 'Criado_Por']
                worksheet.update('A1:H1', [headers])
                print(f"✅ Nova planilha {self.worksheet_name} criada com cabeçalhos")
                
            except Exception as create_error:
                print(f"❌ Erro ao criar planilha {self.worksheet_name}: {create_error}")
                raise
    
    def list_reports(self, only_active=False):
        """Lista todos os relatórios"""
        try:
            self._ensure_worksheet_exists()
            worksheet = self.sheets_service.get_worksheet(self.worksheet_name)
            all_values = worksheet.get_all_values()
            
            if len(all_values) <= 1:
                return []
            
            headers = all_values[0]
            reports = all_values[1:]
            
            report_list = []
            for report_row in reports:
                if len(report_row) >= len(headers):
                    report_data = {}
                    for i, header in enumerate(headers):
                        value = report_row[i] if i < len(report_row) else ''
                        
                        # Converter data_criacao para datetime se não estiver vazia
                        if header.lower() == 'data_criacao' and value:
                            try:
                                report_data[header.lower()] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                            except ValueError:
                                # Se não conseguir converter, deixa como string
                                report_data[header.lower()] = value
                        else:
                            report_data[header.lower()] = value
                    
                    # Filtrar apenas ativos se solicitado
                    if only_active and report_data.get('ativo', '').lower() != 'sim':
                        continue
                        
                    report_list.append(report_data)
            
            # Ordenar por ordem
            report_list.sort(key=lambda x: int(x.get('ordem', '999') or '999'))
            return report_list
            
        except Exception as e:
            print(f"Erro ao listar relatórios: {e}")
            return []
    
    def create_report(self, nome, descricao, link, ativo='Sim', ordem=1, criado_por='Sistema'):
        """Cria um novo relatório"""
        try:
            self._ensure_worksheet_exists()
            worksheet = self.sheets_service.get_worksheet(self.worksheet_name)
            
            # Gera novo ID
            all_values = worksheet.get_all_values()
            new_id = len(all_values)  # Número da próxima linha
            
            # Dados do novo relatório
            report_data = [
                str(new_id),
                nome,
                descricao,
                link,
                ativo,
                str(ordem),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                criado_por
            ]
            
            # Adiciona nova linha
            worksheet.append_row(report_data)
            
            return {
                'success': True,
                'message': 'Relatório criado com sucesso!',
                'id': new_id
            }
            
        except Exception as e:
            print(f"Erro ao criar relatório: {e}")
            return {
                'success': False,
                'message': f'Erro ao criar relatório: {str(e)}'
            }
