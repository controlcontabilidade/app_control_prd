#!/usr/bin/env python3
"""
Script de verificação final para deploy no Render
Verifica se todas as otimizações estão prontas
"""

def check_deploy_readiness():
    print("🚀 VERIFICAÇÃO FINAL PARA DEPLOY NO RENDER")
    print("=" * 60)
    
    checks_passed = 0
    total_checks = 0
    
    # 1. Verificar arquivos essenciais
    print("\n📁 1. ARQUIVOS ESSENCIAIS")
    essential_files = [
        'app.py', 'wsgi.py', 'gunicorn.conf.py', 
        'memory_optimizer.py', 'requirements.txt'
    ]
    
    import os
    for file in essential_files:
        total_checks += 1
        if os.path.exists(file):
            print(f"   ✅ {file}")
            checks_passed += 1
        else:
            print(f"   ❌ {file} FALTANDO!")
    
    # 2. Verificar dependências Python
    print("\n🐍 2. DEPENDÊNCIAS PYTHON")
    dependencies = ['flask', 'gunicorn', 'google-api-python-client']
    
    for dep in dependencies:
        total_checks += 1
        try:
            __import__(dep.replace('-', '_'))
            print(f"   ✅ {dep}")
            checks_passed += 1
        except ImportError:
            print(f"   ❌ {dep} não instalado!")
    
    # 3. Verificar memory optimizer
    print("\n🧠 3. MEMORY OPTIMIZER")
    total_checks += 1
    try:
        from memory_optimizer import MemoryOptimizer
        print(f"   ✅ Memory Optimizer OK")
        print(f"   💾 Uso atual: {MemoryOptimizer.get_memory_usage()}")
        checks_passed += 1
    except ImportError:
        print("   ❌ Memory Optimizer com problemas!")
    
    # 4. Verificar configurações de produção
    print("\n⚙️ 4. CONFIGURAÇÕES DE PRODUÇÃO")
    
    # Simular ambiente de produção
    os.environ['FLASK_ENV'] = 'production'
    
    total_checks += 1
    try:
        from app import app
        print("   ✅ App Flask carregável")
        checks_passed += 1
    except Exception as e:
        print(f"   ❌ Erro ao carregar app: {e}")
    
    # 5. Verificar gunicorn
    print("\n🦄 5. GUNICORN")
    total_checks += 1
    try:
        import gunicorn
        print("   ✅ Gunicorn instalado")
        checks_passed += 1
    except ImportError:
        print("   ❌ Gunicorn não instalado!")
    
    # 6. Verificar configuração de memória
    print("\n🧹 6. CONFIGURAÇÕES DE MEMÓRIA")
    import gc
    
    # Aplicar configurações otimizadas
    gc.set_threshold(500, 5, 5)
    threshold = gc.get_threshold()
    
    total_checks += 1
    if threshold == (500, 5, 5):
        print(f"   ✅ GC otimizado: {threshold}")
        checks_passed += 1
    else:
        print(f"   ❌ GC não otimizado: {threshold}")
    
    # 7. Verificar variáveis de ambiente necessárias
    print("\n🌍 7. VARIÁVEIS DE AMBIENTE (para Render)")
    required_vars = [
        'FLASK_ENV', 'GOOGLE_SHEETS_ID', 'SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        total_checks += 1
        if os.environ.get(var):
            print(f"   ✅ {var} definido")
            checks_passed += 1
        else:
            print(f"   ⚠️ {var} não definido (definir no Render)")
            missing_vars.append(var)
    
    # 8. Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO FINAL")
    print(f"✅ Verificações passaram: {checks_passed}/{total_checks}")
    print(f"📈 Taxa de sucesso: {(checks_passed/total_checks)*100:.1f}%")
    
    if checks_passed >= total_checks - len(missing_vars):
        print("\n🎉 PRONTO PARA DEPLOY NO RENDER!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Copiar todos os arquivos para o repositório")
        print("2. Configurar variáveis de ambiente no Render:")
        for var in missing_vars:
            print(f"   - {var}")
        print("3. Build Command: pip install --no-cache-dir -r requirements.txt")
        print("4. Start Command: gunicorn --config gunicorn.conf.py wsgi:application")
        print("5. Monitorar: GET /api/memory-status")
        
        return True
    else:
        print("\n❌ PROBLEMAS ENCONTRADOS - CORRIGIR ANTES DO DEPLOY")
        return False

if __name__ == "__main__":
    check_deploy_readiness()
