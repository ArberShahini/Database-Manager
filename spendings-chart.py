import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import env

engine = create_engine(env.DB_URL)

query = """
SELECT
    klient.emer AS emri_klientit,
    SUM(transaksion.vlera) AS shpenzimet_totale
FROM klient
JOIN transaksion ON klient.id = transaksion.id_klienti
GROUP BY klient.id, klient.emer
ORDER BY shpenzimet_totale DESC;
"""

df = pd.read_sql(query, engine)

plt.figure(figsize=(12, 6))
plt.bar(df['emri_klientit'], df['shpenzimet_totale'])
plt.xlabel('Emri i Klientit')
plt.ylabel('Shpenzimet Totale')
plt.title('Klientët me më shumë shpenzime')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()