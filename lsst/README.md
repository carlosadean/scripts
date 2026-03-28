---
**Criado com auxílio do Gemini**

# 📑 Automação de Relatórios Rubin (IDAC-BR)

Esta automação consiste em um Google Apps Script vinculado à planilha de controle de atividades. O objetivo é extrair dados da aba **"Entries"** e formatá-los automaticamente seguindo os padrões exigidos pelo Rubin Observatory, utilizando sintaxe **Markdown** para facilitar o uso em editores de texto.

## 🚀 Como Usar

1. No menu superior da planilha, clique em **Rubin Report**.
2. Selecione uma das três opções:
   * **1. Relatório ANUAL:** Consolida tarefas de todo o ano fiscal (FY).
   * **2. Relatório QUARTER (Específico):** Gera o progresso detalhado de um trimestre específico.
   * **3. PLANO DE TRABALHO (Next Quarter):** Gera o planejamento para o trimestre seguinte.
3. Responda aos prompts (ex: `FY26`, `Q2`).
4. Uma nova aba será criada (ou atualizada) com o texto formatado.

---

## 🛠️ Lógica de Funcionamento

### 1. Relatório Anual (Consolidado)
* **Agrupamento:** Identifica tarefas repetidas entre quarters pelo título e consolida em uma única entrada.
* **Tags de Tempo:** Adiciona tags como `[P Q1-Q3]` (Planned, do Q1 ao Q3) ou `[U Q2]` (Unplanned, apenas Q2).
* **Status Final:** Exibe apenas o status mais recente da tarefa no ano.

### 2. Relatório de Quarter (Progresso)
* **Filtro Rígido:** Lista apenas o que aconteceu no trimestre selecionado.
* **Estrutura:** Exibe o título em negrito seguido pela descrição e o status mapeado.

### 3. Plano de Trabalho (Work Plan)
* **Continuidade:** Identifica tarefas do trimestre atual que estão `In Progress` ou `Ongoing` e adiciona automaticamente o prefixo **"Continue"**.
* **Novas Tarefas:** Busca na planilha linhas do quarter subsequente com status `Planned` ou vazio.
* **Simplificação:** Gera uma lista de itens (bullet points) focada em entregas futuras.

---

## 🎨 Formatação de Saída (Markdown)

Para garantir a legibilidade, o script aplica as seguintes regras:

* **Títulos de Seção:** Usa `## NOME DA ÁREA` (ex: `## HARDWARE`).
* **Destaque de Atividades:** Títulos e status são formatados em negrito: `**Título da Atividade - STATUS**`.
* **Status Mapping:** Converte termos internos para o padrão Rubin:
    * *Done* → `COMPLETE`
    * *Ongoing/In Progress* → `ONGOING`
    * *Postponed/Canceled* → `POSTPONED` / `CANCELLED`
* **Espaçamento:** * Uma linha em branco entre cada atividade dentro de uma seção.
    * Uma linha horizontal (`---`) entre seções diferentes, com duas linhas de espaço acima e abaixo para respiro visual.

---

## 📋 Requisitos da Planilha (Aba "Entries")

O script depende das seguintes colunas (os nomes devem ser exatos no cabeçalho):
* `Activity / Title`: Nome da tarefa.
* `FY`: Ano fiscal (ex: FY26).
* `Quarter`: Trimestre (Q1, Q2, Q3, Q4).
* `Area`: Categoria (Hardware, Software, IAM, etc).
* `Status`: Status da tarefa.
* `Description (1-2 lines)`: Detalhamento técnico.
* `Type (PQ/UQ)`: Define se é Planejado (PQ) ou Não Planejado (UQ).
