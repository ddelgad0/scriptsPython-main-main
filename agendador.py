import subprocess
import pandas as pd
import os
from datetime import datetime

# Caminhos
caminho_csv = "dados_semanais/contagem_anuncios_acumulado_por_marca.csv"
caminho_html = "dados_semanais/index.html"
caminho_script = "scriptStandVirtualPorMarca.py"

def gerar_pagina_html(csv_path, html_output_path):
    if not os.path.exists(csv_path):
        print(f"❌ Ficheiro CSV não encontrado: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    if df.empty:
        print("⚠️ CSV está vazio. Nenhum dado para gerar HTML.")
        return

    ultima_data = df["Data"].max()
    df_ultima = df[df["Data"] == ultima_data].sort_values(by="Total_Anuncios", ascending=False)

    html = f"""
    <html>
    <head><meta charset="UTF-8"><title>Contagem de Anúncios</title>
    <style>
        body {{ font-family: Arial; background: #f0f0f0; padding: 20px; }}
        table {{ border-collapse: collapse; width: 100%; background: white; }}
        th, td {{ border: 1px solid #ccc; padding: 10px; text-align: left; }}
        th {{ background-color: #0073e6; color: white; }}
    </style></head><body>
        <h1>📊 Contagem de Anúncios por Marca</h1>
        <p>📅 Última atualização: {ultima_data}</p>
        <table>
            <tr><th>Marca</th><th>Total de Anúncios</th></tr>
            {''.join(f"<tr><td>{row['Marca'].capitalize()}</td><td>{row['Total_Anuncios']}</td></tr>" for _, row in df_ultima.iterrows())}
        </table>
    </body></html>
    """
    with open(html_output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Página HTML gerada em: {html_output_path}")

def executar_scraper(script_path):
    print("🚀 A executar o script de scraping...")
    resultado = subprocess.run(["python", script_path], capture_output=True, text=True)

    if resultado.returncode == 0:
        print("✅ Script executado com sucesso.")
        return True
    else:
        print("❌ Erro ao executar o script:")
        print(resultado.stderr)
        return False

# EXECUÇÃO
if executar_scraper(caminho_script):
    gerar_pagina_html(caminho_csv, caminho_html)
