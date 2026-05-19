import sqlite3
import hashlib
import datetime

DB = 'mentecheck.db'

def criar_banco():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS qsm (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        data TEXT,
        pontuacao REAL,
        zona TEXT
    )''')
    conn.commit()
    conn.close()

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def cadastrar(nome, email, senha):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO usuarios (nome, email, senha) VALUES (?,?,?)',
                  (nome, email, hash_senha(senha)))
        conn.commit()
        print(f"\n✅ Usuário {nome} cadastrado com sucesso!")
    except:
        print("\n❌ Email já cadastrado.")
    conn.close()

def login(email, senha):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT id, nome FROM usuarios WHERE email=? AND senha=?',
              (email, hash_senha(senha)))
    u = c.fetchone()
    conn.close()
    return u

def fazer_qsm(usuario_id):
    print("\n📋 QUESTIONÁRIO DE SAÚDE MENTAL")
    print("Responda de 0 a 5 (0=nunca, 5=sempre)\n")
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
    total = 0
    for i, p in enumerate(perguntas):
        while True:
            try:
                r = float(input(f"{i+1}. {p} [0-5]: "))
                if 0 <= r <= 5:
                    total += r
                    break
                else:
                    print("   Digite um número entre 0 e 5")
            except:
                print("   Digite um número válido")

    if total <= 20:
        zona = "VERDE"
        msg = "✅ Situação saudável. Continue assim!"
    elif total <= 35:
        zona = "AMARELO"
        msg = "⚠️  Atenção. Sinais de desgaste. Converse com seu gestor."
    else:
        zona = "VERMELHO"
        msg = "🚨 CRÍTICO. Procure apoio profissional imediatamente."

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('INSERT INTO qsm (usuario_id, data, pontuacao, zona) VALUES (?,?,?,?)',
              (usuario_id, datetime.datetime.now().isoformat(), total, zona))
    conn.commit()
    conn.close()

    print(f"\n{'='*40}")
    print(f"Pontuação: {total}/50")
    print(f"Zona: {zona}")
    print(msg)
    print(f"{'='*40}")

def ver_historico(usuario_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT data, pontuacao, zona FROM qsm WHERE usuario_id=? ORDER BY data DESC LIMIT 5',
              (usuario_id,))
    rows = c.fetchall()
    conn.close()
    if not rows:
        print("\nNenhum registro ainda.")
        return
    print("\n📊 SEU HISTÓRICO:")
    for r in rows:
        data = r[0][:10]
        icone = "✅" if r[2]=="VERDE" else "⚠️" if r[2]=="AMARELO" else "🚨"
        print(f"  {data} | {r[1]:.0f} pts | {icone} {r[2]}")

def menu_logado(usuario_id, nome):
    while True:
        print(f"\n🧠 MENTECHECK — Olá, {nome}")
        print("1. Fazer questionário")
        print("2. Ver meu histórico")
        print("3. Sair")
        op = input("Escolha: ")
        if op == "1":
            fazer_qsm(usuario_id)
        elif op == "2":
            ver_historico(usuario_id)
        elif op == "3":
            break

def main():
    criar_banco()
    print("\n" + "="*40)
    print("   🧠 MENTECHECK — Saúde Mental")
    print("="*40)
    while True:
        print("\n1. Entrar")
        print("2. Cadastrar")
        print("3. Sair")
        op = input("Escolha: ")
        if op == "1":
            email = input("Email: ")
            senha = input("Senha: ")
            u = login(email, senha)
            if u:
                print(f"\n✅ Bem-vindo, {u[1]}!")
                menu_logado(u[0], u[1])
            else:
                print("\n❌ Email ou senha incorretos.")
        elif op == "2":
            nome = input("Seu nome: ")
            email = input("Email: ")
            senha = input("Senha: ")
            cadastrar(nome, email, senha)
        elif op == "3":
            print("\n👋 Até logo!")
            break

main()