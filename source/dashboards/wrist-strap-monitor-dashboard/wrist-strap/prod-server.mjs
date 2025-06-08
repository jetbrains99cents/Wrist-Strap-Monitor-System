// prod-server.mjs
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

// Set the environment variables with the *content* of the files
process.env.PORT = '3001';
process.env.NITRO_SSL_KEY = readFileSync(resolve('./localhost+2-key.pem'), 'utf-8');
process.env.NITRO_SSL_CERT = readFileSync(resolve('./localhost+2.pem'), 'utf-8');

// Now, dynamically import and run the actual Nuxt server entry point
await import('./.output/server/index.mjs');