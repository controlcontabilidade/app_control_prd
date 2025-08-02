#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Monitor contínuo de memória para produção no Render
"""

import time
import gc
import os
import sys
from datetime import datetime

class MemoryMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.peak_memory = 0
        self.gc_count = 0
        
    def get_memory_usage(self):
        """Obtém uso de memória atual"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            return memory_mb
        except ImportError:
            return 0
    
    def check_memory_and_cleanup(self):
        """Verifica memória e força limpeza se necessário"""
        memory_mb = self.get_memory_usage()
        
        if memory_mb > self.peak_memory:
            self.peak_memory = memory_mb
        
        # Alertas baseados no limite de 512MB do Render
        if memory_mb > 480:
            print(f"🚨 CRÍTICO: {memory_mb:.1f}MB - Forçando limpeza AGRESSIVA!")
            for _ in range(10):
                gc.collect()
            self.gc_count += 10
            return "CRITICAL"
        elif memory_mb > 400:
            print(f"⚠️ ALTO: {memory_mb:.1f}MB - Limpeza preventiva")
            gc.collect()
            gc.collect()
            self.gc_count += 2
            return "HIGH"
        elif memory_mb > 350:
            print(f"📊 MODERADO: {memory_mb:.1f}MB - Limpeza leve")
            gc.collect()
            self.gc_count += 1
            return "MODERATE"
        else:
            print(f"✅ OK: {memory_mb:.1f}MB")
            return "OK"
    
    def generate_report(self):
        """Gera relatório de uso de memória"""
        uptime = datetime.now() - self.start_time
        current_memory = self.get_memory_usage()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': uptime.total_seconds(),
            'current_memory_mb': current_memory,
            'peak_memory_mb': self.peak_memory,
            'gc_collections': self.gc_count,
            'gc_objects': len(gc.get_objects()),
            'gc_threshold': gc.get_threshold(),
            'environment': os.environ.get('FLASK_ENV', 'development')
        }
        
        return report

# Instância global do monitor
memory_monitor = MemoryMonitor()

def periodic_memory_check():
    """Verificação periódica de memória (para usar em cron/scheduler)"""
    return memory_monitor.check_memory_and_cleanup()

def emergency_memory_cleanup():
    """Limpeza de emergência quando memória está crítica"""
    print("🆘 LIMPEZA DE EMERGÊNCIA INICIADA")
    
    # Múltiplas passadas de GC
    for i in range(20):
        collected = gc.collect()
        print(f"   Passada {i+1}: {collected} objetos coletados")
        time.sleep(0.1)
    
    # Limpar cache Python interno se disponível
    if hasattr(sys, '_clear_type_cache'):
        sys._clear_type_cache()
        print("   ✅ Cache de tipos limpo")
    
    # Forçar limpeza de módulos não essenciais
    modules_to_clear = [
        'requests.adapters', 'urllib3.poolmanager',
        'google.auth._helpers', 'google.api_core._helpers'
    ]
    
    for module in modules_to_clear:
        if module in sys.modules:
            try:
                del sys.modules[module]
                print(f"   ✅ Módulo {module} removido")
            except:
                pass
    
    final_memory = memory_monitor.get_memory_usage()
    print(f"🏁 Limpeza concluída - Memória: {final_memory:.1f}MB")
    
    return final_memory

if __name__ == "__main__":
    print("🔍 Monitor de Memória - Teste Manual")
    print("=" * 50)
    
    # Teste inicial
    status = periodic_memory_check()
    print(f"Status inicial: {status}")
    
    # Gerar relatório
    report = memory_monitor.generate_report()
    print("\n📊 Relatório:")
    for key, value in report.items():
        print(f"   {key}: {value}")
    
    # Teste de limpeza de emergência se necessário
    if status in ["CRITICAL", "HIGH"]:
        print("\n🆘 Executando limpeza de emergência...")
        emergency_memory_cleanup()
