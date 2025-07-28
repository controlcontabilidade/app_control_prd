#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 MONITOR DE PRODUÇÃO - Control Contabilidade
Monitora performance, memória e saúde da aplicação no Render
"""

import os
import sys
import time
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

class ProductionMonitor:
    def __init__(self, app_url):
        self.app_url = app_url.rstrip('/')
        self.start_time = datetime.now()
        self.checks = []
        
    def log(self, message, level="INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
        # Adicionar ao histórico
        self.checks.append({
            'timestamp': timestamp,
            'level': level,
            'message': message
        })
    
    def check_health(self):
        """Verifica saúde básica da aplicação"""
        try:
            response = requests.get(f"{self.app_url}/", timeout=30)
            if response.status_code in [200, 302]:
                self.log("✅ Aplicação respondendo", "SUCCESS")
                return True
            else:
                self.log(f"⚠️  Status HTTP: {response.status_code}", "WARNING")
                return False
        except requests.exceptions.Timeout:
            self.log("❌ Timeout ao acessar aplicação", "ERROR")
            return False
        except requests.exceptions.ConnectionError:
            self.log("❌ Erro de conexão com aplicação", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ Erro inesperado: {e}", "ERROR")
            return False
    
    def check_memory_status(self):
        """Verifica status de memória"""
        try:
            response = requests.get(f"{self.app_url}/api/memory-status", timeout=15)
            if response.status_code == 200:
                data = response.json()
                
                # Extrair informações de memória
                memory_mb = data.get('memory_usage_mb', 0)
                memory_percent = data.get('memory_usage_percent', 0)
                
                if memory_mb > 400:  # > 400MB em plan de 512MB
                    self.log(f"🚨 MEMÓRIA CRÍTICA: {memory_mb:.1f}MB ({memory_percent:.1f}%)", "CRITICAL")
                elif memory_mb > 300:  # > 300MB
                    self.log(f"⚠️  MEMÓRIA ALTA: {memory_mb:.1f}MB ({memory_percent:.1f}%)", "WARNING")
                else:
                    self.log(f"✅ Memória OK: {memory_mb:.1f}MB ({memory_percent:.1f}%)", "SUCCESS")
                
                # Log detalhes adicionais
                gc_counts = data.get('gc_counts', [])
                if gc_counts:
                    self.log(f"🗑️  GC: {gc_counts}", "INFO")
                
                return data
            else:
                self.log(f"❌ Erro ao obter status de memória: HTTP {response.status_code}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Erro ao verificar memória: {e}", "ERROR")
            return None
    
    def check_auth_status(self):
        """Verifica status de autenticação"""
        try:
            response = requests.get(f"{self.app_url}/api/auth-status", timeout=15)
            if response.status_code == 200:
                data = response.json()
                
                auth_working = data.get('service_account_auth', False)
                service_type = data.get('current_service', 'unknown')
                
                if auth_working:
                    self.log(f"✅ Autenticação OK - Serviço: {service_type}", "SUCCESS")
                else:
                    self.log(f"⚠️  MODO FALLBACK - Serviço: {service_type}", "WARNING")
                    
                    # Verificar se tem erro específico
                    error = data.get('last_error')
                    if error:
                        self.log(f"❌ Erro de auth: {error}", "ERROR")
                
                return data
            else:
                self.log(f"❌ Erro ao obter status de auth: HTTP {response.status_code}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Erro ao verificar autenticação: {e}", "ERROR")
            return None
    
    def check_response_time(self):
        """Verifica tempo de resposta"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.app_url}/", timeout=30)
            response_time = (time.time() - start_time) * 1000  # em ms
            
            if response_time > 5000:  # > 5 segundos
                self.log(f"🐌 RESPOSTA LENTA: {response_time:.0f}ms", "WARNING")
            elif response_time > 2000:  # > 2 segundos
                self.log(f"⚠️  Resposta: {response_time:.0f}ms", "WARNING")
            else:
                self.log(f"⚡ Resposta rápida: {response_time:.0f}ms", "SUCCESS")
            
            return response_time
            
        except Exception as e:
            self.log(f"❌ Erro ao medir tempo de resposta: {e}", "ERROR")
            return None
    
    def run_full_check(self):
        """Executa verificação completa"""
        self.log("🔍 Iniciando verificação completa...", "INFO")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'app_url': self.app_url,
            'checks': {}
        }
        
        # Verificações
        results['checks']['health'] = self.check_health()
        results['checks']['memory'] = self.check_memory_status()
        results['checks']['auth'] = self.check_auth_status()
        results['checks']['response_time'] = self.check_response_time()
        
        # Resumo
        total_checks = len([v for v in results['checks'].values() if v is not None])
        success_checks = len([v for v in results['checks'].values() if v])
        
        self.log(f"📊 Verificação completa: {success_checks}/{total_checks} checks OK", "INFO")
        
        return results
    
    def monitor_continuous(self, interval_minutes=5, max_hours=24):
        """Monitora continuamente"""
        self.log(f"🔄 Iniciando monitoramento contínuo (intervalo: {interval_minutes}min, máximo: {max_hours}h)", "INFO")
        
        end_time = datetime.now() + timedelta(hours=max_hours)
        iteration = 0
        
        try:
            while datetime.now() < end_time:
                iteration += 1
                self.log(f"🔍 Verificação #{iteration}", "INFO")
                
                # Executar verificação
                self.run_full_check()
                
                # Aguardar próxima verificação
                self.log(f"⏰ Próxima verificação em {interval_minutes} minutos...", "INFO")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            self.log("⏹️  Monitoramento interrompido pelo usuário", "INFO")
        except Exception as e:
            self.log(f"❌ Erro no monitoramento: {e}", "ERROR")
        
        self.log("🏁 Monitoramento finalizado", "INFO")
    
    def generate_report(self):
        """Gera relatório dos checks realizados"""
        if not self.checks:
            return "Nenhuma verificação realizada."
        
        # Contar por nível
        levels = {}
        for check in self.checks:
            level = check['level']
            levels[level] = levels.get(level, 0) + 1
        
        # Gerar relatório
        report = f"""
📊 RELATÓRIO DE MONITORAMENTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🕐 Período: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📋 Total de checks: {len(self.checks)}

📈 RESUMO POR NÍVEL:
{chr(10).join([f'   {level}: {count}' for level, count in levels.items()])}

🔍 ÚLTIMAS VERIFICAÇÕES:
{chr(10).join([f'   [{check["timestamp"]}] {check["level"]}: {check["message"]}' for check in self.checks[-10:]])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return report

def main():
    if len(sys.argv) < 2:
        print("Uso: python monitor_production.py <URL_DA_APP> [modo] [opções]")
        print("\nModos:")
        print("  check     - Verificação única (padrão)")
        print("  monitor   - Monitoramento contínuo")
        print("\nExemplos:")
        print("  python monitor_production.py https://control-app.render.com")
        print("  python monitor_production.py https://control-app.render.com monitor")
        print("  python monitor_production.py https://control-app.render.com monitor --interval 10 --hours 2")
        sys.exit(1)
    
    app_url = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "check"
    
    # Inicializar monitor
    monitor = ProductionMonitor(app_url)
    
    try:
        if mode == "check":
            # Verificação única
            results = monitor.run_full_check()
            print("\n" + monitor.generate_report())
            
        elif mode == "monitor":
            # Monitoramento contínuo
            interval = 5  # minutos
            hours = 24    # horas
            
            # Processar argumentos opcionais
            args = sys.argv[3:]
            for i, arg in enumerate(args):
                if arg == "--interval" and i + 1 < len(args):
                    interval = int(args[i + 1])
                elif arg == "--hours" and i + 1 < len(args):
                    hours = int(args[i + 1])
            
            monitor.monitor_continuous(interval, hours)
            print("\n" + monitor.generate_report())
            
        else:
            print(f"Modo '{mode}' não reconhecido. Use 'check' ou 'monitor'.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Erro geral: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
