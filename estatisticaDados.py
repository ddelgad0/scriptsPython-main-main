import pandas as pd

# Carregar dados acumulados
ficheiro = "dados_semanais/contagem_anuncios_acumulado_por_marca.csv"
df = pd.read_csv(ficheiro)

# Converter a coluna Data para datetime
df["Data"] = pd.to_datetime(df["Data"])

# Ordenar por Marca e Data
df = df.sort_values(by=["Marca", "Data"])

# Calcular a diferença diária do total de anúncios para cada marca
df["Diferença"] = df.groupby("Marca")["Total_Anuncios"].diff()

# Para ver as maiores variações positivas (mais anúncios acrescentados)
df_positivos = df[df["Diferença"] > 0]

# Marca e data da maior subida
if not df_positivos.empty:
    maior_subida = df_positivos.loc[df_positivos["Diferença"].idxmax()]
    print("Marca com maior aumento de anúncios entre duas datas:")
    print(f"Marca: {maior_subida['Marca']}")
    print(f"Data: {maior_subida['Data'].date()}")
    print(f"Aumento de anúncios: {int(maior_subida['Diferença'])}")
else:
    print("Não foram encontradas diferenças positivas entre datas.")

# Opcional: mostrar todas as diferenças positivas por marca
print("\nResumo dos aumentos positivos por marca:")
print(df_positivos.groupby("Marca")["Diferença"].max().sort_values(ascending=False))
