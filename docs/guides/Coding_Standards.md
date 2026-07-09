# Coding Standards

Enforced by tooling, not just convention — `make lint` runs all of this.
Config lives in `backend/pyproject.toml` and
`frontend-dashboard/eslint.config.js` / `tsconfig.app.json`; this doc
summarizes what's actually configured there rather than repeating it.

## Python (`backend/`)

- **Ruff** (lint): rule sets `E`, `F`, `I` (import sorting), `UP`
  (pyupgrade), `B` (bugbear), `SIM` (simplify). Line length 100.
- **Black** (format): line length 100, target Python 3.12.
- **mypy** (`--strict`): every function needs full type annotations. New
  code should type-check cleanly under strict mode — see
  [Developer_Guide.md](Developer_Guide.md#linting-formatting-type-checking)
  for how to handle genuine third-party typing gaps.
- Type hints are required everywhere, per the Foundation pack's original
  standard — this is what mypy strict enforces.

## TypeScript (`frontend-dashboard/`)

- **ESLint** (flat config, `eslint.config.js`): `@eslint/js` recommended +
  `typescript-eslint` recommended + `eslint-plugin-react-hooks` recommended +
  `eslint-plugin-react-refresh` (`only-export-components`) +
  `eslint-config-prettier` (disables any rule that'd conflict with Prettier).
- **Prettier**: no semicolons, single quotes, 100-char print width, trailing
  commas everywhere (`.prettierrc`).
- **TypeScript strict mode**: `strict: true` plus `noUncheckedIndexedAccess`
  and `noImplicitOverride` (`tsconfig.app.json`), on top of the Vite
  template's own `noUnusedLocals`/`noUnusedParameters`/`erasableSyntaxOnly`.
  `erasableSyntaxOnly` means constructor parameter-property shorthand
  (`constructor(private x: T)`) isn't allowed — see `api/client.ts`'s
  `ApiError` for the explicit-field alternative.

## Both languages

- Prefer editing existing files over creating new ones; don't add
  abstractions (a new shared module, a new context, a new layer) until a
  second real consumer needs it.
- Comments explain *why*, not *what* — see the existing codebase for the
  style (e.g. `backend/app/db/session.py`'s comment on the sqlite path
  parsing, `frontend-dashboard/src/theme/ThemeContext.ts`'s split rationale).
- Naming conventions are documented in
  [docs/architecture/02_REPOSITORY_STRUCTURE.md](../architecture/02_REPOSITORY_STRUCTURE.md#naming-conventions-in-use-today).

## Running the checks

```bash
make lint      # both packages, check only
make format    # both packages, auto-fix
```

Or per-package (see `backend/README.md` / `frontend-dashboard/README.md` for
the individual commands).
