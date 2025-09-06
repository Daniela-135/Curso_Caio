#inicio da aula 30/08
from flask import Flask, request, render_template_string
import pandas as pd 
import sqlite3
import plotly.express as px
import plotly.io as pio
import random
import os

pio.renderers.default = "browser"

caminho = "C:/Users/sabado/Desktop/Python AD Daniela/python_analise_dados-main/"
tabela = ["drinks.csv", "avengers.csv"]

codHtml = '''
    <h1> Dashbords - Consumo de Alcool </h1> 
    <h2> Parte 01 </h2>
        <ul>
            <li><a href="/grafico1"> Top 10 paises em consumo de alcool </a></li>
            <li><a href="/grafico2"> Media de consumo por tipo </a></li>
            <li><a href="/grafico3"> Consumo total por região </a></li>
            <li><a href="/grafico4"> Comparativo entre tipos de bebida </a></li>
            <li><a href="/pais"> Insights por pais </a></li>
        </ul>
    <h2> Parte 02 </h2>
        <ul>
            <li><a href="/comparar"> Comparar </a></li>
            <li><a href="/upload"> Upload CSV Vingadores </a></li>
            <li><a href="/apagar"> Apagar Tabela </a></li>
            <li><a href="/ver"> Ver Tabela </a></li>
            <li><a href="/vaa"> V.A.A (Vingadores Alcoólicos Anônimos) </a></li>
        </ul>
'''

def carregarCsv():
    try:
        dfDrinks = pd.read_csv(os.path.join(caminho, tabela[0]))
        dfAvengers = pd.read_csv(os.path.join(caminho, tabela[1]), encoding='latin1')
        return dfDrinks, dfAvengers
    except Exception as erro:
        print(f"Erro ao carregar os arquivos csv: {erro}")
    return None, None

def criarBancoDados():
    conn = sqlite3.connect(f"{caminho}banco01.bd")
    dfDrinks, dfAvengers = carregarCsv()
    if dfDrinks is None or dfAvengers is None:
        print("Falha ao Carregar os Dados!")
        return
    
    dfDrinks.to_sql("bebidas", conn, if_exists="replace", index=False)
    dfAvengers.to_sql("vingadores", conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string(codHtml)

@app.route('/grafico1')
def grafico1():
    with sqlite3.connect(f'{caminho}banco01.bd') as conn:
        df = pd.read_sql_query("""     
            SELECT country, total_litres_of_pure_alcohol
            FROM bebidas
            ORDER BY total_litres_of_pure_alcohol DESC
            LIMIT 10                   
         """, conn)
        
    figuraGrafico01 = px.bar(
        df,
        x="country",
        y="total_litres_of_pure_alcohol",
        title="Top 10 paises com maior consumo de alcool"
    )
    return figuraGrafico01.to_html()

@app.route('/grafico2')
def grafico2():
    with sqlite3.connect(f'{caminho}banco01.bd') as conn:
        df = pd.read_sql_query("""
            SELECT AVG(beer_servings) AS cerveja,
                   AVG(spirit_servings) AS destilados,
                   AVG(wine_servings) AS vinhos
            FROM bebidas
        """, conn)
    
    df_melted = df.melt(var_name='Bebidas', value_name='Média de Porções')
    figuraGrafica02 = px.bar(
        df_melted,
        x="Bebidas",
        y="Média de Porções",
        title='Media de consumo "global" por tipo'
    )
    return figuraGrafica02.to_html()

@app.route('/grafico3')
def grafico3():
    regioes = {
        "Europa": ['France', 'Germany', 'Spain', 'Italy', 'Portugal'],
        "Asia": ['China', 'Japan', 'India', 'Thailand'],
        "Africa": ['Angola', 'Nigeria', 'Egypt', 'Algeria'],
        "Americas": ['USA', 'Canada', 'Brazil', 'Argentina', 'Mexico']
    }
    dados = []
    with sqlite3.connect(f'{caminho}banco01.bd') as conn:
        for regiao, paises in regioes.items():
            placeholders = ",".join([f"'{pais}'" for pais in paises])
            query = f"""
                SELECT SUM(total_litres_of_pure_alcohol) AS total 
                FROM bebidas
                WHERE country IN ({placeholders})
            """
            total = pd.read_sql_query(query, conn).iloc[0, 0]
            dados.append({
                "Região": regiao,
                "Consumo Total": total
            })

    dfRegioes = pd.DataFrame(dados)
    figuraGrafico3 = px.pie(
        dfRegioes,
        names="Região",
        values="Consumo Total",
        title="Consumo Total por Região"
    )
    return figuraGrafico3.to_html()

@app.route('/comparar', methods=['POST','GET'])
def comparar():
    opcoes = [
        'beer_servings',
        'spirit_servings',
        'wine_servings'
    ]
    if request.method == "POST":
        eixoX = request.form.get('eixo_x')
        eixoY = request.form.get('eixo_y')
        if eixoX == eixoY:
            return "<marquee>Você fez besteira.... escolha tabelas diferentes...</marquee>"
        conn = sqlite3.connect(f'{caminho}banco01.bd')
        df = pd.read_sql_query("SELECT country, {}, {} FROM bebidas".format(eixoX, eixoY), conn)
        conn.close()
        figuraComparar = px.scatter(
            df,
            x=eixoX,
            y=eixoY,
            title=f"Comparação entre {eixoX} VS {eixoY}"
        )
        figuraComparar.update_traces(textposition="top center")
        return figuraComparar.to_html()

    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Comparar</title>
    <style>
        /* Estilização geral */
        body {
            font-family: Arial, sans-serif;
            background: #f7f9fc;
            color: #333;
            display: flex;
            justify-content: center;
            padding: 40px;
        }

        /* Título */
        h2 {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 20px;
        }

        /* Formulário */
        form {
            background-color: #fff;
            padding: 25px 30px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            width: 350px;
        }

        /* Labels */
        form label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #34495e;
        }

        /* Selects */
        form select {
            width: 100%;
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid #ccc;
            border-radius: 6px;
            background-color: #f9f9f9;
            font-size: 14px;
        }

        /* Quebra de linha (corrige aparência dos <br>) */
        form br {
            display: none;
        }

        /* Botão de submit */
        form input[type="submit"] {
            background-color: #2980b9;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            width: 100%;
            font-size: 15px;
            transition: background-color 0.3s ease;
        }

        form input[type="submit"]:hover {
            background-color: #1c5980;
        }
    </style>
