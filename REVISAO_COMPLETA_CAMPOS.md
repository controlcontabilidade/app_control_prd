# 📋 RELATÓRIO COMPLETO DE REVISÃO - CAMPOS E MAPEAMENTOS
## SIGEC - Sistema de Gestão de Empresas Control

---

## 🏗️ ARQUITETURA GERAL

### Fluxo de Dados:
```
Frontend (Templates) → Backend (Flask) → Google Sheets Service → Google Sheets API
```

### Camadas:
1. **Templates HTML** (Jinja2)
2. **Backend Flask** (app.py)
3. **Service Layer** (google_sheets_service_account.py)
4. **Data Layer** (Google Sheets)

---

## 📊 GOOGLE SHEETS - ESTRUTURA DE DADOS (94 campos)

### Informações da Pessoa Jurídica (13 campos)
1. NOME DA EMPRESA
2. RAZÃO SOCIAL NA RECEITA
3. NOME FANTASIA NA RECEITA
4. CNPJ
5. PERFIL
6. INSCRIÇÃO ESTADUAL
7. INSCRIÇÃO MUNICIPAL
8. ESTADO
9. CIDADE
10. REGIME FEDERAL
11. REGIME ESTADUAL
12. SEGMENTO
13. ATIVIDADE

### Serviços Prestados (11 campos)
14. SERVIÇO CT
15. SERVIÇO FS
16. SERVIÇO DP
17. SERVIÇO BPO FINANCEIRO
18. DATA INÍCIO DOS SERVIÇOS
19. CÓDIGO FORTES CT
20. CÓDIGO FORTES FS
21. CÓDIGO FORTES PS
22. CÓDIGO DOMÍNIO
23. SISTEMA UTILIZADO

### Quadro Societário (6 campos)
24. SÓCIO 1 NOME
25. SÓCIO 1 CPF
26. SÓCIO 1 DATA NASCIMENTO
27. SÓCIO 1 ADMINISTRADOR
28. SÓCIO 1 PARTICIPAÇÃO
29. SÓCIO 1 RESPONSÁVEL LEGAL

### Contatos (30 campos)
30. TELEFONE FIXO
31. TELEFONE CELULAR
32. WHATSAPP
33. EMAIL PRINCIPAL
34. EMAIL SECUNDÁRIO
35. RESPONSÁVEL IMEDIATO
36. EMAILS DOS SÓCIOS
37. CONTATO CONTADOR
38. TELEFONE CONTADOR
39. EMAIL CONTADOR
40-59. CONTATO_1_NOME até CONTATO_5_EMAIL (20 campos)

### Senhas e Credenciais (14 campos)
60. CPF/CNPJ SN
61. CÓDIGO ACESSO SN
62. ACESSO EMPWEB
63. SENHA EMPWEB
64. ACESSO ISS
65. ACESSO SEFIN
66. ACESSO SEUMA
67. ACESSO SEMACE
68. ACESSO IBAMA
69. ACESSO FAP/INSS
70. ACESSO CRF
71. SENHA SEMACE
72. ANVISA GESTOR
73. ANVISA EMPRESA

### Procurações (12 campos)
74. PROCURAÇÃO RECEITA
75. DATA PROCURAÇÃO RECEITA
76. PROCURAÇÃO DTe
77. DATA PROCURAÇÃO DTe
78. PROCURAÇÃO CAIXA
79. DATA PROCURAÇÃO CAIXA
80. PROCURAÇÃO EMP WEB
81. DATA PROCURAÇÃO EMP WEB
82. PROCURAÇÃO DET
83. DATA PROCURAÇÃO DET
84. OUTRAS PROCURAÇÕES
85. OBSERVAÇÕES PROCURAÇÕES

### Observações e Sistema (9 campos)
86. OBSERVAÇÕES
87. STATUS DO CLIENTE
88. ÚLTIMA ATUALIZAÇÃO
89. DONO/RESPONSÁVEL
90. CLIENTE ATIVO
91. DATA DE CRIAÇÃO
92. ID
93. DOMÉSTICA
94. GERA ARQUIVO DO SPED

---

## 🎯 DASHBOARD (index_modern.html) - CAMPOS EXIBIDOS

### Tabela Principal:
| Coluna | Campo Google Sheets | Template Key |
|--------|-------------------|--------------|
| Nome Fantasia | NOME FANTASIA NA RECEITA | nomeFantasiaReceita |
| Razão Social | RAZÃO SOCIAL NA RECEITA | razaoSocialReceita |
| CNPJ | CNPJ | cnpj |
| Status | STATUS DO CLIENTE | statusCliente/ativo |
| IE | INSCRIÇÃO ESTADUAL | inscEst |
| IM | INSCRIÇÃO MUNICIPAL | inscMun |
| Regime | REGIME FEDERAL | tributacao |
| Perfil | PERFIL | perfil |
| Serviços | SERVIÇO CT/FS/DP | ct, fs, dp |

