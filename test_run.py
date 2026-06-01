import json
from main import analyze, PGNRequest
import asyncio

pgn_text = "1. e4 e5 2. Nf3 Nc6 3. Bc4 d6 4. Nc3 Bg4 5. h3 Bh5 6. Nxe5 Bxd1 7. Bxf7+ Ke7 8. Nd5#"

req = PGNRequest(pgn=pgn_text)
res = analyze(req)

for m in res['moves_data']:
    if m['cat_key'] == 'brilliant':
        print(f"Brilliant move found! {m['san']} with comment: {m['comment']}")
    if m['san'] == 'Nxe5':
        print(f"Nxe5 stats: cpl={m['cpl']}, cat={m['cat_key']}")

print("Done")
