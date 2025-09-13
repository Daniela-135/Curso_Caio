import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import datetime

# Cabeçalho para simular navegador e evitar bloqueio
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36'
}

# Variáveis de configuração
baseURL = "https://www.adorocinema.com/filmes/melhores/"
filmes = []  # Lista para armazenar os dados
data_hoje = datetime.date.today().strftime("%d-%m-%Y")
paginaLimite = 5
card_temp_min = 1
card_temp_max = 3
pg_temp_min = 3
pg_temp_max = 4
pasta = "C:/Users/sabado/Desktop/Python AD Daniela/python_analise_dados-main/"
saidaCSV = f'filmes_adoro_cinema_{data_hoje}.csv'

# Loop pelas páginas
for pagina in range(1, paginaLimite + 1):
    url = f"{baseURL}?page={pagina}"
    print(f"Coletando dados da página: {pagina} \nURL: {url}")
    resposta = requests.get(url, headers=headers)

    if resposta.status_code != 200:
        print(f"Erro ao carregar a página {pagina}. Código do erro: {resposta.status_code}")
        continue

    soup = BeautifulSoup(resposta.text, "html.parser")
    cards = soup.find_all("div", class_="card entity-card entity-card-list cf")

    for card in cards:
        try:
            # Título e link do filme
            titulo_tag = card.find("a", class_="meta-title-link")
            titulo = titulo_tag.text.strip() if titulo_tag else "N/A"
            link = "https://www.adorocinema.com" + titulo_tag['href'] if titulo_tag else None

            # Nota do filme
            nota_tag = card.find("span", class_="stareval-note")
            nota = nota_tag.text.strip().replace(',', '.') if nota_tag else "N/A"

            if link:
                # Requisição para a página do filme
                filme_resposta = requests.get(link, headers=headers)
                filme_soup = BeautifulSoup(filme_resposta.text, "html.parser")

                # Diretor
                diretor_tag = filme_soup.find("div", class_="meta-body-item meta-body-direction meta-body-oneline")
                diretor = (
                    diretor_tag.text
                    .strip()
                    .replace('Direção:', '')
                    .replace(',', '')
                    .replace('|', '')
                    .replace('\n', ' ')
                    .replace('\r', '')
                    .strip()
                ) if diretor_tag else "N/A"

                # Gêneros
                genero_blocks = filme_soup.find('div', class_='meta-body-info')
                if genero_blocks:
                    genero_links = genero_blocks.find_all('a')
                    generos = [g.text.strip() for g in genero_links]
                    categoria = ", ".join(generos[:3]) if generos else "N/A"
                else:
                    categoria = "N/A"

                # Ano de lançamento
                ano_tag = genero_blocks.find('span', class_='date') if genero_blocks else None
                ano = ano_tag.text.strip() if ano_tag else "N/A"

                # Verifica se os dados são válidos antes de salvar
                if titulo != "N/A" and link != "N/A" and nota != "N/A":
                    filmes.append({
                        "Titulo": titulo,
                        "Direção": diretor,
                        "Nota": nota,
                        "Link": link,
                        "Ano": ano,
                        "Categoria": categoria
                    })
                else:
                    print(f"Filme incompleto ou erro na coleta de dados: {titulo}")

                # Tempo aleatório entre requisições de filmes
                tempo = random.uniform(card_temp_min, card_temp_max)
                time.sleep(tempo)

        except Exception as erro:
            print(f"Erro ao processar o filme {titulo}\nErro: {erro}")

    # Tempo entre páginas
    tempo = random.uniform(pg_temp_min, pg_temp_max)
    time.sleep(tempo)

# Salva os dados em CSV
df = pd.DataFrame(filmes)
df.to_csv(pasta + saidaCSV, sep=';', index=False, encoding='utf-8-sig')
print(f"\nTotal de filmes coletados: {len(filmes)}")
