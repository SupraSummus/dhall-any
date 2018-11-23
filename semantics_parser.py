import yaml
import parglare
from pprint import pprint

from parglare_adapter import to_parglare_grammar

with open('semantics.bnf.yml', 'rt') as f:
    grammar = yaml.load(f)
pprint(grammar)
pg_grammar, start = to_parglare_grammar(grammar['productions'], grammar['terminals'], grammar['start'])
parser = parglare.GLRParser(pg_grammar, ws='')

t = parser.parse("""
    t₀ ⇥ t₁   [ ts₀… ] ⇥ [ ts₁… ]
    ─────────────────────────────
    [ t₀, ts₀… ] ⇥ [ t₁, ts₁… ]
""")


pprint(t)
