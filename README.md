# ZOAU Python Stubs

Type stubs for IBM Z Open Automation Utilities (ZOAU) Python package (`zoautil_py`).

## Purpose

This package provides type hints and IntelliSense support for the ZOAU Python
package when developing on non-z/OS systems (like macOS, Linux, or Windows).
The stubs allow you to:

- Get autocomplete and type checking in VS Code and other IDEs
- Write code that uses ZOAU APIs with full IDE support
- Run the same code on z/OS without any modifications

## How It Works

The stubs package uses the same package name (`zoautil_py`) as the real ZOAU
package. When you install it in "editable" mode on your development machine:

1. **On your development machine**: Python finds the stub package and provides
   IntelliSense
2. **On z/OS**: Python finds the real ZOAU package (which takes precedence)
   and uses it at runtime

This works because:

- The real ZOAU package on z/OS is installed in the system Python path
- The stub package is installed in editable mode in your local environment
- Python's import system prioritizes the real package when both are available

## Installation

### On Your Development Machine (macOS/Linux/Windows)

Install the stubs in editable mode:

```bash
cd /path/to/zoautil_py-stubs
pip install -e .
```

The `-e` flag installs in "editable" mode, which means:

- Changes to the `.pyi` files are immediately available
- The package links to this directory rather than copying files
- You can update the stubs without reinstalling

### On z/OS

**Do not install this package on z/OS!** The real ZOAU package should already
be installed on z/OS. Your code will automatically use the real package when
running on z/OS.

## Usage

Write your code normally using ZOAU imports:

```python
from zoautil_py import mvscmd, datasets
from zoautil_py.ztypes import DDStatement, FileDefinition

# Your code here - works on both dev machine and z/OS
result = mvscmd.execute_authorized("LISTCAT")
```

### Development Workflow

1. **Write code on your dev machine** with full IntelliSense support
2. **Test locally** (stubs provide type checking but no runtime functionality)
3. **Deploy to z/OS** - code runs unchanged with the real ZOAU package

## VS Code Configuration

For best results, configure VS Code's Python extension:

1. Open VS Code settings (Cmd+, on macOS, Ctrl+, on Windows/Linux)
2. Search for "Python: Analysis Extra Paths"
3. Add the path to this directory if needed (usually automatic with editable install)

Or add to `.vscode/settings.json` in your project:

```json
{
    "python.analysis.extraPaths": [
        "/path/to/zoautil_py-stubs"
    ]
}
```

## Updating the Stubs

Since the package is installed in editable mode, you can update the `.pyi`
files directly:

1. Edit the `.pyi` files in the `zoautil_py/` directory
2. Save the changes
3. Restart VS Code's Python language server (Cmd+Shift+P → "Python: Restart
   Language Server")

## Package Structure

```text
zoautil_py-stubs/
├── pyproject.toml              # Package configuration
├── setup.py                    # Setup script
├── README.md                   # This file
├── INSTALL.md                  # Detailed installation guide
├── QUICKSTART.md               # Quick 2-minute setup guide
├── SOLUTION_SUMMARY.md         # Architecture and design notes
└── zoautil_py/                 # Stub package
    ├── __init__.py             # Package initialisation
    ├── py.typed                # Marker file for type checkers
    ├── core.pyi                # C extension: core ZOAU library calls
    ├── _zoau_io.pyi            # C extension: z/OS record-stream I/O
    ├── _zoau_dynalloc.pyi      # C extension: dynamic DD allocation
    ├── zoau_io.py              # Public I/O wrapper (ZIOBase, RecordIO)
    ├── zoau_io.pyi             # Stubs for zoau_io.py
    ├── common.py               # Common utilities
    ├── core_return_codes.py    # Return code constants
    ├── datasets.py             # Dataset operations
    ├── exceptions.py           # Exception definitions
    ├── gdgs.py                 # GDG operations
    ├── jobs.py                 # Job operations
    ├── members.py              # PDS/PDSE member operations
    ├── mvscmd.py               # MVS command execution
    ├── opercmd.py              # Operator command execution
    ├── utilities.py            # Utility functions
    ├── volumes.py              # Volume operations
    ├── vsam.py                 # VSAM dataset operations
    ├── zsystem.py              # z/OS system information
    └── ztypes.py               # Type definitions
```

## Troubleshooting

### IntelliSense not working

1. Verify installation: `pip list | grep zoautil`
2. Restart VS Code's Python language server
3. Check Python interpreter is correct: Cmd+Shift+P → "Python: Select Interpreter"

### Import errors on z/OS

Make sure you **did not** install this stub package on z/OS. Only the real
ZOAU package should be installed there.

### Conflicts between stub and real package

This should not happen if:

- Stubs are installed in editable mode on dev machine only
- Real ZOAU is installed on z/OS only
- You don't install both in the same environment

## License

MIT License - See LICENSE file for details

## Contributing

To add or update stubs:

1. Edit the appropriate `.pyi` file in `zoautil_py/`
2. Follow Python stub file conventions (PEP 484)
3. Test that IntelliSense works in VS Code
4. Commit your changes

## References

- [IBM Z Open Automation Utilities Documentation](https://www.ibm.com/docs/en/zoau)
- [Python Type Hints (PEP 484)](https://www.python.org/dev/peps/pep-0484/)
- [Python Stub Files (PEP 561)](https://www.python.org/dev/peps/pep-0561/)
