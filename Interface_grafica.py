import sqlite3
import tkinter as tk
from tkinter import messagebox

# Função para cadastrar aluno
def cadastrar_aluno():
    nome = entry_nome.get()
    nota = entry_nota.get()

    if nome and nota:
        try:
            conn = sqlite3.connect('alunos.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO alunos (nome, nota) VALUES (?, ?)', (nome, float(nota)))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", "Aluno cadastrado com sucesso!")
            entry_nome.delete(0, tk.END)
            entry_nota.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar aluno: {e}")
    else:
        messagebox.showwarning("Atenção", "Por favor, preencha todos os campos!")

# Função para consultar notas
def consultar_notas():
    conn = sqlite3.connect('alunos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM alunos')
    alunos = cursor.fetchall()
    conn.close()

    result_window = tk.Toplevel(root)
    result_window.title("Consulta de Notas")
    result_window.geometry("400x300")  # Definindo um tamanho maior para a janela de consulta
    
    for aluno in alunos:
        label = tk.Label(result_window, text=f"ID: {aluno[0]} | Nome: {aluno[1]} | Nota: {aluno[2]}")
        label.pack(pady=2)

# Criação da janela principal
root = tk.Tk()
root.title("Cadastro de Notas de Alunos")
root.geometry("400x300")  # Aumentando o tamanho da janela principal

# Criação dos campos de entrada
label_nome = tk.Label(root, text="Nome do Aluno:", font=('Arial', 12))
label_nome.pack(pady=10)
entry_nome = tk.Entry(root, font=('Arial', 12))
entry_nome.pack(pady=5)

label_nota = tk.Label(root, text="Nota do Aluno:", font=('Arial', 12))
label_nota.pack(pady=10)
entry_nota = tk.Entry(root, font=('Arial', 12))
entry_nota.pack(pady=5)

btn_cadastrar = tk.Button(root, text="Cadastrar", command=cadastrar_aluno, font=('Arial', 12))
btn_cadastrar.pack(pady=15)

btn_consultar = tk.Button(root, text="Consultar Notas", command=consultar_notas, font=('Arial', 12))
btn_consultar.pack(pady=10)

root.mainloop()
