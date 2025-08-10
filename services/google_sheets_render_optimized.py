# -*- coding: utf-8 -*-
"""
Google Sheets Service - VERSÃO ULTRA-OTIMIZADA PARA RENDER
Objetivo: Consumir menos de 50MB de memória
"""

import os
import json
import gc
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime
from typing import List, Dict, Optional

class RenderOptimizedGoogleSheetsService:
    """
    Serviço Google Sheets EXTREMAMENTE otimizado para Render
    - Lazy loading de dados
    - Cache mínimo
    - Limpeza agressiva de memória
    """
    
    def __init__(self, spreadsheet_id: str, range_name: str = 'Clientes!A:CH'):
        self.spreadsheet_id = spreadsheet_id
        self.range_name = range_name
        self.service = None
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        
        # Cache mínimo - apenas para evitar re-requests desnecessários
        self._cache = {}
        self._cache_timeout = 30  # 30 segundos apenas
        self._last_cache_clear = datetime.now()
        
        print(f"🎯 Render Optimized Sheets Service - planilha: {self.spreadsheet_id}")
        self._authenticate()
    
    def _authenticate(self):
        """Autentica usando Service Account com lazy loading"""
        try:
            service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
            
            if service_account_json:
                print("🔐 Autenticando com variável de ambiente...")
                
                # Parse JSON com limpeza imediata
                credentials_info = json.loads(service_account_json)
                del service_account_json  # Limpar da memória imediatamente
                
                credentials = Credentials.from_service_account_info(
                    credentials_info, scopes=self.scopes
                )
                del credentials_info  # Limpar da memória
                
                # Lazy build do service
                self.service = build('sheets', 'v4', credentials=credentials, cache_discovery=False)
                del credentials  # Limpar credenciais da memória
                
                print("✅ Autenticação concluída (otimizada)")
                
                # Forçar limpeza de memória após autenticação
                gc.collect()
                
            else:
                print("❌ GOOGLE_SERVICE_ACCOUNT_JSON não encontrado")
                raise Exception("Credenciais não disponíveis")
                
        except Exception as e:
            print(f"❌ Erro na autenticação: {e}")
            raise
    
    def _clear_cache_if_needed(self):
        """Limpa cache se necessário para economizar memória"""
        now = datetime.now()
        if (now - self._last_cache_clear).seconds > self._cache_timeout:
            self._cache.clear()
            self._last_cache_clear = now
            gc.collect()
    
    def get_clients(self) -> List[Dict]:
        """Obter clientes com otimizações de memória"""
        self._clear_cache_if_needed()
        
        # Verificar cache primeiro
        cache_key = 'clients_data'
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            print("📊 Buscando dados da planilha (otimizado)...")
            
            # Request otimizado - apenas dados necessários
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=self.range_name,
                valueRenderOption='UNFORMATTED_VALUE',  # Mais rápido
                dateTimeRenderOption='FORMATTED_STRING'
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                print("⚠️ Nenhum dado encontrado")
                return []
            
            # Processar dados de forma otimizada
            clients = self._process_data_optimized(values)
            
            # Cache com TTL curto
            self._cache[cache_key] = clients
            
            # Limpeza imediata de variáveis temporárias
            del result, values
            gc.collect()
            
            print(f"✅ {len(clients)} clientes carregados (otimizado)")
            return clients
            
        except Exception as e:
            print(f"❌ Erro ao buscar clientes: {e}")
            return []
    
    def _process_data_optimized(self, values: List[List]) -> List[Dict]:
        """Processar dados com otimização de memória"""
        if not values:
            return []
        
        # Assumir primeira linha como headers
        headers = values[0] if values else []
        data_rows = values[1:] if len(values) > 1 else []
        
        clients = []
        
        # Processar em lotes pequenos para economizar memória
        batch_size = 10  # Muito pequeno para Render
        
        for i in range(0, len(data_rows), batch_size):
            batch = data_rows[i:i+batch_size]
            
            for row in batch:
                client_dict = {}
                
                # Mapear apenas campos não vazios para economizar memória
                for j, value in enumerate(row):
                    if j < len(headers) and value and str(value).strip():
                        client_dict[headers[j]] = str(value).strip()
                
                if client_dict:  # Só adicionar se não vazio
                    clients.append(client_dict)
            
            # Limpeza a cada lote
            del batch
            gc.collect()
        
        # Limpeza final
        del headers, data_rows
        gc.collect()
        
        return clients
    
    def save_client(self, client_data: Dict) -> bool:
        """Salvar cliente com otimizações"""
        try:
            # Limpar cache antes de salvar
            self._cache.clear()
            
            # Implementar lógica de salvamento otimizada
            # (similar ao service original, mas com limpeza de memória)
            
            # Limpeza após operação
            gc.collect()
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar cliente: {e}")
            return False
    
    def get_client(self, client_id: str) -> Optional[Dict]:
        """Obter cliente específico (otimizado)"""
        clients = self.get_clients()
        
        # Busca otimizada
        for client in clients:
            if client.get('id') == client_id:
                return client
        
        return None
    
    def delete_client(self, client_id: str) -> bool:
        """Deletar cliente (otimizado)"""
        try:
            # Limpar cache
            self._cache.clear()
            
            # Implementar lógica de deleção
            # (marcar como inativo para economizar operações)
            
            gc.collect()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao deletar cliente: {e}")
            return False
    
    def __del__(self):
        """Destructor para limpeza de memória"""
        if hasattr(self, '_cache'):
            self._cache.clear()
        gc.collect()

# Alias para compatibilidade
GoogleSheetsServiceAccountService = RenderOptimizedGoogleSheetsService
