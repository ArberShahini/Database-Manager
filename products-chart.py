import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import env

engine = create_engine(env.DB_URL)

query = """
SELECT 
    ferma.qyteti AS qyteti,
    COUNT(DISTINCT produkt.id) AS nr_produktesh
FROM ferma
JOIN produkt ON ferma.id = produkt.id_ferme
GROUP BY ferma.qyteti
ORDER BY nr_produktesh DESC;
"""

df = pd.read_sql(query, engine)

plt.figure(figsize=(10, 6))
plt.scatter(df['qyteti'], df['nr_produktesh'], s=200, c=df['nr_produktesh'], cmap='viridis', alpha=0.7)
plt.xlabel('Qyteti')
plt.ylabel('Numri i Produkteve')
plt.title('Numri i produkteve sipas qytetit', pad=20)
plt.xticks(rotation=45, ha='right')
plt.colorbar(label='Product Count')
plt.tight_layout()
plt.show()