import { compile } from 'json-schema-to-typescript';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function run() {
  const schemasDir = path.resolve(__dirname, '../../../packages/contracts/schemas');
  const outDir = path.resolve(__dirname, '../src/types');
  fs.mkdirSync(outDir, { recursive: true });

  const files = fs.readdirSync(schemasDir).filter((f) => f.endsWith('.json') && f !== 'contracts.json');
  let output = '/* eslint-disable */\n/**\n* Auto-generated from packages/contracts JSON Schemas.\n* DO NOT EDIT DIRECTLY.\n*/\n\n';

  for (const file of files) {
    const filePath = path.join(schemasDir, file);
    const schema = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    const modelName = path.basename(file, '.json');
    try {
      const ts = await compile(schema, modelName, {
        bannerComment: '',
        unreachableDefinitions: false,
      });
      output += `// ================= ${modelName} =================\n` + ts + '\n\n';
    } catch (err) {
      console.error(`Failed to compile ${file}:`, err);
    }
  }

  const dest = path.join(outDir, 'contracts.d.ts');
  fs.writeFileSync(dest, output);
  console.log(`Generated contracts.d.ts at ${dest}`);
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
