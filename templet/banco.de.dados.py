import sqlite3

def criar_banco():
    conn = sqlite3.connect('alunos.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            nota REAL NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

criar_banco()
