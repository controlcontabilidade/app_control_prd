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
            expected_headers = ['ID', 'Nome', 'Descricao', 'Link', 'Ativo', 'Ordem', 'Data_Criacao', 'Criado_Por', 'Usuarios_Autorizados']
            
            if not headers or headers != expected_headers:
                # Adiciona os cabeçalhos usando o range correto da aba
                range_name = f'{self.worksheet_name}!A1:I1'
                self.sheets_service.update_range(range_name, [expected_headers])
                print(f"✅ Cabeçalhos da planilha {self.worksheet_name} configurados")
            
        except Exception as e:
            # Se a planilha não existe, cria uma nova
            try:
                self.sheets_service.create_worksheet(self.worksheet_name, 1000, 8)
                worksheet = self.sheets_service.get_worksheet(self.worksheet_name)
                
                # Adiciona cabeçalhos
                headers = ['ID', 'Nome', 'Descricao', 'Link', 'Ativo', 'Ordem', 'Data_Criacao', 'Criado_Por', 'Usuarios_Autorizados']
                range_name = f'{self.worksheet_name}!A1:I1'
                self.sheets_service.update_range(range_name, [headers])
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
                print("🔍 Debug: Nenhum relatório encontrado na planilha")
                return []
            
            headers = all_values[0]
            reports = all_values[1:]
            
            print(f"🔍 Debug: {len(reports)} linhas de relatórios encontradas")
            print(f"🔍 Debug: Cabeçalhos: {headers}")
            
            report_list = []
            for i, report_row in enumerate(reports):
                if len(report_row) >= len(headers) and any(cell.strip() for cell in report_row[:3]):  # Verifica se não é linha vazia
                    report_data = {}
                    for j, header in enumerate(headers):
                        value = report_row[j] if j < len(report_row) else ''
                        
                        # Converter data_criacao para datetime se não estiver vazia
                        if header.lower() == 'data_criacao' and value:
                            try:
                                report_data[header.lower()] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                            except ValueError:
                                # Se não conseguir converter, deixa como string
                                report_data[header.lower()] = value
                        else:
                            report_data[header.lower()] = value
                    
                    # Debug do valor 'ativo'
                    ativo_value = report_data.get('ativo', '')
                    print(f"🔍 Debug: Relatório '{report_data.get('nome')}' - Ativo: '{ativo_value}' (tipo: {type(ativo_value)})")
                    
                    # Filtrar apenas ativos se solicitado
                    if only_active:
                        is_active = ativo_value.lower().strip() == 'sim'
                        print(f"🔍 Debug: Filtrando ativos - '{ativo_value}' -> is_active: {is_active}")
                        if not is_active:
                            continue
                        
                    report_list.append(report_data)
            
            # Ordenar por ordem
            report_list.sort(key=lambda x: int(x.get('ordem', '999') or '999'))
            return report_list
            
        except Exception as e:
            print(f"Erro ao listar relatórios: {e}")
            return []
    
    def user_has_access(self, report, username):
        """Verifica se o usuário tem acesso ao relatório"""
        try:
            usuarios_autorizados = report.get('usuarios_autorizados', 'todos').lower()
            
            # Se for 'todos', qualquer um pode acessar
            if usuarios_autorizados == 'todos':
                return True
            
            # Se tiver lista de usuários, verifica se o usuário está na lista
            if username and username.lower() in usuarios_autorizados.lower():
                return True
                
            # Se for admin, sempre tem acesso
            if username and 'admin' in username.lower():
                return True
            
            return False
            
        except Exception as e:
            print(f"Erro ao verificar acesso do usuário: {e}")
            return False
    
    def get_available_users(self):
        """Retorna lista de usuários disponíveis no sistema"""
        try:
            users_list = ['todos']  # Sempre incluir 'todos'
            
            try:
                # Primeira tentativa: buscar da aba 'Usuarios' se existir
                users_worksheet = self.sheets_service.get_worksheet('Usuarios')
                users_data = users_worksheet.get_all_values()
                
                if len(users_data) > 1:
                    headers = users_data[0]
                    # Procura coluna de nome de usuário
                    username_col = -1
                    for i, header in enumerate(headers):
                        if header.lower() in ['usuario', 'username', 'nome_usuario', 'login', 'nome']:
                            username_col = i
                            break
                    
                    if username_col >= 0:
                        for row in users_data[1:]:
                            if len(row) > username_col and row[username_col].strip():
                                users_list.append(row[username_col].strip())
                
            except Exception:
                # Segunda tentativa: buscar da planilha principal (Clientes)
                try:
                    main_worksheet = self.sheets_service.get_worksheet('Clientes')
                    clients_data = main_worksheet.get_all_values()
                    
                    if len(clients_data) > 1:
                        headers = clients_data[0]
                        # Procura coluna de responsável ou contato
                        contact_col = -1
                        for i, header in enumerate(headers):
                            if header.lower() in ['responsavel', 'contato', 'nome_responsavel', 'usuario_responsavel']:
                                contact_col = i
                                break
                        
                        if contact_col >= 0:
                            for row in clients_data[1:]:
                                if len(row) > contact_col and row[contact_col].strip():
                                    users_list.append(row[contact_col].strip())
                
                except Exception:
                    # Lista padrão se não conseguir acessar nenhuma planilha
                    users_list.extend(['admin', 'gerente', 'operador', 'usuario'])
            
            # Remove duplicatas e ordena
            users_list = list(set(users_list))
            users_list.sort(key=lambda x: (x != 'todos', x.lower()))  # 'todos' sempre primeiro
            
            # Limitar a 20 usuários para não sobrecarregar a interface
            if len(users_list) > 21:  # 20 + 'todos'
                users_list = users_list[:21]
            
            return users_list
            
        except Exception as e:
            print(f"Erro ao buscar usuários: {e}")
            return ['todos', 'admin', 'gerente', 'operador', 'usuario']
    
    def create_report(self, nome, descricao, link, ativo='Sim', ordem=1, criado_por='Sistema', usuarios_autorizados='todos'):
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
                criado_por,
                usuarios_autorizados
            ]
            
            # Adiciona nova linha usando update_range para a próxima linha vazia
            next_row = len(all_values) + 1
            range_name = f'{self.worksheet_name}!A{next_row}:I{next_row}'
            self.sheets_service.update_range(range_name, [report_data])
            
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
    
    def get_report_by_id(self, report_id):
        """Busca relatório por ID"""
        try:
            worksheet = self.sheets_service.get_worksheet(self.worksheet_name)
            all_values = worksheet.get_all_values()
            
            if len(all_values) <= 1:
                return None
            
            headers = all_values[0]
            reports = all_values[1:]
            
            for report_row in reports:
                if len(report_row) >= 2 and report_row[0] == str(report_id):
                    report_data = {}
                    for i, header in enumerate(headers):
                        if i < len(report_row):
                            value = report_row[i]
                            
                            # Converter data_criacao para datetime se não estiver vazia
                            if header.lower() == 'data_criacao' and value:
                                try:
                                    report_data[header.lower()] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                                except ValueError:
                                    # Se não conseguir converter, deixa como string
                                    report_data[header.lower()] = value
                            else:
                                report_data[header.lower()] = value
                    return report_data
            
            return None
            
        except Exception as e:
            print(f"Erro ao buscar relatório: {e}")
            return None

    def update_report(self, report_id, nome, descricao, link, ativo='Sim', ordem=1, usuarios_autorizados='todos'):
        """Atualiza um relatório existente"""
        try:
            worksheet = self.sheets_service.get_worksheet(self.worksheet_name)
            all_values = worksheet.get_all_values()
            
            if len(all_values) <= 1:
                return {
                    'success': False,
                    'message': 'Nenhum relatório encontrado para atualizar'
                }
            
            # Procura o relatório para atualizar
            for row_index, report_row in enumerate(all_values[1:], start=2):
                if len(report_row) >= 2 and report_row[0] == str(report_id):
                    # Atualiza os dados (mantém ID, data de criação e criado por)
                    updated_data = [
                        str(report_id),  # ID
                        nome,            # Nome
                        descricao,       # Descrição
                        link,            # Link
                        ativo,           # Ativo
                        str(ordem),      # Ordem
                        report_row[6] if len(report_row) > 6 else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Data criação original
                        report_row[7] if len(report_row) > 7 else 'Sistema',  # Criado por original
                        usuarios_autorizados  # Usuários autorizados
                    ]
                    
                    # Atualiza a linha
                    range_name = f'{self.worksheet_name}!A{row_index}:I{row_index}'
                    self.sheets_service.update_range(range_name, [updated_data])
                    
                    return {
                        'success': True,
                        'message': 'Relatório atualizado com sucesso!'
                    }
            
            return {
                'success': False,
                'message': 'Relatório não encontrado'
            }
            
        except Exception as e:
            print(f"Erro ao atualizar relatório: {e}")
            return {
                'success': False,
                'message': f'Erro ao atualizar relatório: {str(e)}'
            }

    def delete_report(self, report_id):
        """Deleta um relatório"""
        try:
            worksheet = self.sheets_service.get_worksheet(self.worksheet_name)
            all_values = worksheet.get_all_values()
            
            if len(all_values) <= 1:
                return {
                    'success': False,
                    'message': 'Nenhum relatório encontrado para deletar'
                }
            
            # Procura o relatório para deletar
            for row_index, report_row in enumerate(all_values[1:], start=2):
                if len(report_row) >= 2 and report_row[0] == str(report_id):
                    # Remove a linha substituindo por valores vazios
                    empty_row = [''] * 9  # 9 colunas vazias
                    range_name = f'{self.worksheet_name}!A{row_index}:I{row_index}'
                    self.sheets_service.update_range(range_name, [empty_row])
                    
                    return {
                        'success': True,
                        'message': 'Relatório deletado com sucesso!'
                    }
            
            return {
                'success': False,
                'message': 'Relatório não encontrado'
            }
            
        except Exception as e:
            print(f"Erro ao deletar relatório: {e}")
            return {
                'success': False,
                'message': f'Erro ao deletar relatório: {str(e)}'
            }
