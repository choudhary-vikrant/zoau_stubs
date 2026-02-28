# Quick Start Guide

Get up and running with ZOAU stubs in 2 minutes!

## Installation (One-Time Setup)

```bash
cd /path/to/zoautil_py-stubs
pip install -e .
```

## Verify It Works

1. Open VS Code
2. Create a new Python file
3. Type this code:

```python
from zoautil_py import mvscmd
from zoautil_py.ztypes import DDStatement

# Start typing 'mvscmd.' and you should see autocomplete!
```

If you see autocomplete suggestions, you're all set! 🎉

## What This Does

- **On your Mac/Linux/Windows**: Provides IntelliSense and type hints
- **On z/OS**: Your code automatically uses the real ZOAU package
- **No code changes needed**: Same imports work everywhere

## Usage in Your Projects

Just import ZOAU normally:

```python
from zoautil_py import mvscmd, datasets
from zoautil_py.ztypes import DDStatement, FileDefinition

# Write your code with full IntelliSense support
result = mvscmd.execute_authorized("LISTCAT")
```

## Troubleshooting

### IntelliSense not working?

1. Restart VS Code's Python language server:
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Python: Restart Language Server"
   - Press Enter

2. Check installation:

   ```bash
   pip list | grep zoautil
   ```

   You should see: `zoautil-py-stubs`

### Still not working?

See [INSTALL.md](INSTALL.md) for detailed troubleshooting.

## Key Points

✅ **DO** install stubs on your development machine  
✅ **DO** use the same imports in your code  
✅ **DO** test your code on z/OS  

❌ **DON'T** install stubs on z/OS  
❌ **DON'T** commit stubs to your project repository  
❌ **DON'T** expect stubs to provide runtime functionality  

## Next Steps

- Read [README.md](README.md) for detailed documentation
- See [INSTALL.md](INSTALL.md) for advanced configuration
- Start coding with full IntelliSense support!

## Questions?

The stubs provide type hints only. For ZOAU functionality documentation, see:

- [IBM ZOAU Documentation](https://www.ibm.com/docs/en/zoau)
