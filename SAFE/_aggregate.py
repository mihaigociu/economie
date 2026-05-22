"""Aggregations over the SAFE Romania contracts ledger.
Run: /Users/2346263/projects/economie/.venv/bin/python _aggregate.py
"""
import pandas as pd

df = pd.read_csv('/Users/2346263/projects/economie/SAFE/contracts_ledger.csv')
total = df['value_eur_m'].sum()

print("=== BASIC ===")
print(f"Programmes: {len(df)}")
print(f"Total value (EUR M): {total:,.1f}")
print(f"Total value (EUR bn): {total/1000:,.3f}")

print("\n=== BY COUNTRY OF PRIME ===")
g = df.groupby('country_of_prime')['value_eur_m'].agg(['sum','count']).sort_values('sum', ascending=False)
g['share_%'] = (g['sum'] / total * 100).round(1)
print(g.round(1).to_string())

print("\n=== GERMAN vs NON-GERMAN ===")
def cat(c):
    if pd.isna(c) or c == 'unknown': return 'unknown'
    s = str(c)
    if 'Germany' in s: return 'German'
    return 'Non-German'
df['german'] = df['country_of_prime'].apply(cat)
g2 = df.groupby('german')['value_eur_m'].agg(['sum','count'])
g2['share_%'] = (g2['sum'] / total * 100).round(1)
print(g2.round(1).to_string())

print("\n=== Rheinmetall-prime ===")
rh = df[df['prime_contractor'].str.contains('Rheinmetall', case=False, na=False)]
print(f"Programmes: {len(rh)}")
print(f"Value (EUR M): {rh['value_eur_m'].sum():,.1f}")
print(f"Share: {rh['value_eur_m'].sum()/total*100:.1f}%")
print(rh[['id','programme_name_en','value_eur_m']].to_string(index=False))

print("\n=== BY PROCEDURE TYPE ===")
g3 = df.groupby('procedure_type')['value_eur_m'].agg(['sum','count']).sort_values('sum', ascending=False)
g3['share_%'] = (g3['sum'] / total * 100).round(1)
print(g3.round(1).to_string())

print("\n=== BY TRACK ===")
g4 = df.groupby('track')['value_eur_m'].agg(['sum','count']).sort_values('sum', ascending=False)
g4['share_%'] = (g4['sum'] / total * 100).round(1)
print(g4.round(1).to_string())

print("\n=== BY DOMAIN ===")
g5 = df.groupby('domain')['value_eur_m'].agg(['sum','count']).sort_values('sum', ascending=False)
g5['share_%'] = (g5['sum'] / total * 100).round(1)
print(g5.round(1).to_string())

print("\n=== BY STATUS ===")
g6 = df.groupby('status')['value_eur_m'].agg(['sum','count']).sort_values('sum', ascending=False)
g6['share_%'] = (g6['sum'] / total * 100).round(1)
print(g6.round(1).to_string())
