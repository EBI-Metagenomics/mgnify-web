import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../', import.meta.url));
const output = path.join(root, 'overrides', 'client');
await mkdir(output, { recursive: true });

for (const filename of ['config.json', 'config.private.json']) {
  let config;
  try {
    config = JSON.parse(await readFile(path.join(root, 'ebi-metagenomics-client', filename), 'utf8'));
  } catch (error) {
    if (filename !== 'config.private.json' || error.code !== 'ENOENT') throw error;
    config = {};
  }
  config.api_v2 = 'http://localhost:8000/';
  config.api_branchwater = 'http://localhost:8000/services/branchwater/';
  await writeFile(path.join(output, filename), `${JSON.stringify(config, null, 2)}\n`, { mode: 0o600 });
}
console.log('Local API v2 settings: overrides/client/config{,.private}.json');
