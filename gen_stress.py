import pandas as pd
import numpy as np
from datetime import datetime, timedelta

rows = 20000
services = ['API-Gateway', 'Auth-Service', 'Payment-Processor', 'DB-Cluster', 'Storage-S3']
statuses = ['200', '200', '200', '401', '500', '503']
start_time = datetime(2023, 10, 1, 10, 0, 0)

data = {
    'timestamp': [start_time + timedelta(seconds=i*0.5) for i in range(rows)],
    'service': [np.random.choice(services) for _ in range(rows)],
    'status': [np.random.choice(statuses) for _ in range(rows)],
    'message': ['Log entry ' + str(i) for i in range(rows)]
}

df = pd.DataFrame(data)
# Add a specific failure burst to test anomaly detection
df.loc[5000:5100, 'status'] = '500'
df.loc[5000:5100, 'service'] = 'DB-Cluster'

df.to_csv('c:\\Users\\punam\\antigravity\\stress_test_20k.csv', index=False)
print("Generated 20,000 rows in stress_test_20k.csv")
