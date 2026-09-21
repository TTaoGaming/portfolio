"""Frozen, data-only OpenEvolve-style evaluate(program_path) adapter.
No candidate imports, eval(), exec(), subprocesses or network calls.
No OpenEvolve dependency is needed for local testing.
Higher combined_score is better. Valid 425 => 1.0; valid 424 => 425/424.
The search representation is restricted, not a global shortest-chain solver.
"""
from __future__ import annotations
import ast,hashlib,json,sys
from pathlib import Path
TARGET=int('ffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52971',16)
KEYS={'SMALL','PREFIX_BASE','PREFIX_SHIFTS','DEFERRED','TAIL'}

def literal_recipe(path:str)->dict:
    raw=Path(path).read_bytes()
    if not raw or len(raw)>16_384: raise ValueError('candidate size limit')
    tree=ast.parse(raw.decode('utf-8'))
    if sum(1 for _ in ast.walk(tree))>3000: raise ValueError('syntax size limit')
    data={}
    for node in tree.body:
        if isinstance(node,ast.Expr) and isinstance(node.value,ast.Constant) and type(node.value.value) is str: continue
        if not isinstance(node,ast.Assign) or len(node.targets)!=1 or not isinstance(node.targets[0],ast.Name):
            raise ValueError('only literal assignments are admitted')
        name=node.targets[0].id
        if name not in KEYS or name in data: raise ValueError('unknown or duplicate field')
        data[name]=ast.literal_eval(node.value)
    if data.keys()!=KEYS: raise ValueError('required fields missing')
    def integer(n,minimum=1,maximum=TARGET):
        if type(n) is not int or not minimum<=n<=maximum: raise ValueError('integer bound')
    integer(data['PREFIX_BASE'])
    for key,width in [('SMALL',2),('DEFERRED',3),('TAIL',2)]:
        entries=data[key]
        if type(entries) is not list or len(entries)>128: raise ValueError('list bound')
        for entry in entries:
            if type(entry) not in (tuple,list) or len(entry)!=width: raise ValueError('tuple arity')
            for j,n in enumerate(entry): integer(n,0 if key=='DEFERRED' and j==0 else 1)
    if type(data['PREFIX_SHIFTS']) is not list or len(data['PREFIX_SHIFTS'])>32: raise ValueError('prefix bound')
    for k in data['PREFIX_SHIFTS']: integer(k,1,384)
    for k,d in data['TAIL']: integer(k,1,384)
    for index,a,b in data['DEFERRED']: integer(index,0,len(data['TAIL'])-1)
    return data

def expand(data:dict)->list[tuple[int,int,int]]:
    rows=[]; available={1}
    def add(a:int,b:int)->int:
        c=a+b
        if a not in available or b not in available: raise ValueError('unavailable operand')
        if c in available or c>TARGET: raise ValueError('duplicate or oversized result')
        if len(rows)>=1024: raise ValueError('operation limit')
        rows.append((c,a,b));available.add(c);return c
    def shift(a:int,k:int)->int:
        for _ in range(k): a=add(a,a)
        return a
    for a,b in data['SMALL']: add(a,b)
    acc=data['PREFIX_BASE']
    if acc not in available: raise ValueError('prefix base was not built')
    for k in data['PREFIX_SHIFTS']: acc=add(shift(acc,k),acc)
    for index,(k,d) in enumerate(data['TAIL']):
        for at,a,b in data['DEFERRED']:
            if at==index: add(a,b)
        acc=add(shift(acc,k),d)
    if not rows or rows[-1][0]!=TARGET: raise ValueError('wrong exact scalar exponent')
    return rows

def inspect(path:str)->dict:
    rows=expand(literal_recipe(path))
    squares=sum(a==b for _,a,b in rows)
    raw=''.join(f'{c} {a} {b}\n' for c,a,b in rows).encode()
    return {'valid':True,'operations':len(rows),'squarings':squares,
            'multiplications':len(rows)-squares,'combined_score':425.0/len(rows),
            'canonical_sha256':hashlib.sha256(raw).hexdigest(),
            'promotion_candidate':len(rows)<425}

def evaluate(program_path:str)->dict[str,float]:
    try:
        result=inspect(program_path)
        # Return only the objective, avoiding accidental averaging of raw costs.
        return {'combined_score':result['combined_score']}
    except (OSError,ValueError,SyntaxError,TypeError,RecursionError,MemoryError):
        return {'combined_score':0.0}

if __name__=='__main__':
    if len(sys.argv) not in (2,3): raise SystemExit('Usage: evaluator.py recipe.py [output_chain.txt]')
    try:
        report=inspect(sys.argv[1])
        if len(sys.argv)==3:
            rows=expand(literal_recipe(sys.argv[1]))
            Path(sys.argv[2]).write_text(''.join(f'{c} {a} {b}\n' for c,a,b in rows),encoding='ascii')
        print(json.dumps(report,sort_keys=True,indent=2))
    except (OSError,ValueError,SyntaxError,TypeError,RecursionError,MemoryError) as e:
        print(json.dumps({'valid':False,'error':str(e)})); raise SystemExit(1)
