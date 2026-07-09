# scripts

Developer bootstrap scripts, one per shell so setup works the same way on
every supported platform:

- `setup.sh` — Linux, macOS, Raspberry Pi OS, and Git Bash/WSL on Windows.
- `setup.ps1` — native Windows PowerShell.

Both scripts create the backend virtual environment, install backend and
frontend dependencies, and copy `.env.example` files to `.env` where missing.
They are also wired up as `make setup` (see the root [Makefile](../Makefile)).
