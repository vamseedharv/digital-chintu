import js from '@eslint/js'
import importPlugin from 'eslint-plugin-import'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import globals from 'globals'
import tseslint from 'typescript-eslint'
import eslintConfigPrettier from 'eslint-config-prettier'

export default tseslint.config(
  { ignores: ['dist', 'coverage'] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2023,
      globals: globals.browser,
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
      import: importPlugin,
    },
    settings: {
      // import/no-restricted-paths resolves import paths itself; without
      // this the default resolver only knows .js/.json and every .ts/.tsx
      // import silently fails to resolve, so the rule never fires.
      'import/resolver': {
        node: {
          extensions: ['.js', '.jsx', '.ts', '.tsx'],
        },
      },
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      // Mirrors the backend's import-linter contract (backend/pyproject.toml):
      // api/theme are cross-cutting infrastructure, never allowed to depend
      // on the UI layers built on top of them.
      'import/no-restricted-paths': [
        'error',
        {
          zones: [
            {
              target: './src/api',
              from: ['./src/components', './src/routes', './src/app'],
              message: 'src/api must not depend on components/routes/app — it is a lower-level layer they depend on.',
            },
            {
              target: './src/theme',
              from: ['./src/components', './src/routes', './src/app'],
              message: 'src/theme must not depend on components/routes/app — it is a lower-level layer they depend on.',
            },
          ],
        },
      ],
    },
  },
  eslintConfigPrettier,
)
