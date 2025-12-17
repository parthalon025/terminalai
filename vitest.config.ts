import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    // Test environment
    environment: 'node',

    // Global test setup
    globals: true,

    // Test file patterns
    include: ['tests/**/*.{test,spec}.{ts,tsx}'],
    exclude: ['node_modules', 'dist', '.git'],

    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'text-summary', 'lcov', 'html', 'json'],
      reportsDirectory: './coverage',
      include: ['src/**/*.ts'],
      exclude: [
        'src/**/*.d.ts',
        'src/**/*.test.ts',
        'src/**/*.spec.ts',
        'src/**/index.ts',
        'src/types/**',
      ],
      // Coverage thresholds
      thresholds: {
        global: {
          statements: 80,
          branches: 80,
          functions: 80,
          lines: 80,
        },
      },
      // Clean coverage before running tests
      clean: true,
    },

    // Test timeouts
    testTimeout: 10000,
    hookTimeout: 10000,

    // Parallel execution
    pool: 'threads',
    poolOptions: {
      threads: {
        singleThread: false,
      },
    },

    // Reporter configuration
    reporters: ['default', 'html'],

    // Watch mode configuration
    watch: true,
    watchExclude: ['node_modules', 'dist'],

    // Type checking
    typecheck: {
      enabled: true,
      checker: 'tsc',
    },

    // Retry failed tests
    retry: process.env.CI ? 2 : 0,

    // Setup files
    setupFiles: ['./tests/setup.ts'],

    // Mock reset
    mockReset: true,
    restoreMocks: true,
    clearMocks: true,
  },

  // Path aliases
  resolve: {
    alias: {
      '@': '/src',
      '@tests': '/tests',
    },
  },
});
