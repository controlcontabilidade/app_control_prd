#!/usr/bin/env python3
"""
Script para monitorar o uso de memória da aplicação
Útil para identificar vazamentos e otimizar recursos no Render
"""

import os
import gc
import sys
import time
import traceback

def get_memory_usage():
    """Retorna o uso atual de memória"""
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        return {
            'rss': memory_info.rss / 1024 / 1024,  # MB
            'vms': memory_info.vms / 1024 / 1024,  # MB
            'percent': process.memory_percent()
        }
    except ImportError:
        return {'rss': 'N/A', 'vms': 'N/A', 'percent': 'N/A'}

def test_memory_optimization():
    """Testa as otimizações de memória"""
    print("🧪 Testando otimizações de memória...")
    
    # Teste 1: Garbage collection
    print("🧹 Teste 1: Garbage collection")
    memory_before = get_memory_usage()
    gc.collect()
    memory_after = get_memory_usage()
    
    if isinstance(memory_before['rss'], (int, float)) and isinstance(memory_after['rss'], (int, float)):
        saved = memory_before['rss'] - memory_after['rss']
        print(f"   Antes: {memory_before['rss']:.1f}MB")
        print(f"   Depois: {memory_after['rss']:.1f}MB")
        print(f"   Economizado: {saved:.1f}MB")
    
    # Teste 2: Configurações de GC
    print("\n🔧 Teste 2: Configurações de GC")
    thresholds_before = gc.get_threshold()
    print(f"   Thresholds padrão: {thresholds_before}")
    
    # Aplicar configurações otimizadas
    gc.set_threshold(500, 5, 5)
    thresholds_after = gc.get_threshold()
    print(f"   Thresholds otimizadas: {thresholds_after}")
    
    # Teste 3: Verificar otimizador
    try:
        from memory_optimizer import MemoryOptimizer
        print("\n✅ Teste 3: Memory Optimizer disponível")
        print(f"   Memory usage: {MemoryOptimizer.get_memory_usage()}")
    except ImportError as e:
        print(f"\n❌ Teste 3: Memory Optimizer NÃO disponível: {e}")

if __name__ == "__main__":
    print("🧠 Monitor de Memória - Control App")
    print("=" * 50)
    test_memory_optimization()
