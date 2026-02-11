import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import env

# Your connection
engine = create_engine(env.DB_URL)

# Execute query
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

# Create pie chart
plt.figure(figsize=(10, 8))
plt.pie(df['nr_gjallesave'], 
        labels=df['qyteti'], 
        autopct='%1.1f%%',  # Show percentages
        startangle=90)
plt.title('Përqindja e gjallesave për çdo qytet', pad=20)
plt.axis('equal')  # Equal aspect ratio ensures pie is circular
plt.tight_layout()
plt.show()