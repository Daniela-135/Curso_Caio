from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import sqlite3
import os
import plotly.graph_objs as go
from dash import Dash, html, dcc
import dash
import numpy as np
import config
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
#pip install scikit-learn
#Para lista todas as libs instaladas no python use pip list 

app = Flask(__name__)
pasta = config.FOLDER
caminhoBd = config.DB_PATH
rotas = config.ROTAS
vazio = 0

def init_db():
    with sqlite3.connect (f'{pasta}{caminhoBd}') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inadimplencia (
                mes TEXT PRIMARY KEY,
                inadimplencia REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS selic (
                mes TEXT PRIMARY KEY,
                selic_diaria REAL
            )
        ''')
        conn.commit()
vazio = 0

@app.route(rotas[0])
def index():
    return render_template_string(f'''
        <h1>Upload de dados Economicos</h1>
        <form action="{rotas[1]}" method="POST" enctype="multipart/form-data">
            <label for="campo_inadimplencia">Arquivo de Inadimplencia (CSV)</label>
            <input name="campo_inadimplencia" type="file" required>
            <label for="campo_selic">Arquivo da Taxa Selic (CSV)</label>
            <input name="campo_selic" type="file" required>
            <input type="submit" value="Fazer Upload">
        </form>
        <br><br>
        <hr>
        <a href="{rotas[2]}">Consultar dados Armazenados</a><br>
        <a href="{rotas[3]}">Visualizar Graficos</a><br>
        <a href="{rotas[4]}">Editar dados de Inadimplencia</a><br>
        <a href="{rotas[5]}">Analisar Correlação </a><br>
        <a href="{rotas[6]}">Observabilidade em 3D</a><br>
        <a href="{rotas[7]}">Editar Selic</a><br>
    ''')

@app.route(rotas[1], methods=['POST','GET'])
def upload():
    inad_file = request.files.get('campo_inadimplencia')
    selic_file = request.files.get('campo_selic')

    if not inad_file or not selic_file:
        return jsonify({"Erro":"Ambos os arquivos devem ser enviados!"}),406
    
    inad_df = pd.read_csv(
        inad_file,
        sep = ';',
        names = ['data','inadimplencia'],
        header = 0
    )
    selic_df = pd.read_csv(
        selic_file,
        sep = ';',
        names = ['data','selic_diaria'],
        header = 0
    )

    inad_df['data'] = pd.to_datetime(
        inad_df['data'], 
        format = "%d/%m/%Y"
    )
    selic_df['data'] = pd.to_datetime(
          selic_df['data'], 
          format="%d/%m/%Y"
        )
    
    inad_df['mes'] = inad_df['data'].dt.to_period('M').astype(str)
    selic_df['mes'] = selic_df['data'].dt.to_period('M').astype(str)

    inad_mensal = inad_df[["mes","inadimplencia"]].drop_duplicates()
    selic_mensal = selic_df.groupby('mes')['selic_diaria'].mean().reset_index()

    with sqlite3.connect(caminhoBd) as conn:
        inad_df.to_sql(
            'inadimplencia',
            conn,
            if_exists = 'replace',
            index = False
        )
        selic_df.to_sql(
            'selic',
            conn,
            if_exists = 'replace',
            index = False
        )
    return jsonify({"Mensagem":"Dados cadastrados com sucesso!"})

@app.route(rotas[2], methods=['GET','POST'])
def consultar():

    if request.method == "POST":
        tabela = request.form.get("campo_tabela")
        if tabela not in ["inadimplencia","selic"]:
            return jsonify({"Erro":"Tabela Invalida"}),400
        with sqlite3.connect(caminhoBd) as conn:
            df = pd.read_sql_query(f"SELECT * FROM {tabela}",conn)
        return df.to_html(index=False)
    
    return render_template_string(f'''
        <h1> Consulta de Tabelas </h1>
        <form method="POST">
            <label for="campo_tabela"> Escolha uma tabela: </label>
            <select name="campo_tabela">
                <option value="inadimplencia"> Inadimplencia </option>
                <option value="selic"> Taxa Selic </option>
            </select>
            <input type="submit" value="Consultar">
        </form>
        <br><a href="{rotas[0]}"> Voltar </a>
    ''')
@app.route(rotas[4], methods=['POST','GET'])
def editar_inadimplencia():
    if request.method == "POST":
        mes = request.form.get('campo_mes')
        novo_valor = request.form.get('campo_valor')
        try:
            novo_valor = float(novo_valor)
        except:
            return jsonify({"Erro:":"Valor invalido"}),418
        with sqlite3.connect (f'{pasta}{caminhoBd}') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                    UPDATE inadimplencia 
                    SET inadimplencia = ? 
                    WHERE mes = ?
                ''',(novo_valor, mes))
            conn.commit()
        return jsonify({"Mensagem":f"Valor atualozado para o mês {mes}"})

    return render_template_string(f'''
        <h1> Editar Inadimplencia </h1>
        <form method="POST" action="{rotas[4]}">
            <label for="campo_mes"> Mês (AAAA-MM)</label>
            <input type="text" name="campo_mes"><br>
                                  
            <label for="campo_valor"> Novo valor de Inadimplencia </label>
            <input type="text" name="campo_valor"><br>
                                  
            <input type="submit" value="Salvar">
        </form>
        <br>
        <a href="{rotas[0]}">Voltar</a>                         
    ''')
