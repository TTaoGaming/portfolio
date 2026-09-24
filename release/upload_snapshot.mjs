// One-attempt, unauthenticated Turbo upload of an already-public snapshot.
// Usage: node upload_snapshot.mjs <payload.json> <sdk-project/package.json> <receipt.json>
import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const [payloadPath, sdkProjectPackageJson, receiptPath] = process.argv.slice(2);
if (!payloadPath || !sdkProjectPackageJson || !receiptPath) throw new Error('ARGUMENTS_REQUIRED');
const requireFromSdkProject = createRequire(pathToFileURL(resolve(sdkProjectPackageJson)));
const { TurboFactory } = requireFromSdkProject('@ardrive/turbo-sdk');
const payload = readFileSync(payloadPath);
const sha256 = createHash('sha256').update(payload).digest('hex');
if (payload.length >= 100_000) throw new Error('PAYLOAD_EXCEEDS_FREE_TIER_TARGET');
if (!payload.includes(Buffer.from('tommytai.public_research_snapshot.v1'))) throw new Error('SCHEMA_MISMATCH');
const turbo = TurboFactory.unauthenticated({ token: 'base-usdc' });

const base = {
  schema: 'tommytai.permaweb_upload_receipt.v1',
  payload_sha256: sha256,
  bytes: payload.length,
  provider: 'ArDrive Turbo',
  client_mode: 'UNAUTHENTICATED_FREE_ONLY',
  paid_funding_available: false,
  attempts: 1,
};
try {
  const result = await turbo.uploadRawX402Data({ data: payload });
  const receipt = {
    ...base,
    status: 'SUBMITTED_GET_BACK_PENDING',
    observed_utc: new Date().toISOString(),
    transaction_id: result?.id ?? null,
    owner: result?.owner ?? null,
    data_caches: result?.dataCaches ?? null,
    fast_finality_indexes: result?.fastFinalityIndexes ?? null,
    measured_spend_usd: null,
  };
  writeFileSync(receiptPath, JSON.stringify(receipt, null, 2) + '\n');
  console.log(JSON.stringify(receipt));
} catch (error) {
  const errorText = String(error?.message ?? error);
  const paymentRequired = /Status 402/.test(errorText);
  const amount = paymentRequired ? /"maxAmountRequired":"(\d+)"/.exec(errorText)?.[1] ?? null : null;
  const receipt = {
    ...base,
    status: paymentRequired ? 'REJECTED_PAYMENT_REQUIRED' : 'SUBMISSION_UNCERTAIN',
    observed_utc: new Date().toISOString(),
    transaction_id: null,
    error_code: paymentRequired ? 'HTTP_402' : 'UPLOAD_ERROR',
    quoted_micro_usdc: amount,
  };
  writeFileSync(receiptPath, JSON.stringify(receipt, null, 2) + '\n');
  console.error(JSON.stringify(receipt));
  process.exitCode = 1;
}
