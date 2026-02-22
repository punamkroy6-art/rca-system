import pandas as pd
import numpy as np
from datetime import datetime, timedelta

rows = 5000
categories = ['Hardware', 'Software', 'Access Management', 'Network', 'Email', 'ERP System', 'Security', 'Voice/VOIP', 'Mobile Device', 'Printing']
states = ['New', 'In Progress', 'On Hold', 'Resolved', 'Closed']
priorities = ['P1 - Critical', 'P2 - High', 'P3 - Moderate', 'P4 - Low']
start_time = datetime(2023, 1, 1, 0, 0, 0)

data = {
    'Incident Number': ['INC' + str(100000 + i) for i in range(rows)],
    'Opened At': [start_time + timedelta(hours=i*0.5) for i in range(rows)], # Spans ~100 days
    'Category': [np.random.choice(categories) for _ in range(rows)],
    'State': [np.random.choice(states) for _ in range(rows)],
    'Priority': [np.random.choice(priorities) for _ in range(rows)],
    'Short Description': ['System issue ' + str(i) for i in range(rows)]
}

df = pd.DataFrame(data)
# Add a massive spike in P1 Hardware tickets mid-way
df.loc[2000:2100, 'Priority'] = 'P1 - Critical'
df.loc[2000:2100, 'Category'] = 'Hardware'

df.to_csv('c:\\Users\\punam\\antigravity\\service_desk_test.csv', index=False)
print("Generated service_desk_test.csv")
