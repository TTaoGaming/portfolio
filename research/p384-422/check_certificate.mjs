#!/usr/bin/env node
// Independent BigInt checker. It does not import the Python generator or verifier.
import fs from 'node:fs';
import crypto from 'node:crypto';

const N = 39402006196394479212279040100143613805079739270465446667946905279627659399113263569398956308152294913554433653942643n;
const EXPECTED_SHA256 = '5228f6c12fda873ebb2eecdb34a858a193e92c718efedf81b2c9de4fd72d3d70';

function verify(path) {
  const raw = fs.readFileSync(path);
  if (!raw.length || raw.length > 512000 || raw.at(-1) !== 10 || raw.includes(13)) {
    throw Error('size or LF newline');
  }
  if ([...raw].some(byte => byte > 127)) throw Error('non-ASCII byte');
  const lines = raw.toString('ascii').slice(0, -1).split('\n');
  if (lines.length > 1024) throw Error('operation limit');
  const known = new Set(['1']);
  let previous = 1n;
  let squarings = 0;
  for (const [offset, line] of lines.entries()) {
    const index = offset + 1;
    if (!/^[1-9][0-9]{0,119} [1-9][0-9]{0,119} [1-9][0-9]{0,119}$/.test(line)) throw Error(`row syntax ${index}`);
    const [outputText, leftText, rightText] = line.split(' ');
    if (!known.has(leftText) || !known.has(rightText)) throw Error(`unavailable parent ${index}`);
    const output = BigInt(outputText), left = BigInt(leftText), right = BigInt(rightText);
    if (output <= previous || known.has(outputText)) throw Error(`not strictly increasing ${index}`);
    if (left >= output || right >= output || left + right !== output) throw Error(`incorrect sum ${index}`);
    known.add(outputText);
    previous = output;
    if (left === right) squarings++;
  }
  if (previous !== N - 2n) throw Error('wrong P-384 scalar inversion target');
  const multiplications = lines.length - squarings;
  if (lines.length !== 422 || squarings !== 382 || multiplications !== 40) throw Error('wrong operation counts');
  const digest = crypto.createHash('sha256').update(raw).digest('hex');
  if (digest !== EXPECTED_SHA256) throw Error('certificate SHA-256 differs');
  return {valid:true, operations:lines.length, squarings, other_multiplications:multiplications,
    weighted_0_8:'345.6', target_hex:'0x'+previous.toString(16), sha256:digest};
}

try {
  if (process.argv.length !== 3) throw Error('usage: node verify.mjs certificate.txt');
  console.log(JSON.stringify(verify(process.argv[2])));
} catch (error) {
  console.error(JSON.stringify({valid:false, error:String(error.message)}));
  process.exit(1);
}
