#!/usr/bin/env python3
"""
Verifica dependências disponíveis antes da importação
"""

def check_pandas():
    """Verifica se pandas está disponível"""
    try:
        import pandas as pd
        return True
    except ImportError:
        return False

def get_available_import_service():
    """Retorna o serviço de importação disponível"""
    if check_pandas():
        try:
            from services.import_service import ImportService
            return ImportService, "full"
        except Exception as e:
            print(f"⚠️ Erro ao importar ImportService completo: {e}")
    
    # Fallback para ImportServiceLite
    try:
        from services.import_service_lite import ImportServiceLite
        return ImportServiceLite, "lite"
    except Exception as e:
        print(f"❌ Erro ao importar ImportServiceLite: {e}")
        return None, "none"
