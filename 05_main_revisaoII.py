from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import sqlite3
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import config

app = Flask(__name__)
pasta = config.FOLDER
caminhoBd = os.path.join(pasta, config.DB_PATH)
rotas = config.ROTAS

def init_db():
    with sqlite3.connect(caminhoBd) as conn:
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

@app.route(rotas[1], methods=['POST','GET'])
def upload():
    inad_file = request.files.get('campo_inadimplencia')
    selic_file = request.files.get('campo_selic')

    if not inad_file or not selic_file:
        return jsonify({"Erro":"Ambos os arquivos devem ser enviados!"}), 406

    inad_df = pd.read_csv(inad_file, sep=';', names=['data', 'inadimplencia'], header=0)
    selic_df = pd.read_csv(selic_file, sep=';', names=['data', 'selic_diaria'], header=0)

    inad_df['data'] = pd.to_datetime(inad_df['data'], format="%d/%m/%Y")
    selic_df['data'] = pd.to_datetime(selic_df['data'], format="%d/%m/%Y")

    inad_df['mes'] = inad_df['data'].dt.to_period('M').astype(str)
    selic_df['mes'] = selic_df['data'].dt.to_period('M').astype(str)

    inad_mensal = inad_df[["mes", "inadimplencia"]].drop_duplicates()
    selic_mensal = selic_df.groupby('mes')['selic_diaria'].mean().reset_index()

    with sqlite3.connect(caminhoBd) as conn:
        inad_mensal.to_sql('inadimplencia', conn, if_exists='replace', index=False)
        selic_mensal.to_sql('selic', conn, if_exists='replace', index=False)

    return jsonify({"Mensagem": "Dados cadastrados com sucesso!"})

@app.route(rotas[4], methods=['POST','GET'])
def editar_inadimplencia():
    if request.method == "POST":
        mes = request.form.get('campo_mes')
        novo_valor = request.form.get('campo_valor')
        try:
            novo_valor = float(novo_valor)
        except ValueError:
            return jsonify({"Erro": "Valor inválido, insira um número."}), 400
        with sqlite3.connect(caminhoBd) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE inadimplencia 
                SET inadimplencia = ? 
                WHERE mes = ?
            ''', (novo_valor, mes))
            conn.commit()
        return jsonify({"Mensagem": f"Valor atualizado para o mês {mes}"})

    # Formulário
    return render_template_string(f'''
        <h1> Editar Inadimplência </h1>
        <form method="POST" action="{rotas[4]}">
            <label for="campo_mes"> Mês (AAAA-MM)</label>
            <input type="text" name="campo_mes" required><br>
            <label for="campo_valor"> Novo valor de Inadimplência </label>
            <input type="text" name="campo_valor" required><br>
            <input type="submit" value="Salvar">
        </form>
        <br><a href="{rotas[0]}">Voltar</a>
    ''')
