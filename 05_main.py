from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import sqlite3
import os
import plotly.graph_objs as go
from dash import Dash, html, dcc
import numpy as  np
import config #Nosso arquivo config.py
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)
pasta = config.FOLDER
caminhoBd = config.DB_PATH
rotas = config.ROTAS
vazio = 0

def init_db():
    with sqlite3.connect (f'{pasta}{caminhoBd}') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inadimplencia(
                mes TEXT PRIMARY KEY,
                inadimplencia REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS SELIC(
                mes TEXT PRIMARY KEY,
                Selic_diaria REAL
            )
        ''')
        conn.commit

@app.route(rotas[0])
def index(): 
    return render_template_string(f'''
        <h1> upload de dados economicos </h1>
        <form action="{rotas[1]}"method="POST" enctype="multipart/form-data">
                                  
            <label for="campo_inadimplencia"> Arquivo de Inadimplencia (CSV): </label>
            <input name="campo_inadimplencia" type="file" required> <br>
                                  
            <label for="campo_selic"> Arquivo de Taxa Selic (CSV): </label>
            <input name="campo_selic" type="file" required><br>

            <input type="submit" value="Fazer upload">  <br>               
            </form>
            <br><br>
            <a href="{rotas[2]}">Consultar dados armazanados </a> <br> 
            <a href="{rotas[3]}"> Visualizar Graficos </a> <br> 
            <a href="{rotas[4]}"> Editar Inadimplencia </a> <br> 
            <a href="{rotas[5]}"> Analisar Correlação </a> <br> 

    ''')
@app.route(rotas[1], methods=['POST', 'GET'])
def upload():
    inad_file = request.files.get('campo_inadimplencia')
    selic_file = request.files.get('campo_selic')
    if not inad_file or not selic_file:
        return jsonify({"Erro":"Ambos arquivos devem serenviados"}), 406
    
    inad_df = pd.read_csv(
        inad_file,
        sep = ';',
        names = ['data','inadimplencia' ],
        header= 0
    selic_file_df = pd.read_csv
        selic_file_file,
        sep = ';',
        names = ['data','selic_diaria' ],
        header= 0
    )
    inad_df['data'] = pd.to_datetime(
        inad_df['data']
        format='%d/%m/%Y'
    )
    selic_df['data'] = pd.to_datetime(
        selic_df['data']
        format='%d/%m/%Y'
    )
    inad_df['mes'] = inad_df['data'].dt.to_period('M').astype(str)
    selic_df['mes'] = selic_df['data'].dt.to_period('M').astype(str) 
    inad_df['mes'] = inad_df[['mes', 'inadimplencia']].drop_duplicates()
    selic_mesal = selic_df.groupby('mes')['selic_diaria'].mean().reset_index()

    with sqlite3.connect(f'{pasta}{caminhoBd}') as conn:
        inad_df.to_sql(
            'inadimplencia',
            if_exists = 'replace',
            index= False
        )
        selic_df.to_sql(
            'selic',
            if_exists = 'replace',
            index= False
        )
    return jsonify({"Mensagem":"Dados cadastrados com sucesso!"}),200
@app.route(rotas[2], methods=['POST', 'GET'])
def consultar():

    return render_template_string(f'''
        <h1> Consulta de Tabelas </h1>
        <form method="POST">
            <label for="campo_tabela"> Escolha uma tabela: </lab"el>
            <selec name="campo_tabela">
                <option value="inadimplencia"> Inadimplência </option>
                <option value="selic"> Taxa Selic </option>
            <select>
            <input type="submit" value="Consultar">
        </form>
        <br>
        <a href="{rotas[0]}"> Voltar </a>
                
                                  



''')




if __name__ == "__main__":
    init_db()
    app.run(
        debug=config.FLASK_DEBUG,
        host = config.FLASK_HOST,
        port = config.FLASK_PORT
    )