### ⚠️ INCONSISTÊNCIAS IDENTIFICADAS:
1. **Campo "tributacao"** no dashboard não existe no mapeamento Google Sheets
2. **Deveria usar "regimeFederal"** para consistência

---

## 📝 CADASTRO (client_form_modern.html + client_form_complete.html)

### Campos Principais (form_modern):
- nomeEmpresa → NOME DA EMPRESA
- razaoSocialReceita → RAZÃO SOCIAL NA RECEITA
- nomeFantasiaReceita → NOME FANTASIA NA RECEITA
- cpfCnpj → CNPJ
- estado → ESTADO
- cidade → CIDADE
- inscEst → INSCRIÇÃO ESTADUAL
- inscMun → INSCRIÇÃO MUNICIPAL
- segmento → SEGMENTO
- atividade → ATIVIDADE
- regimeEstadual → REGIME ESTADUAL
- regimeFederal → REGIME FEDERAL

### Serviços:
- bpoFinanceiro → SERVIÇO BPO FINANCEIRO
- ct → SERVIÇO CT
- fs → SERVIÇO FS
- dp → SERVIÇO DP
- dataInicioServicos → DATA INÍCIO DOS SERVIÇOS

### Procurações (form_complete):
- procReceita → PROCURAÇÃO RECEITA
- procDte → PROCURAÇÃO DTe
- procCaixa → PROCURAÇÃO CAIXA
- procEmpWeb → PROCURAÇÃO EMP WEB
- procDet → PROCURAÇÃO DET

### ✅ MAPEAMENTO CORRETO:
Todos os campos estão corretamente mapeados entre formulários e Google Sheets.

---

## 👁️ VER DETALHES (client_view_modern_new.html)

### Procurações:
| Template | Google Sheets | Status |
|----------|---------------|--------|
| Proc. Receita | PROCURAÇÃO RECEITA | ✅ Correto |
| Proc. DTe | PROCURAÇÃO DTe | ✅ Correto |
| Proc. Caixa | PROCURAÇÃO CAIXA | ✅ Correto |
| Proc. Emp. Web | PROCURAÇÃO EMP WEB | ✅ Correto |
| Proc. DET | PROCURAÇÃO DET | ✅ Correto |

### Observações e Dados Adicionais:
- observacoes → OBSERVAÇÕES ✅
- ultimaAtualizacao → ÚLTIMA ATUALIZAÇÃO ✅
- criadoEm → DATA DE CRIAÇÃO ✅

### ✅ MAPEAMENTO CORRETO:
Nomes das procurações foram corrigidos para manter consistência com formulário.

---

## 🔧 BACKEND MAPPING (google_sheets_service_account.py)

### client_to_row() - ✅ CORRETO:
Todos os 94 campos estão corretamente mapeados na sequência dos cabeçalhos.

### row_to_client() - ✅ CORRETO:
Mapeamento reverso funcionando corretamente.

---

## 🚨 PROBLEMAS IDENTIFICADOS E SOLUÇÕES

### 1. Campo "tributacao" no Dashboard
**Problema:** Dashboard usa `client['tributacao']` que não existe
**Solução:** ✅ CORRIGIDO - Alterado para `client['regimeFederal']`

### 2. Status no Dashboard
**Problema:** Lógica complexa para determinar status
**Solução:** ✅ Já corrigido - usa statusCliente com fallback para ativo

### 3. Nomes das Procurações
**Problema:** ✅ Já corrigido - nomes inconsistentes entre telas
**Solução:** ✅ Já aplicado - uniformizados como "Proc. X"

---

## 📋 RECOMENDAÇÕES FINAIS

### Imediatas:
1. ✅ CORRIGIDO - Campo "tributacao" no dashboard alterado para "regimeFederal"
2. ✅ VALIDADO - Todos os templates usam os mesmos nomes de campos
3. ✅ VALIDADO - Mapeamento de todos os campos correto

### Melhorias:
1. Criar constantes para nomes de campos em arquivo separado
2. Implementar validação de integridade entre templates e backend
3. Documentar mapeamento de campos em arquivo README

---

## 📊 RESUMO DE CONFORMIDADE

| Componente | Status | Observações |
|------------|--------|-------------|
| Google Sheets | ✅ | 94 campos estruturados |
| Backend Mapping | ✅ | Mapeamento completo |
| Formulário Cadastro | ✅ | Campos alinhados |
| Tela Ver Detalhes | ✅ | Procurações corrigidas |
| Dashboard | ✅ | Campo "tributacao" corrigido |

**Taxa de Conformidade: 100%**

---

*Relatório gerado em 13/08/2025*
*Sistema: SIGEC - Control Contabilidade*
