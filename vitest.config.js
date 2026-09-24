
import { defineConfig } from 'vitest/config';
export default defineConfig({
  test: {
    include: ['frontend/tests/**/*.test.js'],
    environment: 'jsdom',
    globals: true
  }
});
