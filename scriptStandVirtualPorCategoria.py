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

# Configurações do Chrome headless com user-agent para evitar bloqueios
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

categoria = ["comerciais", "carros", "motos"]
data_hoje = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def contar_anuncios(categoria):
    url = f"https://www.standvirtual.com/{categoria}/"
    driver.get(url)
    try:
        wait = WebDriverWait(driver, 15)
        p = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//p[contains(text(), 'Número de anúncios:')]")
        ))
        b = p.find_element(By.TAG_NAME, "b")
        total_texto = b.text.strip().replace(" ", "")
        total = int(total_texto)
        print(f"{categoria.upper()}: {total} anúncios")
        return total
    except TimeoutException:
        print(f"Timeout: elemento 'Número de anúncios:' não encontrado para {categoria}")
        return 0
    except Exception as e:
        print(f"Erro ao obter anúncios para {categoria}: {e}")
        return 0

def salvar_dados_acumulados(novos_dados, ficheiro_saida):
    if os.path.exists(ficheiro_saida):
        df_existente = pd.read_csv(ficheiro_saida)
        df_atualizado = pd.concat([df_existente, pd.DataFrame(novos_dados)], ignore_index=True)
        # Remover duplicados mantendo a última entrada por categoria + Data
        df_atualizado.drop_duplicates(subset=["categoria", "Data"], keep="last", inplace=True)
    else:
        df_atualizado = pd.DataFrame(novos_dados)

    df_atualizado.to_csv(ficheiro_saida, index=False)

dados = []
for categoria in categoria:
    total = contar_anuncios(categoria)
    dados.append({"categoria": categoria, "Data": data_hoje, "Total_Anuncios": total})

driver.quit()

os.makedirs("dados_semanais", exist_ok=True)
ficheiro_saida = "dados_semanais/contagem_anuncios_acumulado_por_categoria.csv"
salvar_dados_acumulados(dados, ficheiro_saida)
print(f"\n✅ Dados acumulados salvos em: {ficheiro_saida}")
