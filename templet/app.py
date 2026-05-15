from flask import Flask, render_template, request, redirect, url_for
# Importa a biblioteca para trabalhar com bancos de dados SQLite
import sqlite3
# Importa a biblioteca para interagir com o sistema operacional (como verificar/criar arquivos)
import os
# Importa a biblioteca 'requests' para fazer requisições HTTP (essencial para consumir APIs externas)
import requests 

# Cria uma instância da aplicação Flask. O argumento '__name__' ajuda o Flask a encontrar 
# recursos como templates e arquivos estáticos.
app = Flask(__name__)

# Nome do arquivo do banco de dados SQLite
DATABASE_NAME = 'notas.db'

# Função para criar o banco de dados e a tabela, caso não existam
def create_database():
    # Verifica se o arquivo do banco de dados não existe
    if not os.path.exists(DATABASE_NAME):
        # Conecta-se ao banco de dados (se não existir, ele é criado)
        conn = sqlite3.connect(DATABASE_NAME)
        # Executa o comando SQL para criar a tabela 'notas'
        # Adicionamos a coluna 'uf' (Unidade Federativa) na tabela para armazenar a sigla do estado
        conn.execute('''CREATE TABLE IF NOT EXISTS notas (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            aluno TEXT NOT NULL,
                            disciplina TEXT NOT NULL,
                            nota TEXT NOT NULL,
                            uf TEXT NOT NULL -- Nova coluna para a Unidade Federativa
                        );''')
        # Confirma as alterações no banco de dados
        conn.commit()
        # Fecha a conexão com o banco de dados
        conn.close()

# Função para conectar ao banco de dados SQLite
def get_db_connection():
    # Conecta-se ao banco de dados
    conn = sqlite3.connect(DATABASE_NAME)
    # Define o 'row_factory' para 'sqlite3.Row'. 
    # Isso permite que os resultados das consultas sejam 
    # acessados como dicionários (ex: nota['aluno'])
    conn.row_factory = sqlite3.Row
    return conn

# Rota principal ('/') que exibe a lista de notas
@app.route('/')
def index():
    # Obtém a conexão com o banco de dados
    conn = get_db_connection()
    # Executa uma consulta para selecionar todos os registros da tabela 'notas'
    notas = conn.execute('SELECT * FROM notas').fetchall()
    # Fecha a conexão
    conn.close()
    # Renderiza o template 'index.html', passando a lista de notas para ser exibida
    return render_template('index.html', notas=notas)

# Rota para adicionar uma nova nota. Aceita requisições GET e POST
@app.route('/adicionar', methods=('GET', 'POST'))
def adicionar():
    # Verifica se a requisição foi do tipo POST (ou seja, o formulário foi submetido)
    if request.method == 'POST':
        # Captura os dados enviados pelo formulário HTML (os nomes são os atributos 'name' dos campos)
        aluno = request.form['aluno']
        disciplina = request.form['disciplina']
        nota = request.form['nota']
        # Captura a UF do formulário e converte para maiúsculas (ex: 'sp' -> 'SP')
        uf = request.form['uf'].upper() 

        # Obtém a conexão com o banco de dados
        conn = get_db_connection()
        # Executa o comando SQL para inserir um novo registro, incluindo a 'uf'
        conn.execute('INSERT INTO notas (aluno, disciplina, nota, uf) VALUES (?, ?, ?, ?)',
                     (aluno, disciplina, nota, uf))
        # Confirma a inserção
        conn.commit()
        # Fecha a conexão
        conn.close()
        # Redireciona o usuário de volta para a rota principal ('/')
        return redirect(url_for('index'))

    # Se a requisição for GET, renderiza o template do formulário de adição
    return render_template('adicionar.html')

# --- NOVA ROTA PARA DETALHES DO ALUNO E CONSUMO DA API ---
# A rota recebe o ID do aluno como parte da URL (ex: /aluno/1)
@app.route('/aluno/<int:id>')
def detalhes_aluno(id):
    # 1. Busca os dados do aluno no nosso banco de dados local
    conn = get_db_connection()
    # Executa a consulta para encontrar a nota com o ID específico
    aluno_local = conn.execute('SELECT * FROM notas WHERE id = ?', (id,)).fetchone()
    conn.close()

    # Verifica se o aluno foi encontrado
    if aluno_local is None:
        # Retorna uma mensagem de erro com código HTTP 404 (Não Encontrado)
        return "Aluno não encontrado!", 404

    # 2. Usa a UF do aluno para chamar a API do IBGE
    uf_aluno = aluno_local['uf'] # Pega a sigla da UF do registro local
    
    # URL da API do IBGE para buscar dados de um estado pela sua sigla
    # f-string: interpola a variável {uf_aluno} diretamente na string da URL
    url_api_ibge = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf_aluno}"
    
    dados_estado = None # Inicializa a variável para armazenar a resposta da API
    
    try:
        # Faz a requisição GET para a API usando a biblioteca 'requests'
        response = requests.get(url_api_ibge)
        
        # Verifica se o status HTTP da resposta é 200 (OK)
        if response.status_code == 200:
            # Converte o conteúdo JSON da resposta para um dicionário ou lista Python
            dados_estado = response.json()
        else:
             # Se o status não for 200 (ex: 404 para UF inexistente), salva uma mensagem de erro
            dados_estado = {"erro": f"API retornou status: {response.status_code}"}
            
    # Captura exceções que podem ocorrer durante a requisição (ex: falha de rede, URL errada)
    except requests.exceptions.RequestException as e:
        # Em caso de erro de conexão/requisição, guarda a mensagem de erro
        dados_estado = {"erro": f"Erro ao conectar na API: {str(e)}"}

    # 3. Renderiza uma nova página ('detalhes.html'), passando:
    # - 'aluno': os dados do registro local
    # - 'estado': os dados retornados pela API do IBGE (ou a mensagem de erro)
    return render_template('detalhes.html', aluno=aluno_local, estado=dados_estado)


# Bloco principal de execução do script
if __name__ == '__main__':
    # Esta parte é importante para garantir que, ao rodar, você crie a nova tabela
    # Se o banco de dados antigo existir, ele é apagado para criar um novo com a coluna 'uf'.
    if os.path.exists(DATABASE_NAME):
        print(f"Apagando o banco de dados antigo ({DATABASE_NAME}) para recriar com a nova coluna 'uf'.")
        os.remove(DATABASE_NAME)
        
    # Chama a função para criar o banco de dados e a tabela
    create_database()
    # Inicia o servidor web Flask
    # debug=True permite recarregamento automático do código e exibe mensagens de erro detalhadas
    print("Iniciando aplicação Flask...")
    app.run(debug=True)