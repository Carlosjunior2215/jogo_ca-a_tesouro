import sqlite3
import pandas as pd

con = sqlite3.connect('jogo.db')

print("\n=== MOVIMENTOS ===")
df_mov = pd.read_sql_query("SELECT * FROM movimentos", con)
print(df_mov)

print("\n=== PARTIDAS ===")
df_partidas = pd.read_sql_query("SELECT * FROM partidas", con)
print(df_partidas)

con.close()
