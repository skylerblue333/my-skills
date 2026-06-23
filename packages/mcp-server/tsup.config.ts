import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/server.ts', 'src/composites.ts'],
  format: ['esm'],
  dts: true,
  clean: true,
  shims: true,
  splitting: false,
  sourcemap: true,
  banner: {
    js: '#!/usr/bin/env node',
  },
});
