import path from 'node:path';
import { fileURLToPath } from 'node:url';
import clientConfig from '../ebi-metagenomics-client/vite.config.ts';

const root = fileURLToPath(new URL('../', import.meta.url));
const client = path.join(root, 'ebi-metagenomics-client');
const files = new Map(['config.json', 'config.private.json'].map((filename) => [
  path.join(client, filename), path.join(root, 'overrides', 'client', filename),
]));

export default async (env) => {
  const config = typeof clientConfig === 'function' ? await clientConfig(env) : clientConfig;
  return {
    ...config,
    plugins: [
      {
        name: 'local-api-settings',
        enforce: 'pre',
        resolveId(source, importer) {
          if (!importer) return;
          const filename = path.resolve(path.dirname(importer.split('?')[0]), source);
          return files.get(filename);
        },
      },
      ...(config.plugins ?? []),
    ],
    server: {
      ...config.server,
      fs: { ...config.server?.fs, allow: [root] },
    },
  };
};
