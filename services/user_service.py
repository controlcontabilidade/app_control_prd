"""
Serviço para gerenciar usuários do sistema SIGEC
"""
import hashlib
import secrets
from services.google_sheets_service_account import GoogleSheetsServiceAccountService

class UserService:
    def __init__(self, spreadsheet_id=None):
        self.spreadsheet_id = spreadsheet_id or '1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s'
        self.sheets_service = GoogleSheetsServiceAccountService(self.spreadsheet_id)
        self.worksheet_name = 'Usuarios'
    
    def _hash_password(self, password):
        """Gera hash da senha usando SHA256 com salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def _verify_password(self, password, stored_hash):
        """Verifica se a senha corresponde ao hash armazenado"""
        try:
            salt, stored_password_hash = stored_hash.split(':')
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return password_hash == stored_password_hash
        except:
            return False
    
    def _ensure_worksheet_exists(self):
        """Garante que a planilha de usuários existe com os cabeçalhos corretos"""
        try:
            # Verifica se a aba existe, se não, cria
            if not self.sheets_service.worksheet_exists(self.worksheet_name):
                print(f"📋 Criando aba '{self.worksheet_name}' no Google Sheets...")
                self.sheets_service.create_worksheet(self.worksheet_name)
            
            # Tenta acessar a planilha
            worksheet = self.sheets_service.get_worksheet(self.worksheet_name)
            
            # Verifica se tem cabeçalhos
            headers = worksheet.row_values(1) if worksheet.row_count > 0 else []
            
            if not headers:
                print(f"📋 Adicionando cabeçalhos na aba '{self.worksheet_name}'...")
                # Adiciona cabeçalhos se não existirem - versão atualizada com sistemas e permissões
                headers = [
                    'ID', 'Nome', 'Email', 'Usuario', 'Senha_Hash', 'Perfil', 'Ativo', 
                    'Data_Criacao', 'Ultimo_Login', 'Sistemas_Acesso', 'Permissoes_SIGEC'
                ]
                worksheet.insert_row(headers, 1)
                
                print(f"👤 Criando usuário admin padrão...")
                # Cria usuário admin padrão se não existir com novos campos
                admin_password_hash = self._hash_password('admin123')
                admin_data = [
                    '1',
                    'Administrador',
                    'admin@sigec.com',
                    'admin',
                    admin_password_hash,
                    'Administrador',
                    'Sim',
                    '2024-01-01',
                    '',  # Ultimo_Login
                    'sigec,operacao-fiscal,gestao-operacional,gestao-financeira',  # Sistemas_Acesso
                    'TOTAL_CADASTROS'  # Permissoes_SIGEC
                ]
                worksheet.insert_row(admin_data, 2)
                print(f"✅ Usuário admin criado com sucesso!")
                
        except Exception as e:
            print(f"❌ Erro ao criar planilha de usuários: {e}")
            raise
    
    def authenticate_user(self, username, password):
        """Autentica um usuário"""
        try:
            print(f"🔐 Tentando autenticar usuário: {username}")
            self._ensure_worksheet_exists()
            worksheet = self.sheets_service.get_worksheet(self.worksheet_name)
            
            # Busca todos os usuários
            all_values = worksheet.get_all_values()
            print(f"📊 Encontrados {len(all_values)} registros na aba Usuarios")
            
            if len(all_values) <= 1:  # Só cabeçalho
                print("⚠️ Nenhum usuário encontrado além dos cabeçalhos")
                return None
            
            headers = all_values[0]
            users = all_values[1:]
            print(f"👥 Processando {len(users)} usuários")
            
            # Encontra índices das colunas
            usuario_idx = headers.index('Usuario')
            senha_idx = headers.index('Senha_Hash')
            ativo_idx = headers.index('Ativo')
            
            for i, user_row in enumerate(users):
                print(f"🔍 Verificando usuário {i+1}: {user_row[usuario_idx] if len(user_row) > usuario_idx else 'N/A'}")
                
                if (len(user_row) > max(usuario_idx, senha_idx, ativo_idx) and 
                    user_row[usuario_idx].lower() == username.lower() and
                    user_row[ativo_idx].lower() == 'sim'):
                    
                    print(f"✅ Usuário encontrado, verificando senha...")
                    # Verifica a senha
                    if self._verify_password(password, user_row[senha_idx]):
                        print(f"✅ Senha correta para usuário: {username}")
                        # Retorna dados do usuário
                        user_data = {}
                        for j, header in enumerate(headers):
                            if j < len(user_row):
                                user_data[header.lower()] = user_row[j]
                        
                        # Atualiza último login
                        self._update_last_login(user_data['id'])
                        
                        return user_data
                    else:
                        print(f"❌ Senha incorreta para usuário: {username}")
            
            print(f"❌ Usuário não encontrado ou inativo: {username}")
            return None
            
        except Exception as e:
            print(f"❌ Erro na autenticação: {e}")
            return None
    
    def _update_last_login(self, user_id):
        """Atualiza o último login do usuário"""
        try:
            from datetime import datetime
            worksheet = self.sheets_service.get_worksheet(self.worksheet_name)
            all_values = worksheet.get_all_values()
            
            if len(all_values) <= 1:
                return
            
            headers = all_values[0]
            id_idx = headers.index('ID')
            ultimo_login_idx = headers.index('Ultimo_Login')
            
            for i, row in enumerate(all_values[1:], 2):  # Começa da linha 2
                if len(row) > id_idx and row[id_idx] == str(user_id):
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    worksheet.update_cell(i, ultimo_login_idx + 1, current_time)
                    break
                    
        except Exception as e:
            print(f"Erro ao atualizar último login: {e}")
    
    def get_user_by_id(self, user_id):
        """Busca usuário por ID"""
        try:
            worksheet = self.sheets_service.get_worksheet(self.worksheet_name)
            all_values = worksheet.get_all_values()
            
            if len(all_values) <= 1:
                return None
            
            headers = all_values[0]
            users = all_values[1:]
            
            id_idx = headers.index('ID')
            
            for user_row in users:
                if len(user_row) > id_idx and user_row[id_idx] == str(user_id):
                    user_data = {}
                    for i, header in enumerate(headers):
                        if i < len(user_row):
                            user_data[header.lower()] = user_row[i]
                    return user_data
            
            return None
            
        except Exception as e:
            print(f"Erro ao buscar usuário: {e}")
            return None
    
    def create_user(self, nome, email, usuario, senha, perfil='Usuario', sistemas_acesso='sigec', permissoes_sigec='VISUALIZADOR'):
        """Cria um novo usuário com sistemas e permissões"""
        try:
            self._ensure_worksheet_exists()
            worksheet = self.sheets_service.get_worksheet(self.worksheet_name)
            
            # Verifica se usuário já existe
            all_values = worksheet.get_all_values()
            if len(all_values) > 1:
                headers = all_values[0]
                users = all_values[1:]
                usuario_idx = headers.index('Usuario')
                email_idx = headers.index('Email')
                
                for user_row in users:
                    if (len(user_row) > max(usuario_idx, email_idx) and 
                        (user_row[usuario_idx].lower() == usuario.lower() or
                         user_row[email_idx].lower() == email.lower())):
                        return {'success': False, 'message': 'Usuário ou email já existe'}
            
            # Gera novo ID
            new_id = len(all_values)  # Número da próxima linha
            
            # Cria hash da senha
            password_hash = self._hash_password(senha)
            
            # Dados do novo usuário
            from datetime import datetime
            user_data = [
                str(new_id),
                nome,
                email,
                usuario,
                password_hash,
                perfil,
                'Sim',
                datetime.now().strftime('%Y-%m-%d'),
                '',  # Ultimo_Login
                sistemas_acesso,  # Sistemas_Acesso
                permissoes_sigec  # Permissoes_SIGEC
            ]
            
            # Adiciona à planilha
            worksheet.insert_row(user_data, len(all_values) + 1)
            
            return {'success': True, 'message': 'Usuário criado com sucesso', 'user_id': new_id}
            
        except Exception as e:
            print(f"Erro ao criar usuário: {e}")
            return {'success': False, 'message': f'Erro ao criar usuário: {str(e)}'}
    
    def list_users(self):
        """Lista todos os usuários (sem senhas)"""
        try:
            worksheet = self.sheets_service.get_worksheet(self.worksheet_name)
            all_values = worksheet.get_all_values()
            
            if len(all_values) <= 1:
                return []
            
            headers = all_values[0]
            users = all_values[1:]
            
            user_list = []
            for user_row in users:
                user_data = {}
                for i, header in enumerate(headers):
                    if i < len(user_row) and header.lower() != 'senha_hash':
                        user_data[header.lower()] = user_row[i]
                
                # Filtrar usuários vazios ou inválidos
                # Verificar se tem campos essenciais preenchidos
                if (user_data.get('nome', '').strip() and 
                    user_data.get('email', '').strip() and 
                    user_data.get('usuario', '').strip() and
                    user_data.get('nome', '').lower() not in ['nome', 'id'] and  # Evitar header rows
                    user_data.get('email', '').lower() not in ['email', 'e-mail']):  # Evitar header rows
                    
                    user_list.append(user_data)
            
            return user_list
            
        except Exception as e:
            print(f"Erro ao listar usuários: {e}")
            return []

    def update_user(self, user_id, nome, email, usuario, perfil, ativo, nova_senha=None, sistemas_acesso='sigec', permissoes_sigec='VISUALIZADOR'):
        """Atualiza os dados de um usuário com novos campos"""
        try:
            self._ensure_worksheet_exists()
            worksheet = self.sheets_service.get_worksheet(self.worksheet_name)
            all_values = worksheet.get_all_values()
            
            if len(all_values) <= 1:
                return {'success': False, 'message': 'Usuário não encontrado'}
            
            headers = all_values[0]
            users = all_values[1:]
            
            # Encontra índices das colunas
            id_idx = headers.index('ID')
            nome_idx = headers.index('Nome')
            email_idx = headers.index('Email')
            usuario_idx = headers.index('Usuario')
            senha_idx = headers.index('Senha_Hash')
            perfil_idx = headers.index('Perfil')
            ativo_idx = headers.index('Ativo')
            
            # Índices dos novos campos
            sistemas_idx = headers.index('Sistemas_Acesso') if 'Sistemas_Acesso' in headers else None
            permissoes_idx = headers.index('Permissoes_SIGEC') if 'Permissoes_SIGEC' in headers else None
            
            # Verifica se email ou usuário já existem (exceto para o próprio usuário)
            for i, user_row in enumerate(users):
                if (len(user_row) > max(usuario_idx, email_idx, id_idx) and 
                    user_row[id_idx] != str(user_id)):
                    if (user_row[usuario_idx].lower() == usuario.lower() or
                        user_row[email_idx].lower() == email.lower()):
                        return {'success': False, 'message': 'Usuário ou email já existe'}
            
            # Encontra e atualiza o usuário
            for i, user_row in enumerate(users):
                if len(user_row) > id_idx and user_row[id_idx] == str(user_id):
                    row_number = i + 2  # +2 porque lista começa em 0 e planilha em 1, mais linha de cabeçalho
                    
                    # Atualiza os campos básicos
                    worksheet.update_cell(row_number, nome_idx + 1, nome)
                    worksheet.update_cell(row_number, email_idx + 1, email)
                    worksheet.update_cell(row_number, usuario_idx + 1, usuario)
                    worksheet.update_cell(row_number, perfil_idx + 1, perfil)
                    worksheet.update_cell(row_number, ativo_idx + 1, ativo)
                    
                    # Atualiza novos campos se existirem
                    if sistemas_idx is not None:
                        worksheet.update_cell(row_number, sistemas_idx + 1, sistemas_acesso)
                    if permissoes_idx is not None:
                        worksheet.update_cell(row_number, permissoes_idx + 1, permissoes_sigec)
                    
                    # Atualiza senha se fornecida
                    if nova_senha:
                        password_hash = self._hash_password(nova_senha)
                        worksheet.update_cell(row_number, senha_idx + 1, password_hash)
                    
                    return {'success': True, 'message': 'Usuário atualizado com sucesso'}
            
            return {'success': False, 'message': 'Usuário não encontrado'}
            
        except Exception as e:
            print(f"Erro ao atualizar usuário: {e}")
            return {'success': False, 'message': f'Erro ao atualizar usuário: {str(e)}'}

    def delete_user(self, user_id):
        """Exclui um usuário"""
        try:
            worksheet = self.sheets_service.get_worksheet(self.worksheet_name)
            all_values = worksheet.get_all_values()
            
            if len(all_values) <= 1:
                return {'success': False, 'message': 'Usuário não encontrado'}
            
            headers = all_values[0]
            users = all_values[1:]
            
            id_idx = headers.index('ID')
            usuario_idx = headers.index('Usuario')
            
            # Encontra o usuário
            for i, user_row in enumerate(users):
                if len(user_row) > id_idx and user_row[id_idx] == str(user_id):
                    # Não permite excluir o usuário admin
                    if len(user_row) > usuario_idx and user_row[usuario_idx].lower() == 'admin':
                        return {'success': False, 'message': 'Não é possível excluir o usuário admin'}
                    
                    row_number = i + 2  # +2 porque lista começa em 0 e planilha em 1, mais linha de cabeçalho
                    worksheet.delete_rows(row_number)
                    
                    return {'success': True, 'message': 'Usuário excluído com sucesso'}
            
            return {'success': False, 'message': 'Usuário não encontrado'}
            
        except Exception as e:
            print(f"Erro ao excluir usuário: {e}")
            return {'success': False, 'message': f'Erro ao excluir usuário: {str(e)}'}
