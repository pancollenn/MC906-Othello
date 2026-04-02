import os
import re
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# CONFIGURAÇÃO DOS DIRETÓRIOS
# ==========================================
# Caminho da pasta que contém os arquivos .txt (relativo ao plot.py)
LOGS_DIR = "results" 

# Caminho da pasta onde os gráficos serão salvos
OUTPUT_DIR = "graficos"
# ==========================================

def parse_results(logs_path):
    """Lê os arquivos txt da pasta especificada e extrai os dados do torneio."""
    data = []
    
    # Monta o caminho de busca: ex: "results/*vs*.txt"
    search_pattern = os.path.join(logs_path, '*vs*.txt')
    files = glob.glob(search_pattern)
    
    if not files:
        print(f"Atenção: Nenhum arquivo encontrado buscando por '{search_pattern}'.")
        return pd.DataFrame()
        
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Extraindo nomes e profundidades do título
            match_title = re.search(r'=== TORNEIO: (\w+)\(d=(\d+)\) vs (\w+)\(d=(\d+)\) ===', content)
            if not match_title:
                continue
                
            p1_name, p1_d, p2_name, p2_d = match_title.groups()
            
            # Extraindo vitórias
            wins = re.findall(r'Vitórias \w+: (\d+)', content)
            draws_match = re.search(r'Empates: (\d+)', content)
            time_match = re.search(r'Média por partida: ([\d.]+)s', content)
            
            if len(wins) >= 2 and draws_match and time_match:
                data.append({
                    'P1': f"{p1_name}(d={p1_d})",
                    'P2': f"{p2_name}(d={p2_d})",
                    'P1_Name': p1_name,
                    'P2_Name': p2_name,
                    'P1_Depth': int(p1_d),
                    'P2_Depth': int(p2_d),
                    'P1_Wins': int(wins[0]),
                    'P2_Wins': int(wins[1]),
                    'Draws': int(draws_match.group(1)),
                    'Avg_Time_s': float(time_match.group(1))
                })
                
    return pd.DataFrame(data)

def plot_analysis(df, output_path):
    if df.empty:
        print("Cancelando a geração de gráficos pois não há dados.")
        return

    # Garante que a pasta de saída exista
    os.makedirs(output_path, exist_ok=True)
    sns.set_theme(style="whitegrid")
    
    # --- Gráfico 1: Heatmap de Win Rate Geral ---
    plt.figure(figsize=(10, 8))
    df['Total_Games'] = df['P1_Wins'] + df['P2_Wins'] + df['Draws']
    df['P1_Win_Rate'] = (df['P1_Wins'] / df['Total_Games']) * 100
    
    pivot = df.pivot(index='P1', columns='P2', values='P1_Win_Rate')
    sns.heatmap(pivot, annot=True, cmap="YlGnBu", fmt=".1f", cbar_kws={'label': '% de Vitória do P1'})
    plt.title("Taxa de Vitória (%) - Jogador 1 vs Jogador 2")
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, "1_win_rate_heatmap.png"))
    plt.close()

    # --- Gráfico 2: Vantagem da Profundidade (Mesma Heurística d=4 vs d=6) ---
    depth_df = df[(df['P1_Name'] == df['P2_Name']) & 
                  (df['P1_Depth'] == 4) & (df['P2_Depth'] == 6)].copy()
    
    if not depth_df.empty:
        plt.figure(figsize=(8, 5))
        bar_width = 0.35
        x = range(len(depth_df))
        
        plt.bar(x, depth_df['P1_Wins'], width=bar_width, label='Vitórias d=4', color='#FF9999')
        plt.bar([i + bar_width for i in x], depth_df['P2_Wins'], width=bar_width, label='Vitórias d=6', color='#66B2FF')
        
        plt.xlabel('Heurística')
        plt.ylabel('Número de Vitórias')
        plt.title('Impacto da Profundidade: d=4 vs d=6 (Mesma Heurística)')
        plt.xticks([i + bar_width/2 for i in x], depth_df['P1_Name'])
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_path, "2_depth_advantage.png"))
        plt.close()

    # --- Gráfico 3: Custo Computacional vs Profundidade ---
    plt.figure(figsize=(8, 5))
    df['Max_Depth'] = df[['P1_Depth', 'P2_Depth']].max(axis=1)
    
    time_df = df.groupby('Max_Depth')['Avg_Time_s'].mean().reset_index()
    
    sns.barplot(data=time_df, x='Max_Depth', y='Avg_Time_s', palette="viridis")
    plt.title("Tempo Médio por Partida vs Profundidade Máxima Usada")
    plt.xlabel("Profundidade (d)")
    plt.ylabel("Tempo Médio por Partida (segundos)")
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, "3_time_vs_depth.png"))
    plt.close()

    # --- Gráfico 4: Gráficos de Pizza Individuais por Confronto (Com Legenda) ---
    pie_output_dir = os.path.join(output_path, "winrates_pizza")
    os.makedirs(pie_output_dir, exist_ok=True)
    
    for index, row in df.iterrows():
        p1_label = row['P1']
        p2_label = row['P2']
        
        # Filtra os valores para o gráfico de pizza (remove as fatias que são zero)
        labels_raw = [f"{p1_label} (Vitórias)", f"{p2_label} (Vitórias)", 'Empates']
        sizes_raw = [row['P1_Wins'], row['P2_Wins'], row['Draws']]
        colors_raw = ["#0a5d7b", "#8b0fa4", "#AB699A"]
        
        labels = [l for l, s in zip(labels_raw, sizes_raw) if s > 0]
        sizes = [s for s in sizes_raw if s > 0]
        colors = [c for c, s in zip(colors_raw, sizes_raw) if s > 0]
        
        # Ajuste no tamanho da figura para acomodar a legenda ao lado
        fig, ax = plt.subplots(figsize=(7, 5))
        
        # Passamos as fatias (wedges) para variáveis para usar na legenda
        wedges, texts, autotexts = ax.pie(sizes, colors=colors, autopct='%1.1f%%', startangle=140, 
                                          wedgeprops={'edgecolor': 'black', 'linewidth': 1})
        
        plt.title(f"Confronto: {p1_label} vs {p2_label}", pad=20, fontsize=14, fontweight='bold')
        
        # Adiciona a legenda fora do gráfico, alinhada à direita
        ax.legend(wedges, labels,
                  title="Legenda",
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1))
        
        # Limpa o nome do arquivo
        safe_p1 = p1_label.replace('(', '_').replace(')', '').replace('=', '')
        safe_p2 = p2_label.replace('(', '_').replace(')', '').replace('=', '')
        filename = f"pizza_{safe_p1}_vs_{safe_p2}.png"
        
        # bbox_inches='tight' garante que a legenda não seja cortada ao salvar
        plt.savefig(os.path.join(pie_output_dir, filename), bbox_inches='tight')
        plt.close()
    
    print(f"Gráficos gerais salvos em '{output_path}'")
    print(f"Gráficos de pizza (com legendas) salvos em '{pie_output_dir}'")

if __name__ == "__main__":
    print(f"Processando arquivos da pasta '{LOGS_DIR}'...")
    df_results = parse_results(LOGS_DIR)
    plot_analysis(df_results, OUTPUT_DIR)