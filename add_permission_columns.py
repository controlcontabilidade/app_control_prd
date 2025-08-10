#!/usr/bin/env python3
"""
Script para adicionar as colunas de sistemas e permissões na planilha de usuários
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.user_service import UserService

def add_permission_columns():
    """Adiciona as colunas de permissão na planilha"""
    
    print("🔧 === ADICIONANDO COLUNAS DE PERMISSÃO ===")
    
    try:
        # Inicializar serviço
        user_service = UserService()
        
        # Acessar planilha diretamente
        worksheet = user_service.sheets_service.get_worksheet('Usuarios')
        all_values = worksheet.get_all_values()
        
        if len(all_values) > 0:
            headers = all_values[0]
            print(f"📊 Colunas atuais: {len(headers)}")
            
            # Verificar se as colunas já existem
            needs_sistemas = 'Sistemas_Acesso' not in headers
            needs_permissoes = 'Permissoes_SIGEC' not in headers
            
            if needs_sistemas or needs_permissoes:
                print("\n🔧 Adicionando colunas necessárias...")
                
                # Adicionar cabeçalhos
                new_headers = headers.copy()
                
                if needs_sistemas:
                    new_headers.append('Sistemas_Acesso')
                    print("   ➕ Adicionando coluna: Sistemas_Acesso")
                
                if needs_permissoes:
                    new_headers.append('Permissoes_SIGEC')
                    print("   ➕ Adicionando coluna: Permissoes_SIGEC")
                
                # Atualizar cabeçalhos
                for i, header in enumerate(new_headers):
                    worksheet.update_cell(1, i + 1, header)
                
                print(f"   ✅ Cabeçalhos atualizados: {len(new_headers)} colunas")
                
                # Configurar dados padrão para usuários existentes
                users = all_values[1:]
                for i, user_row in enumerate(users):
                    row_number = i + 2  # +2 porque lista começa em 0 e planilha em 1, mais linha de cabeçalho
                    
                    # Definir valores padrão baseado no perfil
                    perfil_idx = headers.index('Perfil') if 'Perfil' in headers else None
                    perfil = user_row[perfil_idx] if perfil_idx and perfil_idx < len(user_row) else ''
                    
                    # Atualizar campos específicos
                    if needs_sistemas:
                        sistemas_idx = new_headers.index('Sistemas_Acesso')
                        if perfil.lower() == 'administrador':
                            worksheet.update_cell(row_number, sistemas_idx + 1, 'sigec,operacao-fiscal,gestao-operacional,gestao-financeira')
                        else:
                            worksheet.update_cell(row_number, sistemas_idx + 1, 'sigec')
                    
                    if needs_permissoes:
                        permissoes_idx = new_headers.index('Permissoes_SIGEC')
                        if perfil.lower() == 'administrador':
                            worksheet.update_cell(row_number, permissoes_idx + 1, 'TOTAL_CADASTROS')
                        else:
                            worksheet.update_cell(row_number, permissoes_idx + 1, 'VISUALIZADOR')
                    
                    print(f"   🔄 Usuário {row_number-1} atualizado")
                
                print("   ✅ Todos os usuários foram atualizados!")
                
            else:
                print("   ✅ Colunas já existem!")
        
        # Verificação final
        print("\n🔍 Verificação final...")
        final_values = worksheet.get_all_values()
        final_headers = final_values[0]
        
        print(f"📊 Total de colunas agora: {len(final_headers)}")
        
        # Verificar se as colunas foram criadas
        if 'Sistemas_Acesso' in final_headers:
            idx = final_headers.index('Sistemas_Acesso')
            print(f"   ✅ Sistemas_Acesso na posição {idx+1}")
        
        if 'Permissoes_SIGEC' in final_headers:
            idx = final_headers.index('Permissoes_SIGEC')
            print(f"   ✅ Permissoes_SIGEC na posição {idx+1}")
        
        # Mostrar dados do admin
        if len(final_values) > 1:
            admin_data = final_values[1]
            print("\n👤 Dados do administrador após atualização:")
            for i, value in enumerate(admin_data):
                if i < len(final_headers):
                    header = final_headers[i]
                    if header in ['Sistemas_Acesso', 'Permissoes_SIGEC', 'Perfil']:
                        print(f"   {header}: {value}")
        
    except Exception as e:
        print(f"❌ Erro durante a atualização: {str(e)}")
        return False
    
    print("\n🎯 === COLUNAS ADICIONADAS COM SUCESSO ===")
    return True

if __name__ == "__main__":
    success = add_permission_columns()
    sys.exit(0 if success else 1)
