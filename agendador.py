from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import datetime
import pandas as pd
import os
import time

marcas = ["renault", "peugeot", "vw", "bmw", "mercedes-benz", "audi", "byd", "land-rover", "jaguar", "mazda", "mini", "nissan", "porsche", "tesla", "volvo"]

def configurar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    )
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def contar_anuncios(driver, marca):
    url = f"https://www.standvirtual.com/carros/{marca}/"
    driver.get(url)
    try:
        wait = WebDriverWait(driver, 15)
        p = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//p[contains(text(), 'Número de anúncios:')]")
        ))
        b = p.find_element(By.TAG_NAME, "b")
        total_texto = b.text.strip().replace(" ", "")
        total = int(total_texto)
        print(f"{marca.upper()}: {total} anúncios")
        return total
    except TimeoutException:
        print(f"Timeout: elemento 'Número de anúncios:' não encontrado para {marca}")
        return 0
    except Exception as e:
        print(f"Erro ao obter anúncios para {marca}: {e}")
        return 0

def salvar_dados_acumulados(novos_dados, ficheiro_saida):
    if os.path.exists(ficheiro_saida):
        df_existente = pd.read_csv(ficheiro_saida)
        df_atualizado = pd.concat([df_existente, pd.DataFrame(novos_dados)], ignore_index=True)
        df_atualizado.drop_duplicates(subset=["Marca", "Data"], keep="last", inplace=True)
    else:
        df_atualizado = pd.DataFrame(novos_dados)
    df_atualizado.to_csv(ficheiro_saida, index=False)

def gerar_html(ficheiro_saida):
    df = pd.read_csv(ficheiro_saida)
    grupos = df.groupby("Marca")

    html = f"""
    <!DOCTYPE html>
    <html lang="pt">
    <head>
    <meta charset="UTF-8">
    <title>Estatísticas Standvirtual</title>
    <style>
        body {{
        font-family: Arial, sans-serif;
        padding: 20px;
        background: #f7f7f7;
        }}
        table {{
        border-collapse: collapse;
        width: 100%;
        background: white;
        margin-bottom: 40px;
        }}
        th, td {{
        border: 1px solid #ccc;
        padding: 8px;
        text-align: center;
        }}
        th {{
        background-color: #3f51b5;
        color: white;
        }}
        tr:nth-child(even) {{
        background-color: #f2f2f2;
        }}
        h1 {{
        color: #333;
        }}
        h2 {{
        color: #2c387e;
        margin-top: 40px;
        }}
    </style>
    </head>
    <body>
    <h1>📊 Estatísticas de Anúncios por Marca - Standvirtual</h1>
    <p>Última atualização: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    """

    for marca, grupo in grupos:
        html += f"<h2>{marca.upper()}</h2>\n"
        html += """
        <table>
        <thead>
            <tr>
            <th>Data</th>
            <th>Total de Anúncios</th>
            </tr>
        </thead>
        <tbody>
        """
        for _, row in grupo.iterrows():
            html += f"<tr><td>{row['Data']}</td><td>{row['Total_Anuncios']}</td></tr>\n"
        html += """
        </tbody>
        </table>
        """

    html += """
    </body>
    </html>
    """

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ index.html atualizado com sucesso!")

def main():
    driver = configurar_driver()

    while True:
        print("\n🕐 Início do ciclo:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        data_hoje = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        dados = []
        for marca in marcas:
            total = contar_anuncios(driver, marca)
            dados.append({"Marca": marca, "Data": data_hoje, "Total_Anuncios": total})

        os.makedirs("dados_semanais", exist_ok=True)
        ficheiro_saida = "dados_semanais/contagem_anuncios_acumulado_por_marca.csv"
        salvar_dados_acumulados(dados, ficheiro_saida)

        gerar_html(ficheiro_saida)

        print("🕒 A aguardar 1 hora...\n")
        time.sleep(3600)

if __name__ == "__main__":
    main()
