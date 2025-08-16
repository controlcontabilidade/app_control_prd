# 🔧 INSTRUÇÕES PARA TESTE MANUAL - DEBUG SÓCIOS

## 🎯 PROBLEMA IDENTIFICADO
O sistema possui **autenticação ativa**, por isso os testes automáticos não funcionam. Você precisa fazer o teste **logado** no sistema.

## 📋 PASSOS PARA DEBUG MANUAL

### 1. **Preparação**
✅ O código de debug já foi adicionado ao `app.py`  
✅ Quando você acessar um cliente, aparecerão logs detalhados no terminal do servidor

### 2. **Executar o Debug**

1. **Certifique-se que o servidor está rodando:**
   ```bash
   python app.py
   ```

2. **Abra o navegador e faça login no sistema:**
   - Acesse: `http://localhost:5000`
   - Faça login com suas credenciais

3. **Acesse o cliente "Ana Paula":**
   - Navegue até o cliente que tem o problema
   - Clique para ver os detalhes do cliente

4. **Observe o terminal do servidor - procure por:**
   ```
   🔍 [VIEW] ===== DEBUG TODOS OS CAMPOS =====
   🔍 [VIEW] ===== TESTE ESPECÍFICO SÓCIOS =====
   ```

### 3. **O que observar nos logs**

#### ✅ **Se os sócios estão salvos corretamente, você verá:**
```
🔍 [VIEW] ENCONTRADO: socio_1_nome = Ana Paula
🔍 [VIEW] ENCONTRADO: socio1_nome = Ana Paula
🔍 [VIEW] ENCONTRADO: socio_1_cpf = 020.519.665-33
```

#### ❌ **Se há problema nos dados, você verá:**
```
🔍 [VIEW] NÃO EXISTE: socio_1_nome
🔍 [VIEW] NÃO EXISTE: socio1_nome
🔍 [VIEW] NÃO EXISTE: socio_1_cpf
```

#### 🔍 **Se os dados estão em formato diferente:**
```
🔍 [VIEW] SÓCIO 1 NOME: Ana Paula    (formato Google Sheets)
🔍 [VIEW] SÓCIO 1 CPF: 020.519.665-33
```

### 4. **Possíveis Resultados**

#### **CENÁRIO A: Dados não existem**
- **Problema:** Cliente foi criado antes da correção
- **Solução:** Recriar o cliente ou migrar dados

#### **CENÁRIO B: Dados estão em formato Google Sheets**
- **Problema:** Template procura por `socio_1_nome` mas dados estão como `SÓCIO 1 NOME`
- **Solução:** Corrigir o mapeamento no template

#### **CENÁRIO C: Dados estão corretos**
- **Problema:** Template não está encontrando os campos
- **Solução:** Corrigir lógica do template

## 🚨 APÓS EXECUTAR O TESTE

**Copie e cole aqui os logs que aparecerem no terminal**, especialmente:
- A seção `===== DEBUG TODOS OS CAMPOS =====`
- A seção `===== TESTE ESPECÍFICO SÓCIOS =====`

Com esses logs, conseguirei identificar exatamente onde está o problema e implementar a correção final.

## ⚡ CORREÇÃO RÁPIDA (se necessário)

Se o problema for que os dados estão em formato Google Sheets (`SÓCIO 1 NOME` em vez de `socio_1_nome`), eu posso corrigir o template imediatamente.

---

**👉 Execute o teste manual e me envie os logs do terminal!**
