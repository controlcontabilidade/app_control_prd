#!/usr/bin/env python3
"""
Serviço de Importação de Clientes
Permite importar clientes de planilhas XLSX
"""

# Verificar dependências
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

from datetime import datetime
import uuid
from typing import List, Dict, Tuple
import re

class ImportService:
    def __init__(self, storage_service):
        self.storage_service = storage_service
        self.pandas_available = PANDAS_AVAILABLE
        
        if not self.pandas_available:
            print("⚠️ ImportService inicializado sem pandas - funcionalidade limitada")
        else:
            print("✅ ImportService inicializado com pandas completo")
        
    def is_available(self) -> bool:
        """Verifica se o serviço de importação está disponível"""
        return self.pandas_available
        
    def read_excel_file(self, file_path: str):
        """Lê arquivo Excel e retorna DataFrame"""
        if not self.pandas_available:
            raise ImportError("Pandas não está disponível. Funcionalidade de importação desabilitada.")
            
        try:
            print(f"📊 Lendo arquivo Excel: {file_path}")
            df = pd.read_excel(file_path, sheet_name=0)  # Primeira aba
            print(f"✅ Arquivo lido com sucesso: {len(df)} linhas encontradas")
            return df
        except Exception as e:
            print(f"❌ Erro ao ler arquivo Excel: {e}")
            raise e
    
    def normalize_column_names(self, df) -> any:
        """Normaliza nomes das colunas para corresponder ao sistema"""
        column_mapping = {
            'NOME DA EMPRESA': 'nomeEmpresa',
            'CT': 'ct',
            'FS': 'fs', 
            'DP': 'dp',
            'COD. FORTES CT': 'codFortesCt',
            'COD. FORTES FS': 'codFortesFs',
            'COD. FORTES PS': 'codFortesPs',
            'COD. DOMÍNIO': 'codDominio',
            'SISTEMA UTILIZADO': 'sistemaUtilizado',
            'MÓDULO SPED TRIER': 'moduloSpedTrier',
            'RAZÃO SOCIAL NA RECEITA': 'razaoSocialReceita',
            'NOME FANTASIA NA RECEITA': 'nomeFantasiaReceita',
            'CNPJ': 'cnpj',
            'INSC. EST.': 'inscEst',
            'INSC. MUN.': 'inscMun',
            'SEGMENTO': 'segmento',
            'ATIVIDADE': 'atividade',
            'TRIBUTAÇÃO': 'tributacao',
            'PERFIL': 'perfil',
            'CIDADE': 'cidade',
            'DONO / RESP.': 'donoResp',
            'COD. ACESSO SIMPLES': 'codAcessoSimples',
            'CPF OU CNPJ': 'cpfOuCnpj',
            'ACESSO ISS': 'acessoIss',
            'ACESSO SEFIN': 'acessoSefin',
            'ACESSO SEUMA': 'acessoSeuma',
            'ACESSO EMP. WEB': 'acessoEmpWeb',
            'SENHA EMP. WEB': 'senhaEmpWeb',
            'ACESSO FAP/INSS': 'acessoFapInss',
            'ACESSO CRF': 'acessoCrf',
            'EMAIL GESTOR': 'emailGestor',
            'ANVISA GESTOR': 'anvisaGestor',
            'ANVISA EMPRESA': 'anvisaEmpresa',
            'ACESSO IBAMA': 'acessoIbama',
            'ACESSO SEMACE': 'acessoSemace',
            'SENHA SEMACE': 'senhaSemace',
            'PROC. RC': 'procRc',
            'PROC. CX': 'procCx',
            'PROC. SW': 'procSw',
            'MÊS/ANO DE  INÍCIO': 'mesAnoInicio',
            'RESPONSÁVEL IMEDIATO': 'responsavelImediato',
            'TELEFONE FIXO': 'telefoneFixo',
            'TELEFONE CELULAR': 'telefoneCelular',
            'E-MAILS': 'emailsSocio'
        }
        
        # Renomear colunas
        df = df.rename(columns=column_mapping)
        
        # Lidar com colunas de sócios (podem ter nomes duplicados)
        socio_columns = [col for col in df.columns if col == 'SÓCIO']
        for i, col in enumerate(socio_columns):
            if i == 0:
                df = df.rename(columns={col: 'socio1'})
            elif i == 1:
                df = df.rename(columns={col: 'socio2'}) 
            elif i == 2:
                df = df.rename(columns={col: 'socio3'})
            elif i == 3:
                df = df.rename(columns={col: 'socio4'})
        
        return df
    
    def clean_data(self, df):
        """Limpa e normaliza os dados"""
        
        # Substituir NaN por string vazia
        df = df.fillna('')
        
        # Converter tudo para string primeiro
        for col in df.columns:
            df[col] = df[col].astype(str)
        
        # Limpar valores específicos
        df = df.replace('nan', '')
        df = df.replace('-', '')
        
        return df
    
    def convert_boolean_fields(self, row) -> Dict:
        """Converte campos SIM/NÃO para boolean"""
        
        def to_bool(value):
            if isinstance(value, str):
                value = value.strip().upper()
                return value in ['SIM', 'TRUE', '1', 'VERDADEIRO']
            return bool(value)
        
        # Campos que devem ser boolean
        boolean_fields = ['ct', 'fs', 'dp', 'bpoFinanceiro', 'ativo', 'integradoDominio', 'portalCliente', 'onvio']
        
        result = {}
        
        for field in row.index:
            if field in boolean_fields:
                result[field] = to_bool(row[field])
            else:
                # Limpar strings
                value = str(row[field]).strip()
                if value.lower() in ['nan', 'none', '-', '']:
                    value = ''
                result[field] = value
        
        return result
    
    def generate_unique_id(self) -> str:
        """Gera um ID único para o cliente"""
        # Usar timestamp + parte do UUID para garantir unicidade
        timestamp = int(datetime.now().timestamp() * 1000)
        unique_part = str(uuid.uuid4())[:8]
        return f"{timestamp}-{unique_part}"
    
    def process_row_to_client(self, row, row_index: int) -> Dict:
        """Converte uma linha do DataFrame para formato de cliente"""
        
        print(f"🔄 Processando linha {row_index + 1}: {row.get('nomeEmpresa', 'SEM NOME')}")
        
        # Converter campos boolean
        client_data = self.convert_boolean_fields(row)
        
        # Adicionar campos obrigatórios do sistema
        client_data.update({
            'id': self.generate_unique_id(),
            'criadoEm': datetime.now().isoformat(),
            'ativo': True,  # Por padrão, clientes importados são ativos
            'tarefasVinculadas': 0,
            'bpoFinanceiro': False,  # Valor padrão
            'integradoDominio': False,  # Valor padrão 
            'portalCliente': False,  # Valor padrão
            'onvio': False  # Valor padrão
        })
        
        # Validar campos obrigatórios
        if not client_data.get('nomeEmpresa'):
            raise ValueError(f"Linha {row_index + 1}: Nome da empresa é obrigatório")
        
        print(f"✅ Cliente processado: ID {client_data['id']}")
        return client_data
    
    def import_from_excel(self, file_path: str) -> Tuple[int, int, List[str]]:
        """
        Importa clientes de arquivo Excel
        Retorna: (sucessos, erros, lista_erros)
        """
        
        print(f"🚀 === INICIANDO IMPORTAÇÃO ===")
        print(f"📁 Arquivo: {file_path}")
        
        sucessos = 0
        erros = 0
        lista_erros = []
        
        try:
            # Ler arquivo Excel
            df = self.read_excel_file(file_path)
            
            # Normalizar nomes das colunas
            df = self.normalize_column_names(df)
            
            # Limpar dados
            df = self.clean_data(df)
            
            print(f"🔄 Processando {len(df)} linhas...")
            
            # Processar cada linha
            for index, row in df.iterrows():
                try:
                    # Pular linhas vazias
                    if not row.get('nomeEmpresa') or str(row.get('nomeEmpresa')).strip() == '':
                        print(f"⏭️ Pulando linha {index + 1}: sem nome da empresa")
                        continue
                    
                    # Converter linha para formato de cliente
                    client_data = self.process_row_to_client(row, index)
                    
                    # Salvar no storage
                    if self.storage_service.save_client(client_data):
                        sucessos += 1
                        print(f"✅ Cliente {client_data['nomeEmpresa']} importado com sucesso")
                    else:
                        erros += 1
                        erro_msg = f"Linha {index + 1}: Falha ao salvar {client_data.get('nomeEmpresa', 'SEM NOME')}"
                        lista_erros.append(erro_msg)
                        print(f"❌ {erro_msg}")
                        
                except Exception as e:
                    erros += 1
                    erro_msg = f"Linha {index + 1}: {str(e)}"
                    lista_erros.append(erro_msg)
                    print(f"❌ Erro na linha {index + 1}: {e}")
            
            print(f"🏁 === IMPORTAÇÃO CONCLUÍDA ===")
            print(f"✅ Sucessos: {sucessos}")
            print(f"❌ Erros: {erros}")
            
            return sucessos, erros, lista_erros
            
        except Exception as e:
            print(f"❌ Erro geral na importação: {e}")
            return 0, 1, [f"Erro geral: {str(e)}"]
    
    def validate_excel_structure(self, file_path: str) -> Tuple[bool, str]:
        """Valida se o arquivo Excel tem a estrutura esperada"""
        try:
            df = self.read_excel_file(file_path)
            
            # Colunas obrigatórias
            required_columns = ['NOME DA EMPRESA', 'CNPJ']
            
            missing_columns = []
            for col in required_columns:
                if col not in df.columns:
                    missing_columns.append(col)
            
            if missing_columns:
                return False, f"Colunas obrigatórias faltando: {', '.join(missing_columns)}"
            
            if len(df) == 0:
                return False, "Arquivo está vazio"
            
            return True, "Estrutura válida"
            
        except Exception as e:
            return False, f"Erro ao validar arquivo: {str(e)}"
