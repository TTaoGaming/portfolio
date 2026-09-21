#!/usr/bin/env node
// Independent BigInt verifier. No imports from the generator or Python checker.
import fs from 'node:fs';
import crypto from 'node:crypto';
try {
  const name=process.argv[2];
  if (!name) throw new Error('usage: node verify_node.mjs certificate.txt');
  const raw=fs.readFileSync(name);
  if (!raw.length || raw.length>512000 || raw.at(-1)!==10) throw new Error('size/newline');
  const lines=raw.toString('ascii').slice(0,-1).split('\n');
  if (lines.length>1024) throw new Error('operation limit');
  // Independent decimal encoding of the published scalar order.
  const n=39402006196394479212279040100143613805079739270465446667946905279627659399113263569398956308152294913554433653942643n;
  const known=new Set(['1']);
  let squares=0, last=1n;
  for (let i=0;i<lines.length;i++) {
    const line=lines[i];
    if (!/^[1-9][0-9]{0,119} [1-9][0-9]{0,119} [1-9][0-9]{0,119}$/.test(line)) throw new Error(`syntax ${i+1}`);
    const [c,a,b]=line.split(' ');
    if (!known.has(a)||!known.has(b)) throw new Error(`dependency ${i+1}`);
    if (known.has(c)) throw new Error(`duplicate ${i+1}`);
    last=BigInt(a)+BigInt(b);
    if (last!==BigInt(c)) throw new Error(`sum ${i+1}`);
    known.add(c); squares+=(a===b ? 1:0);
  }
  // Re-encoding also forbids non-ASCII bytes that ascii decoding would mask.
  if (!raw.equals(Buffer.from(lines.join('\n')+'\n','ascii'))) throw new Error('non-ASCII');
  if (last!==n-2n) throw new Error('wrong scalar-inversion exponent');
  console.log(JSON.stringify({valid:true,operations:lines.length,squarings:squares,
    multiplications:lines.length-squares,endpoint_hex:last.toString(16),
    sha256:crypto.createHash('sha256').update(raw).digest('hex')}));
} catch(e) { console.log(JSON.stringify({valid:false,error:String(e.message)})); process.exit(1); }
