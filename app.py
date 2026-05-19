from flask import Flask, request, session, redirect, render_template_string
import sqlite3, hashlib, datetime

app = Flask(__name__)
app.secret_key = 'mentecheck2026'
DB = 'mentecheck.db'

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def hash_senha(s):
    return hashlib.sha256(s.encode()).hexdigest()

BASE = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MenteCheck</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:sans-serif;background:#f0f4f8;min-height:100vh}
.topo{background:#1a1a2e;color:white;padding:16px 20px;font-size:20px;font-weight:bold}
.topo span{color:#00b37e}
.card{background:white;border-radius:12px;padding:24px;margin:20px auto;max-width:480px;box-shadow:0 2px 12px rgba(0,0,0,0.1)}
h2{color:#1a1a2e;margin-bottom:16px;font-size:18px}
input{width:100%;padding:12px;border:1px solid #ddd;border-radius:8px;margin-bottom:12px;font-size:15px}
button{width:100%;padding:14px;background:#00b37e;color:white;border:none;border-radius:8px;font-size:16px;font-weight:bold;cursor:pointer}
button:hover{background:#009966}
.link{text-align:center;margin-top:14px;font-size:14px}
.link a{color:#00b37e;text-decoration:none}
.erro{background:#fee;color:#c00;padding:10px;border-radius:8px;margin-bottom:12px;font-size:14px}
.zona-v{background:#d4edda;color:#155724;padding:16px;border-radius:10px;text-align:center;font-size:18px;font-weight:bold}
.zona-a{background:#fff3cd;color:#856404;padding:16px;border-radius:10px;text-align:center;font-size:18px;font-weight:bold}
.zona-r{background:#f8d7da;color:#721c24;padding:16px;border-radius:10px;text-align:center;font-size:18px;font-weight:bold}
.pergunta{margin-bottom:18px}
.pergunta label{display:block;font-size:14px;color:#333;margin-bottom:8px;font-weight:500}
.opcoes{display:flex;gap:8px}
.opcoes input[type=radio]{display:none}
.opcoes label{flex:1;text-align:center;padding:10px 4px;border:2px solid #ddd;border-radius:8px;cursor:pointer;font-size:14px;font-weight:bold}
.opcoes input[type=radio]:checked+label{background:#00b37e;color:white;border-color:#00b37e}
.hist{padding:10px;border-bottom:1px solid #eee;display:flex;justify-content:space-between;align-items:center}
.badge{padding:4px 10px;border-radius:20px;font-size:12px;font-weight:bold}
.bv{background:#d4edda;color:#155724}
.ba{background:#fff3cd;color:#856404}
.br{background:#f8d7da;color:#721c24}
.sair{display:block;text-align:center;margin-top:12px;color:#999;font-size:13px;text-decoration:none}
</style></head>
<body>
<div class="topo">🧠 Mente<span>Check</span></div>
{% block body %}{% endblock %}
</body></html>'''

LOGIN = BASE.replace('{% block body %}{% endblock %}', '''
<div class="card">
<h2>Entrar na plataforma</h2>
{% if erro %}<div class="erro">{{ erro }}</div>{% endif %}
<form method="POST">
<input name="email" type="email" placeholder="Seu email" required>
<input name="senha" type="password" placeholder="Sua senha" required>
<button type="submit">Entrar</button>
</form>
<div class="link"><a href="/cadastro">Ainda não tem conta? Cadastre-se</a></div>
</div>''')

CADASTRO = BASE.replace('{% block body %}{% endblock %}', '''
<div class="card">
<h2>Criar conta</h2>
{% if erro %}<div class="erro">{{ erro }}</div>{% endif %}
<form method="POST">
<input name="nome" placeholder="Seu nome completo" required>
<input name="email" type="email" placeholder="Seu email" required>
<input name="senha" type="password" placeholder="Crie uma senha" required>
<button type="submit">Cadastrar</button>
</form>
<div class="link"><a href="/">Já tenho conta</a></div>
</div>''')

INICIO = BASE.replace('{% block body %}{% endblock %}', '''
<div class="card">
<h2>Olá, {{ nome }}! 👋</h2>
<p style="color:#666;margin-bottom:20px;font-size:14px">O que deseja fazer hoje?</p>
<a href="/qsm"><button>📋 Fazer Questionário</button></a>
<br><br>
<a href="/historico"><button style="background:#1a1a2e">📊 Ver meu Histórico</button></a>
<a href="/sair" class="sair">Sair da conta</a>
</div>''')

@app.route('/', methods=['GET','POST'])
def login():
    erro = None
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        conn = db()
        u = conn.execute('SELECT * FROM usuarios WHERE email=? AND senha=?',
                        (email, hash_senha(senha))).fetchone()
        conn.close()
        if u:
            session['id'] = u['id']
            session['nome'] = u['nome']
            return redirect('/inicio')
        erro = 'Email ou senha incorretos.'
    return render_template_string(LOGIN, erro=erro)

@app.route('/cadastro', methods=['GET','POST'])
def cadastro():
    erro = None
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        conn = db()
        try:
            conn.execute('INSERT INTO usuarios (nome,email,senha) VALUES (?,?,?)',
                        (nome, email, hash_senha(senha)))
            conn.commit()
            conn.close()
            return redirect('/')
        except:
            erro = 'Email já cadastrado.'
        conn.close()
    return render_template_string(CADASTRO, erro=erro)

@app.route('/inicio')
def inicio():
    if 'id' not in session:
        return redirect('/')
    return render_template_string(INICIO, nome=session['nome'])

@app.route('/qsm', methods=['GET','POST'])
def qsm():
    if 'id' not in session:
        return redirect('/')
    perguntas = [
        "O trabalho invade sua vida pessoal?",
        "Você consegue fazer pausas adequadas?",
        "O ritmo de trabalho é excessivo?",
        "Você sente conflitos de valores na equipe?",
        "Seu esforço é reconhecido?",
        "Você se sente desconectado do propósito?",
        "Sente exaustão antes de começar o dia?",
        "As decisões na empresa são justas?",
        "Você sente medo de cometer erros?",
        "O trabalho tem significado para você?"
    ]
    if request.method == 'POST':
        total = sum(float(request.form.get(f'p{i}', 0)) for i in range(10))
        if total <= 20:
            zona, cls, msg = 'VERDE', 'zona-v', '✅ Situação saudável. Continue assim!'
        elif total <= 35:
            zona, cls, msg = 'AMARELO', 'zona-a', '⚠️ Atenção. Sinais de desgaste.'
        else:
            zona, cls, msg = 'VERMELHO', 'zona-r', '🚨 Crítico. Busque apoio profissional.'
        conn = db()
        conn.execute('INSERT INTO qsm (usuario_id,data,pontuacao,zona) VALUES (?,?,?,?)',
                    (session['id'], datetime.datetime.now().isoformat(), total, zona))
        conn.commit()
        conn.close()
        resultado = f'''<div class="card">
<h2>Resultado</h2>
<div class="{cls}">{zona}<br><small style="font-size:14px;font-weight:normal">{msg}</small></div>
<p style="text-align:center;margin-top:16px;color:#666">Pontuação: {total:.0f}/50</p>
<br><a href="/inicio"><button>Voltar ao início</button></a></div>'''
        return render_template_string(BASE.replace('{% block body %}{% endblock %}', resultado))
    form = '<div class="card"><h2>📋 Questionário</h2><form method="POST">'
    for i, p in enumerate(perguntas):
        form += f'<div class="pergunta"><label>{i+1}. {p}</label><div class="opcoes">'
        for n in range(6):
            form += f'<input type="radio" name="p{i}" id="p{i}n{n}" value="{n}" required><label for="p{i}n{n}">{n}</label>'
        form += '</div></div>'
    form += '<button type="submit">Ver meu resultado</button></form></div>'
    return render_template_string(BASE.replace('{% block body %}{% endblock %}', form))

@app.route('/historico')
def historico():
    if 'id' not in session:
        return redirect('/')
    conn = db()
    rows = conn.execute('SELECT data,pontuacao,zona FROM qsm WHERE usuario_id=? ORDER BY data DESC LIMIT 10',
                       (session['id'],)).fetchall()
    conn.close()
    html = '<div class="card"><h2>📊 Meu Histórico</h2>'
    if not rows:
        html += '<p style="color:#999;text-align:center">Nenhum registro ainda.</p>'
    for r in rows:
        data = r['data'][:10]
        b = 'bv' if r['zona']=='VERDE' else 'ba' if r['zona']=='AMARELO' else 'br'
        html += f'<div class="hist"><span>{data} — {r["pontuacao"]:.0f} pts</span><span class="badge {b}">{r["zona"]}</span></div>'
    html += '<br><a href="/inicio"><button>Voltar</button></a></div>'
    return render_template_string(BASE.replace('{% block body %}{% endblock %}', html))

@app.route('/sair')
def sair():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    conn = sqlite3.connect(DB)
    conn.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT, email TEXT UNIQUE, senha TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS qsm (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER, data TEXT, pontuacao REAL, zona TEXT)''')
    conn.commit()
    conn.close()
    app.run(host='0.0.0.0', port=5000, debug=False)