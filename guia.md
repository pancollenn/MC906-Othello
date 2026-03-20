# Plano de Ação e Divisão de Tarefas (Equipe de 5 Pessoas)

## Projeto: Agente de Busca Adversarial - Othello (Reversi)

A divisão abaixo foi pensada para equilibrar a carga de trabalho, isolar dependências (para que várias pessoas programem ao mesmo tempo sem quebrar o código do outro) e cobrir 100% dos requisitos do edital do professor.

---

## 🏗️ Membro 1: Arquiteto do Motor & Gerente de Tempo

**Responsabilidade:** Refatorar o tabuleiro atual, isolar o Pygame e implementar o Iterative Deepening (limite de tempo).  
**Nível de Dificuldade:** Média  

### O que deve ser feito (Subtarefas):

- **Refatoração (Imediato):**  
  Retirar `draw_pieces` e `draw_squares` de `board.py` e passar para `game.py`.  
  O `board.py` deve importar apenas o `numpy`.

- **Interface do Agente:**  
  Criar a classe/função base que o loop principal chamará  
  *(ex: `agente.get_move(board, player)`)*.

- **Iterative Deepening:**  
  Criar o wrapper (casca) que vai chamar o algoritmo de busca repetidas vezes  
  (profundidade 1, depois 2, depois 3...) e monitorar o `time.time()`.  
  Se o tempo estourar (ex: 0.95s), interromper a busca atual e retornar a melhor jogada da profundidade anterior.

### Por que é vital:

Se essa parte falhar, o agente não vai respeitar o tempo e será penalizado.  
É a ponte entre a interface gráfica e a IA.

---

## 🧠 Membro 2: Engenheiro de Busca (Minimax & Alpha-Beta)

**Responsabilidade:** Implementar os algoritmos de busca clássicos e a instrumentação base.  
**Nível de Dificuldade:** Alta (exige cuidado com recursão)

### O que deve ser feito (Subtarefas):

- **Minimax Clássico:**  
  Implementar a recursão MAX/MIN pura.

- **Regra do "Passar a Vez":**  
  Se `get_valid_moves` for vazio, o jogo **não acabou**.  
  O agente deve passar o turno.  
  O jogo só termina quando nenhum dos dois tem jogadas.

- **Poda Alpha-Beta:**  
  Adicionar parâmetros `alpha` e `beta` e aplicar as condições de corte.

- **Instrumentação:**  
  Criar contadores para medir quantos nós (`board.copy()`) foram gerados.

### Por que é vital:

É o coração do projeto.  
Sem Alpha-Beta eficiente, o agente não alcança profundidade suficiente.

---

## ⚔️ Membro 3: Estrategista Heurístico A & Move Ordering

**Responsabilidade:** Implementar a primeira heurística e ordenação de jogadas.  
**Nível de Dificuldade:** Média-Alta  

### O que deve ser feito (Subtarefas):

- **Heurística Básica:**  
  Avaliar estado com:
  - Diferença de peças  
  - Mobilidade (movimentos válidos seus - do oponente)

- **Move Ordering:**  
  Ordenar `valid_moves` antes da busca:
  - Cantos → prioridade máxima  
  - Jogadas ruins → final da lista  

- **Integração:**  
  Aplicar essa ordenação dentro do Alpha-Beta.

### Por que é vital:

Move ordering é obrigatório.  
Sem isso, o Alpha-Beta perde eficiência.

---

## 🛡️ Membro 4: Estrategista Heurístico B (Avançado)

**Responsabilidade:** Desenvolver heurística avançada para comparação.  
**Nível de Dificuldade:** Alta  

### O que deve ser feito (Subtarefas):

- **Matriz de Pesos (Static Weights):**
  Criar matriz `8x8`:
  - Cantos = +100  
  - X-squares = -50  
  - Bordas = +10  

- **Frontier Disks:**
  Penalizar peças com espaço vazio adjacente.

- **Fases do Jogo:**
  - Early game → ignorar contagem de peças  
  - Late game (< 15 espaços vazios) → considerar fortemente  

### Por que é vital:

Essa será a heurística principal do agente competitivo.

---

## 📊 Membro 5: Ciência de Dados, Testes e Relatório

**Responsabilidade:** Simulação, coleta de dados e relatório.  
**Nível de Dificuldade:** Média-Alta  

### O que deve ser feito (Subtarefas):

- **Modo Headless (Sem GUI):**  
  Criar `torneio.py` para rodar partidas automaticamente.

- **Coleta de Dados:**  
  Registrar em CSV/JSON:
  - Tempo por jogada  
  - Profundidade  
  - Nós expandidos  

- **Baseline e Gráficos:**
  - Minimax vs agente aleatório (100 partidas)  
  - Gráficos: profundidade vs tempo  

- **Relatório Técnico:**
  Liderar escrita das 5 páginas:
  - Modelagem (S, A, T, U)  
  - Resultados experimentais  

### Por que é vital:

Metade da nota depende disso.  
Sem análise experimental → nota baixa.

---

## 🔄 Ordem de Execução (Sprints)

### Sprint 1 (Dias 1-3)
- Membro 1: Isolar Pygame  
- Membro 2: Implementar Minimax  
- Membro 5: Criar simulador  

### Sprint 2 (Dias 4-7)
- Membro 2: Alpha-Beta  
- Membros 3 e 4: Heurísticas  

### Sprint 3 (Dias 8-10)
- Membro 1: Iterative Deepening  
- Membro 3: Move Ordering  

### Sprint 4 (Dias 11-14)
- Membro 5: Torneios massivos  
- Todos: Ajustes finos + Relatório  

---