@app.route(rotas[5])
def correlação():
     with sqlite3.connect (f'{pasta}{caminhoBd}') as conn:
        inad_df = pd.read_sql_query("SELECT * FROM inadimplencia", conn)
        selic_df = pd.read_sql_query("SELECT * FROM selic", conn)

    # realiza uma junção entre dois dataframes usando a coluna de mes como chave de junção
        merged = pd.merge(inad_df, selic_df, on='mes')

    #calcula o coeficiente da correlação de pearson entre as duas variaveis
        correl = merged['inadimplencia'].corr(merged['selic_diaria'])
    
    #registra as variaveis para regressão linear onde X é a variavel independente e Y é a variavel dependente
        x = merged['selic_diaria']
        Y = merged['inadimplencia']
        m, b = np.polyfit(x, y, 1) # calcula o coeficiente da reta de regressão linear onde M é a inclinação e B a intersecção

    # Criar grafico
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x = x,
            y = y,
            mode = 'makers',
            name = 'Inadimplencia x Selic',
            marker = dict(
                color = 'rgba(0, 123, 255,0.8)',
                size = 12,
                line = dict(width = 2, color = 'white'),
                symbol = 'circle'
            ),
            hovertemplate = 'selic: %{x:.2f}% <br> Inadimplencia: %{y:.2f}% <extra> <entra>'
 
        ))
        fig.add_trace(go.Scatter(
        
            x = x,# mesmo eixo dos dados
            y = m * x + b, # a equação da linha de tendencia
            mode = 'lines',
            name = 'Linha de Tendência',
            line = dict(
            color = 'rgba(255, 53, 69, 1)',
            width = 4,
            dash = 'dot'
        )
        ))
        fig.update_layout(
        title = {
            'text':f'<b>Correlação entre Selic e Inadimplencia</b><br><span style="font-size:16px;">Coeficiente de Correlação: {correl:.2f}</span>',
            'y':0.95, # posição vertical do titulo (95% da altura do grafico)
            'x':0.5, # posição horizontal do titulo (50% da altura do grafico)
            'xanchor':'center', #alinha o titulo horizontalmente ao centro
            'yanchor':'top' # alinha o titulo verticalmente ao topo
        },
        xaxis_title = dict(
            text = 'SELIC Média Mensal (%)', #titulo do eixo x
            font = dict(
                size = 18,
                family = 'Arial', 
                color = 'gray'
            )
        ),
                xaxis_title = dict(
            text = 'SELIC Média Mensal (%)', #titulo do eixo x
            font = dict(
                size = 18,
                family = 'Arial', 
                color = 'gray'
            )
        ),
        yaxis_title = dict(
            text = 'Inadimplencia (%)', #titulo do eixo y
            font = dict(
                size = 18,
                family = 'Arial', 
                color = 'gray'
            )
        ),
        xaxis = dict(
            tickfont = dict(
                size = 14,
                family = 'Arial',
                color = 'black'
            ),
            gridcolor = 'lightgray' # cor das linhas de grade
        ),
        yaxis = dict(
            tickfont = dict(
                size = 14,
                family = 'Arial',
                color = 'black'
            ),
            gridcolor = 'lightgray'
        ),
        font = dict(
            family = 'Arial',
            size = 14,
            color = 'black'
        ),
        legend = dict(
            orientation = 'h',  #legenda horizontal
            yanchor = 'bottom', #alinhamento vertical da legenda
            y = 1.05,           #posição da legenda pouco acima do grafico
            xanchor = 'center', #alinhamento horizontal da legenda ao centro
            x = 0.5,            #posição horizontal da legenda
            bgcolor = 'rgba(0,0,0,0)',  #cor de fundo da legenda
            borderwidth = 0     #largura da borda da legenda
        ),
        margin = dict(
            l = 60,
            r = 60,
            t = 120,
            b = 60
        ),
        plot_bgcolor = "#7e1f4c", #cor de fundo do grafico
        paper_bgcolor = 'white' #cor de fundo da area do grafico
    )





        ))







if __name__ == "__main__":
    init_db()
    app.run(
        debug=config.FLASK_DEBUG,
        host = config.FLASK_HOST,
        port = config.FLASK_PORT
    )
