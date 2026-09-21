#!/usr/bin/env python3
"""Strict, data-only exact-exponent checker. Python 3.10+; standard library only.

Input: ASCII decimal rows `output_exponent left_exponent right_exponent`.
The implicit, free starting exponent is 1. Every row charges one operation.
Target is independently fixed; candidate metadata never chooses the target.
This is a mathematical certificate checker, not production cryptographic code.
"""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path

ORDER = int('ffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52973',16)
TARGET = ORDER - 2
ROW = re.compile(rb'[1-9][0-9]{0,119} [1-9][0-9]{0,119} [1-9][0-9]{0,119}')

def verify(path: str | Path) -> tuple[dict, list[tuple[int,int,int]]]:
    raw=Path(path).read_bytes()
    if not raw or len(raw)>512_000 or not raw.endswith(b'\n'):
        raise ValueError('empty, oversized, or missing final newline')
    lines=raw[:-1].split(b'\n')
    if len(lines)>1024: raise ValueError('too many operations')
    available={1}; dependencies={}; rows=[]; sq=0
    for i,line in enumerate(lines,1):
        if not ROW.fullmatch(line): raise ValueError(f'row {i}: noncanonical decimal syntax')
        out,a,b=map(int,line.split(b' '))
        if a not in available or b not in available: raise ValueError(f'row {i}: unavailable input')
        if out!=a+b: raise ValueError(f'row {i}: incorrect sum')
        if out in available: raise ValueError(f'row {i}: duplicate output')
        available.add(out); dependencies[out]=(a,b); rows.append((out,a,b)); sq+=(a==b)
    if rows[-1][0]!=TARGET: raise ValueError('endpoint is not the exact P-384 scalar order minus two')
    needed={1}; todo=[TARGET]
    while todo:
        v=todo.pop()
        if v not in needed:
            needed.add(v); todo.extend(dependencies[v])
    dead=len(available-needed)
    # Unused operations are still charged, not silently pruned.
    return {'valid':True,'operations':len(rows),'squarings':sq,
            'multiplications':len(rows)-sq,'unused_operations':dead,
            'endpoint_hex':format(TARGET,'x'),
            'sha256':hashlib.sha256(raw).hexdigest()},rows

def inverse_reference(x:int, rows:list[tuple[int,int,int]]) -> int:
    if type(x) is not int or not 1<=x<ORDER:
        raise ValueError('input must be a nonzero canonical scalar')
    powers={1:x}
    for out,a,b in rows: powers[out]=(powers[a]*powers[b])%ORDER
    return powers[TARGET]

def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('certificate',type=Path)
    p.add_argument('--expect',nargs=3,type=int,metavar=('TOTAL','S','M'))
    args=p.parse_args()
    try:
        result,_=verify(args.certificate)
        measured=[result[k] for k in ('operations','squarings','multiplications')]
        if args.expect and measured!=args.expect: raise ValueError('operation-count expectation failed')
        print(json.dumps(result,sort_keys=True)); return 0
    except (OSError,ValueError,KeyError) as exc:
        print(json.dumps({'valid':False,'error':str(exc)})); return 1
if __name__=='__main__': sys.exit(main())
