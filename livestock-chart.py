import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import env

engine = create_engine(env.DB_URL)

query = """
SELECT 
    ferma.qyteti AS qyteti,
    SUM(gjallese.sasia) AS nr_gjallesave
FROM ferma
JOIN gjallese ON ferma.id = gjallese.id_ferme
GROUP BY ferma.qyteti
ORDER BY nr_gjallesave DESC;
"""

df = pd.read_sql(query, engine)

plt.figure(figsize=(10, 8))
plt.pie(df['nr_gjallesave'], 
        labels=df['qyteti'], 
        autopct='%1.1f%%',  
        startangle=90)
plt.title('Përqindja e gjallesave për çdo qytet', pad=20)
plt.axis('equal')  
plt.tight_layout()
plt.show()