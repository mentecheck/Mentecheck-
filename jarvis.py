import time, random
from datetime import datetime

saldo_usd = 35000.0
saldo_btc = 0.0
preco_entrada = None
stop_loss = None
trades = 0

def linha():
    print("-" * 45)

def status(preco):
    total = saldo_usd + saldo_btc * preco
    print(f"  USD : ${saldo_usd:,.2f}")
    print(f"  BTC : {saldo_btc:.6f}")
    print(f"  Total: ${total:,.2f}")

def comprar(qtd, preco):
    global saldo_usd, saldo_btc, preco_entrada, stop_loss, trades
    custo = qtd * preco
    taxa = custo * 0.0018
    if custo + taxa > saldo_usd:
        print("  SALDO INSUFICIENTE")
        return
    saldo_usd -= (custo + taxa)
    saldo_btc += qtd
    preco_entrada = preco
    stop_loss = preco * 0.92
    trades += 1
    print(f"  COMPRA {qtd:.6f} BTC @ ${preco:,.2f}")

def vender(qtd, preco, motivo="VENDA"):
    global saldo_usd, saldo_btc, preco_entrada, stop_loss, trades
    if qtd > saldo_btc:
        return
    receita = qtd * preco
    taxa = receita * 0.0018
    saldo_usd += (receita - taxa)
    saldo_btc -= qtd
    preco_entrada = None
    stop_loss = None
    trades += 1
    print(f"  {motivo} {qtd:.6f} BTC @ ${preco:,.2f}")

print("JARVIS TERMINAL - Iniciando...")
print("Pressione Ctrl+C para parar\n")

ciclo = 0
while True:
    try:
        ciclo += 1
        preco = random.uniform(58500, 64500)
        rsi = random.uniform(18, 82)
        linha()
        print(f"Ciclo #{ciclo} | {datetime.now().strftime('%H:%M:%S')}")
        print(f"  BTC: ${preco:,.2f} | RSI: {rsi:.1f}")
        status(preco)
        if stop_loss and saldo_btc > 0.001 and preco <= stop_loss:
            print("  STOP LOSS ATIVADO!")
            vender(saldo_btc, preco, "STOP LOSS")
        elif rsi < 32 and saldo_usd > 800:
            qtd = min(0.4, (saldo_usd * 0.018) / preco)
            comprar(qtd, preco)
        elif rsi > 68 and saldo_btc > 0.005:
            vender(saldo_btc * 0.55, preco)
        else:
            print("  Aguardando sinal...")
        print(f"  Trades: {trades}")
        time.sleep(4)
    except KeyboardInterrupt:
        linha()
        print("Jarvis encerrado. Trades:", trades)
        break
