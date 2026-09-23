#!/usr/bin/env python3
import argparse, hashlib
N=int('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC7634D81F4372DDF581A0DB248B0A77AECEC196ACCC52973',16)
TARGET=N-2; EXPECTED='5228f6c12fda873ebb2eecdb34a858a193e92c718efedf81b2c9de4fd72d3d70'
PREFIX=[(1,1),(2,1),(3,3),(6,6),(12,12),(24,24),(48,48),(96,96),(192,3),(195,195),(390,390),(780,780),(1560,3),(1563,192),(1755,192),(1755,780),(2535,2),(2535,1560)]
TAIL={186:1,181:1563,167:1563,162:4095,151:2535,148:4095,141:1563,135:1947,132:1,123:2537,115:3,112:4095,103:1563,94:195,86:1563,78:1947,72:2535,60:1947,53:2535,50:3,34:1563,29:1755,25:4095,23:1755,13:2537,7:4095,3:1,0:2537}
def build():
 rows=[]; seen={1}
 def add(a,b):
  assert a in seen and b in seen; o=a+b; assert o not in seen and a<o and b<o; rows.append((o,a,b)); seen.add(o); return o
 for a,b in PREFIX:add(a,b)
 x=4095
 for shift in (12,24,48,96):
  base=x
  for _ in range(shift):x=add(x,x)
  x=add(x,base)
 assert x==(1<<192)-1
 for pos in range(191,-1,-1):
  x=add(x,x)
  if pos in TAIL:x=add(x,TAIL[pos])
 return rows
rows=build(); seen={1}; prev=1; S=M=0
for o,a,b in rows:
 assert a in seen and b in seen and o==a+b and o>prev and a<o and b<o
 S+=a==b; M+=a!=b; seen.add(o); prev=o
assert prev==TARGET and (len(rows),S,M)==(422,382,40)
blob=''.join(f'{o} {a} {b}\n' for o,a,b in rows).encode(); sha=hashlib.sha256(blob).hexdigest(); assert sha==EXPECTED
ap=argparse.ArgumentParser(); ap.add_argument('--emit'); args=ap.parse_args()
if args.emit:open(args.emit,'wb').write(blob)
print(f'PASS {len(rows)} {S}S {M}M sha256={sha}')
