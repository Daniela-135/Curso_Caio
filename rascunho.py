# Conexão com o banco
conn = sqlite3.connect(pasta + bancoDados)
cursor = conn.cursor()

# Cria tabela se não existir
cursor.execute('''
CREATE TABLE IF NOT EXISTS filmes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT,
    direcao TEXT,
    nota REAL,
    link TEXT UNIQUE,
    ano TEXT,
    categoria TEXT
)
''')

# Insere os dados no banco
for filme in filmes:
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO filmes (titulo, direcao, nota, link, ano, categoria)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            filme["Titulo"],
            filme["Direção"],
            float(filme["Nota"]),
            filme["Link"],
            filme["Ano"],
            filme["Categoria"]
        ))
    except Exception as e:
        print(f"Erro ao inserir no banco o filme {filme['Titulo']}: {e}")

# Salva e fecha a conexão
conn.commit()
conn.close()
print("Dados salvos no banco de dados SQLite com sucesso.")