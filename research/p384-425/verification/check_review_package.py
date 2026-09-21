#!/usr/bin/env python3
"""Run the three certificate checkers and 20 negative controls each without network access.
Requirements: Python 3.10+, Node.js with BigInt, C++17 compiler, Boost headers.
No binaries are included in the distribution; C++ is built in a temp folder.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,platform,re,shutil,subprocess,sys,tempfile,time
from datetime import datetime,timezone
from verify_python import verify,inverse_reference,ORDER,TARGET

ROOT=Path(__file__).resolve().parents[1]
EXPECTED_HASH='14da9fd3bfa7e3e615c78c5d6cf73dc0262ea3ff65eb29553be502de37f0df05'

def require(ok:bool,reason:str)->None:
    if not ok: raise RuntimeError(reason)

def run(argv:list[str],timeout:float=30)->subprocess.CompletedProcess:
    return subprocess.run(argv,text=True,capture_output=True,timeout=timeout)

def binary_stream(target:int)->bytes:
    x=1; rows=[]
    for bit in bin(target)[3:]:
        rows.append((2*x,x,x));x*=2
        if bit=='1': rows.append((x+1,x,1));x+=1
    return ''.join(f'{c} {a} {b}\n' for c,a,b in rows).encode()

def main()->None:
    start=time.monotonic()
    print('START',flush=True)
    for exe in ('node','g++'):
        require(shutil.which(exe) is not None,f'{exe} is required')
    source=ROOT/'p384_scalar_inversion_425.txt'
    raw=source.read_bytes()
    require(hashlib.sha256(raw).hexdigest()==EXPECTED_HASH,'canonical file hash mismatch')
    result,rows=verify(source)
    require((result['operations'],result['squarings'],result['multiplications'])==(425,380,45),'candidate counts')
    require(result['unused_operations']==0,'unused candidate operation')
    print('EXACT_CERTIFICATE_PASS',flush=True)
    # Certificate checks only; alternate-JSON data is not needed in this web package.
    # Check scalar order from a distinct established implementation, when available.
    openssl_receipt={'status':'not_available'}
    if shutil.which('openssl'):
        p=run(['openssl','ecparam','-name','secp384r1','-param_enc','explicit','-text','-noout'])
        require(p.returncode==0,'OpenSSL parameter query failed')
        order_hex=re.sub(r'[^0-9a-fA-F]','',p.stdout.split('Order:')[1].split('Cofactor:')[0])
        require(int(order_hex,16)==ORDER,'OpenSSL scalar order mismatch')
        openssl_receipt={'status':'PASS','version':run(['openssl','version']).stdout.strip(),
                         'order_hex':format(int(order_hex,16),'x')}
    print('OPENSSL_PASS',flush=True)
    # Fixed nonzero inputs: 1024 reproducible SHA-derived values, all powers of 2,
    # and explicit boundaries. Reference inverse is independently computed by pow.
    tests={1,2,3,ORDER-1,ORDER-2,ORDER//2,ORDER//2+1}
    tests.update(1<<k for k in range(384))
    for i in range(1024):
        h=hashlib.sha512(f'p384-425-audit-2026-09-21:{i}'.encode()).digest()
        tests.add(1+int.from_bytes(h,'big')%(ORDER-1))
    for x in sorted(tests):
        y=inverse_reference(x,rows)
        require(y==pow(x,TARGET,ORDER),'modular exponent mismatch')
        require(y==pow(x,-1,ORDER),'modular inverse mismatch')
        require((x*y)%ORDER==1,'inverse identity mismatch')
    print('MODULAR_PASS',len(tests),flush=True)
    boundary_rejected=[]
    for x in (0,-1,ORDER,ORDER+1,True):
        try: inverse_reference(x,rows)
        except ValueError: boundary_rejected.append(str(x))
        else: raise RuntimeError('invalid scalar input accepted')
    lines=raw.splitlines(keepends=True)
    i51=next(i for i,(c,_,_) in enumerate(rows) if c==51)
    def replacing(index:int,text:bytes)->bytes:
        x=lines.copy(); x[index]=text; return b''.join(x)
    negatives={
      'empty':b'',
      'missing_final_newline':raw[:-1],
      'truncated_endpoint':b''.join(lines[:-1]),
      'deleted_first_operation':b''.join(lines[1:]),
      'deleted_51':b''.join(lines[:i51]+lines[i51+1:]),
      'duplicate_first_operation':lines[0]+raw,
      'reordered_dependencies':lines[1]+lines[0]+b''.join(lines[2:]),
      'unavailable_parent':replacing(0,b'1000 999 1\n'),
      'self_reference':replacing(0,b'2 2 1\n'),
      'negative_operand':replacing(0,b'2 -1 3\n'),
      'wrong_sum':replacing(0,b'3 1 1\n'),
      'wrong_51_parents':replacing(i51,b'51 1 49\n'),
      'leading_zero':replacing(0,b'02 1 1\n'),
      'header_spoof':b'operations=425\n'+raw,
      'extra_column':replacing(0,b'2 1 1 0\n'),
      'blank_line':b'\n'+raw,
      'non_ascii':bytes([0xB2])+raw[1:],
      'self_consistent_wrong_n_minus_one':raw+f'{TARGET+1} {TARGET} 1\n'.encode(),
      'valid_chain_for_field_prime_minus_two':binary_stream((1<<384)-(1<<128)-(1<<96)+(1<<32)-3),
      'valid_chain_for_scalar_order':binary_stream(ORDER),
    }
    checker_results={}; negative_results={}
    with tempfile.TemporaryDirectory(prefix='p384-verify-') as d:
        tmp=Path(d); binary=tmp/'verify_cpp'
        print('COMPILE',flush=True)
        compiled=run(['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror',str(ROOT/'verification/verify_cpp.cpp'),'-o',str(binary)],60)
        require(compiled.returncode==0,'C++ compilation failed: '+compiled.stderr)
        commands={'python':[sys.executable,str(ROOT/'verification/verify_python.py')],
                  'node':['node',str(ROOT/'verification/verify_node.mjs')],
                  'cpp':[str(binary)]}
        for checker,cmd in commands.items():
            print('CHECKER',checker,flush=True)
            checker_results[checker]={}
            for label,file,counts in [('candidate',source,(425,380,45))]:
                p=run(cmd+[str(file)])
                require(p.returncode==0,f'{checker} {label} failed: {p.stderr}{p.stdout}')
                r=json.loads(p.stdout)
                require(tuple(r[k] for k in ('operations','squarings','multiplications'))==counts,f'{checker} {label} counts')
                checker_results[checker][label]=r
            rejected=[]
            for name,data in negatives.items():
                print('NEGATIVE',checker,name,flush=True)
                file=tmp/(name+'.txt'); file.write_bytes(data)
                p=run(cmd+[str(file)])
                require(p.returncode!=0,f'{checker} ACCEPTED negative case {name}')
                rejected.append(name)
            negative_results[checker]={'rejected':len(rejected),'cases':rejected}
    receipt={'verdict':'PASS','utc':datetime.now(timezone.utc).isoformat(),
       'canonical_sha256':EXPECTED_HASH,'checkers':checker_results,
       'negative_controls':negative_results,'total_negative_rejections':sum(v['rejected'] for v in negative_results.values()),
       'nonzero_modular_tests':len(tests),'invalid_scalar_inputs_rejected':boundary_rejected,
       'json_alternate_encoding':'not_in_this_package','openssl_order_binding':openssl_receipt,
       'python_version':sys.version.split()[0], 'node_version':run(['node','--version']).stdout.strip(),
       'compiler':run(['g++','--version']).stdout.splitlines()[0], 'platform':platform.platform(),
       'elapsed_seconds':round(time.monotonic()-start,3),
       'scope':'mathematical endpoint and count; not production speed, side-channel review, global optimality or external acceptance'}
    (ROOT/'verification/results.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,indent=2,sort_keys=True))
if __name__=='__main__': main()