</head>
<body>
    <!-- Isso é um comentário em html-->
    <h2> Comparar Campos </h2>
    <form method="POST">
        <label for="eixo_x">Eixo X:</label>
        <select name="eixo_x">
            {% for opcao in opcoes %}
                <option value="{{opcao}}">{{opcao}}</option>
            {% endfor %}
        </select>
        <br><br>

        <label for="eixo_y">Eixo Y:</label>
        <select name="eixo_y">
            {% for opcao in opcoes %}
                <option value="{{opcao}}">{{opcao}}</option>
            {% endfor %}
        </select>
        <br><br>

        <input type="submit" value="--Comparar--">
    </form>
</body>
</html>
''', opcoes=opcoes)

#preciso de um css, para deixar esse html, bonito, mas não devemos mexer em nada do html, nem adicionar nenhuma id ou class, 
#só formatar usando css

#"drinks.csv", "avengers.csv"
@app.route('/ver', methods=['GET', 'POST'])
def ver():
    opcoes = ['bebidas', 'vingadores']

    if request.method == "POST":
        tabela_escolhida = request.form.get('tabela')
        if tabela_escolhida not in opcoes:
            return "<marquee>Escolha inválida!</marquee>"

        conn = sqlite3.connect(f'{caminho}banco01.bd')
        df = pd.read_sql_query(f"SELECT * FROM {tabela_escolhida}", conn)
        conn.close()

        # Estilo simples para a tabela
        estilo_tabela = '''
        <style>
            table {
                border-collapse: collapse;
                width: 90%;
                margin: auto;
                font-family: Arial, sans-serif;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #4CAF50;
                color: white;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            h2 {
                text-align: center;
                font-family: Arial, sans-serif;
                color: #2c3e50;
                margin-top: 30px;
            }
        </style>
        '''

        html_tabela = df.to_html(index=False, classes='tabela')
        return estilo_tabela + f"<h2>Dados da Tabela: {tabela_escolhida.capitalize()}</h2>" + html_tabela

    # Página com o formulário para escolher a tabela
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Ver Tabela</title>
    <style>
        /* Estilização geral */
        body {
            font-family: Arial, sans-serif;
            background: #f7f9fc;
            color: #333;
            display: flex;
            justify-content: center;
            padding: 40px;
        }

        /* Título */
        h2 {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 20px;
        }

        /* Formulário */
        form {
            background-color: #fff;
            padding: 25px 30px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            width: 350px;
        }

        /* Labels */
        form label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #34495e;
        }

        /* Selects */
        form select {
            width: 100%;
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid #ccc;
            border-radius: 6px;
            background-color: #f9f9f9;
            font-size: 14px;
        }

        /* Quebra de linha (corrige aparência dos <br>) */
        form br {
            display: none;
        }

        /* Botão de submit */
        form input[type="submit"] {
            background-color: #2980b9;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            width: 100%;
            font-size: 15px;
            transition: background-color 0.3s ease;
        }

        form input[type="submit"]:hover {
            background-color: #1c5980;
        }
    </style>
</head>
<body>
    <!-- Isso é um comentário em html-->
    <h2> Ver Tabela </h2>
    <form method="POST">
        <label for="tabela">Escolha a Tabela:</label>
        <select name="tabela">
            {% for opcao in opcoes %}
                <option value="{{opcao}}">{{opcao}}</option>
            {% endfor %}
        </select>
        <br><br>
        <input type="submit" value="--Ver Tabela--">
    </form>
</body>
</html>
''', opcoes=opcoes)



# o mundo fica aqui!!!!!
if __name__ == '__main__':
    criarBancoDados()
    app.run(debug=True)
