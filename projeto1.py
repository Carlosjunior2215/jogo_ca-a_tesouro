import numpy as np
import sqlite3
import time
from datetime import datetime

# --- BANCO DE DADOS ---
con = sqlite3.connect('jogo.db')
cur = con.cursor()

# Criação das tabelas
cur.execute('''
CREATE TABLE IF NOT EXISTS movimentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    direcao TEXT,
    posicao_anterior TEXT,
    posicao_nova TEXT,
    timestamp TEXT
)
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS partidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pontuacao INTEGER,
    tempo_total REAL,
    status TEXT,
    data TEXT
)
''')
con.commit()

# --- CONFIGURAÇÃO DO JOGO ---
tamanho = 5
mapa = np.random.randint(1, 10, size=(tamanho, tamanho))
obstaculos = 5

# Adiciona obstáculos
for _ in range(obstaculos):
    while True:
        l, c = np.random.randint(0, tamanho, size=2)
        if (l, c) != (0, 0):
            mapa[l, c] = -2
            break

# Define posição do tesouro
while True:
    tesouro_linha, tesouro_coluna = np.random.randint(0, tamanho, size=2)
    if mapa[tesouro_linha, tesouro_coluna] != -2 and (tesouro_linha, tesouro_coluna) != (0, 0):
        break

posicao_jogador = (0, 0)
pontuacao = 0
vidas = 5
inicio = time.time()

# --- FUNÇÕES ---
def distancia_manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def mostrar_mapa(mapa, posicao_jogador, mostrar_tesouro=False):
    mapa_visual = mapa.copy()
    linha, coluna = posicao_jogador
    mapa_visual[linha, coluna] = -1

    mapa_str = np.char.mod('%2s', mapa_visual.astype(str))
    for i in range(tamanho):
        for j in range(tamanho):
            if mapa[i, j] == -2:
                mapa_str[i, j] = 'X'
    mapa_str[linha, coluna] = 'P'

    if mostrar_tesouro:
        mapa_str[tesouro_linha, tesouro_coluna] = '?'

    print("\nMapa Atual:")
    for linha_str in mapa_str:
        print(" ".join(linha_str))

# --- LOOP PRINCIPAL ---
while vidas > 0:
    mostrar_mapa(mapa, posicao_jogador)
    print(f"Vidas: {vidas} | Pontuação: {pontuacao}")

    dist = distancia_manhattan(posicao_jogador, (tesouro_linha, tesouro_coluna))
    if dist == 0:
        print("\n===== Tesouro Encontrado! =====")
        status_final = 'vitória'
        break
    elif dist <= 2:
        print("🔥 Quente!")
    elif dist <= 4:
        print("🌤️ Morno...")
    else:
        print("❄️ Frio...")

    direcao = input("Mover para (cima, baixo, esquerda, direita ou c/b/e/d): ").strip().lower()

    movimentos = {
        "cima": (-1, 0),
        "baixo": (1, 0),
        "esquerda": (0, -1),
        "direita": (0, 1),
        "c": (-1, 0),
        "b": (1, 0),
        "e": (0, -1),
        "d": (0, 1),
    }

    if direcao not in movimentos:
        print("❌ Direção inválida. Perdeu 1 vida.")
        vidas -= 1
        continue

    nova_pos = (
        posicao_jogador[0] + movimentos[direcao][0],
        posicao_jogador[1] + movimentos[direcao][1]
    )

    if not (0 <= nova_pos[0] < tamanho and 0 <= nova_pos[1] < tamanho):
        print("❌ Fora dos limites! Perdeu 1 vida.")
        vidas -= 1
        continue

    if mapa[nova_pos[0], nova_pos[1]] == -2:
        print("💥 Obstáculo! Perdeu 1 vida.")
        vidas -= 1
        continue

    # Salva movimento no banco
    cur.execute('''
        INSERT INTO movimentos (direcao, posicao_anterior, posicao_nova, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (
        direcao,
        str(posicao_jogador),
        str(nova_pos),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    con.commit()

    posicao_jogador = nova_pos
    pontuacao += 1

else:
    print("\n💀 Suas vidas acabaram.")
    status_final = 'derrota'

# --- FIM DO JOGO ---
fim = time.time()
tempo_total = round(fim - inicio, 2)

cur.execute('''
    INSERT INTO partidas (pontuacao, tempo_total, status, data)
    VALUES (?, ?, ?, ?)
''', (
    pontuacao,
    tempo_total,
    status_final,
    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
))
con.commit()

print(f"\n⏱ Tempo total: {tempo_total}s")
print(f"✅ Pontuação final: {pontuacao}")
print(f"📍 O tesouro estava em: ({tesouro_linha}, {tesouro_coluna})")

mostrar_mapa(mapa, posicao_jogador, mostrar_tesouro=True)

# Fecha banco
con.close()
