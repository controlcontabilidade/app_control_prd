#!/usr/bin/env python3
"""
Script para monitorar uso de memória da aplicação Flask
Útil para identificar vazamentos e otimizar consumo no Render
"""

import psutil
import time
import os
import sys
from datetime import datetime

def format_bytes(bytes_value):
    """Converte bytes para formato legível"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} TB"

def monitor_memory():
    """Monitora uso de memória da aplicação"""
    print("🧠 MONITOR DE MEMÓRIA - Control Contabilidade")
    print("=" * 50)
    
    # Encontrar processo Flask/Gunicorn
    flask_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info']):
        try:
            if any('app.py' in str(cmd) or 'gunicorn' in str(cmd) or 'wsgi' in str(cmd) 
                   for cmd in proc.info['cmdline'] or []):
                flask_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if not flask_processes:
        print("❌ Nenhum processo Flask/Gunicorn encontrado")
        print("💡 Execute: python app.py ou gunicorn wsgi:app")
        return
    
    print(f"📊 Monitorando {len(flask_processes)} processo(s):")
    for proc in flask_processes:
        print(f"   PID {proc.pid}: {proc.info['name']}")
    
    print("\n⏰ Pressione Ctrl+C para parar o monitoramento\n")
    
    try:
        while True:
            timestamp = datetime.now().strftime("%H:%M:%S")
            total_memory = 0
            
            print(f"[{timestamp}]", end=" ")
            
            for i, proc in enumerate(flask_processes):
                try:
                    # Atualizar informações do processo
                    proc = psutil.Process(proc.pid)
                    memory_info = proc.memory_info()
                    memory_mb = memory_info.rss / 1024 / 1024
                    total_memory += memory_mb
                    
                    cpu_percent = proc.cpu_percent()
                    
                    print(f"PID {proc.pid}: {memory_mb:.1f}MB (CPU: {cpu_percent:.1f}%)", end="")
                    if i < len(flask_processes) - 1:
                        print(" | ", end="")
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    print(f"PID {proc.pid}: TERMINATED", end="")
                    flask_processes.remove(proc)
            
            print(f" | TOTAL: {total_memory:.1f}MB")
            
            # Verificar limite do Render (512MB)
            if total_memory > 400:
                print(f"⚠️ ALERTA: Próximo do limite do Render (512MB)")
            if total_memory > 500:
                print(f"🚨 CRÍTICO: Muito próximo do limite!")
            
            # Informações do sistema
            system_memory = psutil.virtual_memory()
            print(f"💻 Sistema: {format_bytes(system_memory.used)}/{format_bytes(system_memory.total)} "
                  f"({system_memory.percent:.1f}%)")
            
            print("-" * 60)
            time.sleep(5)  # Atualizar a cada 5 segundos
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoramento interrompido")
        print("📊 Resumo das recomendações:")
        print("   • Mantenha uso < 400MB para estabilidade no Render")
        print("   • Use garbage collection em routes pesadas")
        print("   • Limite quantidade de dados carregados")
        print("   • Configure Gunicorn com 1 worker apenas")

def check_system_limits():
    """Verifica limites do sistema"""
    print("🔍 VERIFICAÇÃO DOS LIMITES DO SISTEMA")
    print("=" * 40)
    
    memory = psutil.virtual_memory()
    print(f"💾 RAM Total: {format_bytes(memory.total)}")
    print(f"💾 RAM Disponível: {format_bytes(memory.available)}")
    print(f"💾 RAM Usada: {format_bytes(memory.used)} ({memory.percent:.1f}%)")
    
    # Verificar se está rodando no Render
    if os.environ.get('RENDER'):
        print("\n🌐 DETECTADO: Executando no Render")
        print("⚠️ Limite de RAM: 512MB (plano gratuito)")
        if memory.total > 600 * 1024 * 1024:  # 600MB
            print("❌ Sistema com mais RAM que o Render - resultados podem diferir")
        else:
            print("✅ Sistema similar ao Render")
    else:
        print("\n💻 DETECTADO: Executando localmente")
        print("💡 Para simular Render, limite a RAM disponível")
    
    print("\n📊 RECOMENDAÇÕES:")
    print("   • Flask app deve usar < 400MB")
    print("   • Gunicorn: 1 worker + 2 threads")
    print("   • Ativar garbage collection")
    print("   • Limitar dados carregados por vez")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_system_limits()
    else:
        monitor_memory()
