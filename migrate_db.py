"""Quick migration script to add new columns to existing DB."""
import sqlite3

conn = sqlite3.connect('red_teaming.db')
c = conn.cursor()

c.execute('PRAGMA table_info(scan_runs)')
cols = [r[1] for r in c.fetchall()]
print('Before:', cols)

additions = [
    ('scan_type', 'TEXT'),
    ('strategy_id', 'TEXT'),
    ('topic', 'TEXT'),
    ('max_turns', 'INTEGER'),
    ('conversation_data', 'TEXT'),
]

for name, typedef in additions:
    if name not in cols:
        sql = f'ALTER TABLE scan_runs ADD COLUMN {name} {typedef}'
        print(f'Executing: {sql}')
        c.execute(sql)
    else:
        print(f'Already exists: {name}')

conn.commit()

c.execute('PRAGMA table_info(scan_runs)')
cols_after = [r[1] for r in c.fetchall()]
print('After:', cols_after)
conn.close()
print('Migration complete!')
