#!/usr/bin/env python3
"""
Teste completo do sistema de autenticação com fallback
"""
import os
import sys
sys.path.append('.')

def test_fallback_auth():
    print("🔍 TESTE COMPLETO DE AUTENTICAÇÃO COM FALLBACK")
    print("="*60)
    
    # Testar import do fallback service
    print("\n📦 TESTANDO FALLBACK SERVICE:")
    try:
        from services.fallback_user_service import FallbackUserService
        print("✅ FallbackUserService importado com sucesso")
        
        # Inicializar o serviço
        fallback_service = FallbackUserService()
        print("✅ FallbackUserService inicializado")
        
        # Testar autenticação
        print("\n🔐 TESTANDO AUTENTICAÇÃO FALLBACK:")
        user = fallback_service.authenticate_user("admin", "admin123")
        if user:
            print(f"✅ Autenticação bem-sucedida: {user['nome']}")
            print(f"📊 ID: {user['id']}")
            print(f"📊 Perfil: {user['perfil']}")
        else:
            print("❌ Falha na autenticação fallback")
            return False
            
        # Testar credenciais incorretas
        print("\n❌ TESTANDO CREDENCIAIS INCORRETAS:")
        user_fail = fallback_service.authenticate_user("admin", "senha_errada")
        if not user_fail:
            print("✅ Credenciais incorretas rejeitadas corretamente")
        else:
            print("❌ Credenciais incorretas foram aceitas!")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do fallback: {e}")
        return False

def test_app_user_service():
    print("\n🔧 TESTANDO get_user_service() DO APP:")
    try:
        # Simular ambiente sem Google Sheets configurado
        os.environ.pop('GOOGLE_SHEETS_ID', None)
        os.environ.pop('GOOGLE_SERVICE_ACCOUNT_JSON', None)
        
        # Importar a função do app
        from app import get_user_service
        
        # Testar se retorna o fallback
        user_service = get_user_service()
        
        if user_service:
            print("✅ user_service retornado (deve ser fallback)")
            
            # Testar se é o fallback
            if hasattr(user_service, '__class__') and 'Fallback' in user_service.__class__.__name__:
                print("✅ É o FallbackUserService correto")
            else:
                print(f"⚠️  Tipo de serviço: {type(user_service)}")
            
            # Testar autenticação através do app
            user = user_service.authenticate_user("admin", "admin123")
            if user:
                print(f"✅ Autenticação via app funcionando: {user['nome']}")
                return True
            else:
                print("❌ Autenticação via app falhando")
                return False
        else:
            print("❌ user_service retornou None")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste do app: {e}")
        return False

def main():
    print("🚀 INICIANDO TESTES DE AUTENTICAÇÃO")
    
    # Teste 1: Fallback Service direto
    test1 = test_fallback_auth()
    
    # Teste 2: Através do app
    test2 = test_app_user_service()
    
    print("\n" + "="*60)
    print("📊 RESULTADO DOS TESTES:")
    print(f"   Fallback Service: {'✅ PASSOU' if test1 else '❌ FALHOU'}")
    print(f"   App Integration:  {'✅ PASSOU' if test2 else '❌ FALHOU'}")
    
    if test1 and test2:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema de autenticação com fallback está funcionando")
        print("\n💡 CREDENCIAIS DE FALLBACK:")
        print("   Usuário: admin")
        print("   Senha: admin123")
        return True
    else:
        print("\n💥 ALGUNS TESTES FALHARAM!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
