#!/usr/bin/env python3
"""
Script para criar usuário administrativo temporário
"""

import sys
sys.path.append('.')

from services.user_service import UserService

def create_admin_user():
    """Cria usuário administrativo temporário"""
    print("🧪 === CRIANDO USUÁRIO ADMIN TEMPORÁRIO ===")
    
    try:
        # Inicializar serviço de usuários
        user_service = UserService('1jEmEPlxhGsrB_VhP3Pa-69xGRXRSwSAKd1Ypx241M4s')
        
        # Dados do usuário admin
        nome = "Administrador"
        email = "admin@control.com"
        usuario = "admin"
        senha = "123456"  # Senha simples para teste
        perfil = "admin"
        
        print(f"👤 Criando usuário: {usuario}")
        print(f"📧 Email: {email}")
        print(f"🔐 Senha: {senha}")
        print(f"👑 Perfil: {perfil}")
        
        # Criar usuário
        result = user_service.create_user(nome, email, usuario, senha, perfil)
        
        if result['success']:
            print(f"✅ {result['message']}")
            print("\n🎉 Usuário admin criado com sucesso!")
            print("🔐 Para fazer login:")
            print(f"   Usuario: {usuario}")
            print(f"   Senha: {senha}")
        else:
            print(f"❌ {result['message']}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    create_admin_user()
