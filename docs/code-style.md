# Code style

## Formatters & Linters
We will use [Black](https://github.com/python/black) and [isort](https://github.com/PyCQA/isort) for formatting the codebase.
`Black` automatically formats and rewrites code so developers don't need to worry about it.
`isort` keeps all imports nicely ordered.

We will also use [mypy](https://github.com/python/mypy) and [flake8](https://github.com/PyCQA/flake8) for linting code.
`mypy` is a static type checker for Python. `flake8` is a wrapper running `PyFlakes`, `pycodestyle` and `mccabe`.

### Formatting & Linting Command-line Commands
Format project manually
```bash
black .
```

Check if project is formatted
```bash
black . --check
```

Run all validation manually
```bash
pre-commit run --all-files
```

###  Set-up Auto-formatting Shortcut Key

If you are using PyCharm, you can set up an autocorrection shortcut so that it will be available in your IDE:
- Go to `PyCharm` -> `Preferences` -> `Tools` -> `External tools`
- Add new `External tool` with:
    - Name: `black`
    - Program:  `<path to black>`
    - Arguments: `$FilePath$`
    - Working directory: `$ProjectFileDir$`
    - Output paths to refresh: `$FilePathRelativeToProjectRoot$`
    - Go into Advanced options -> Disable checkbox `Open console for tool output`
- Add keyboard shortcut:
    - Go to `PyCharm` -> `Preferences` -> `Keymap`
    - Find `External tools`, right click on `black` and choose `add keyboard shortcut`
    - `CTRL + ALT + SHIFT + S` is an unused keyboard shortcut in Pycharm, but you can choose whatever key binding suits you best

You can also set up black on file changes but this is not recommended. If you are editing code it can save at unexpected moments and your code will change when you don't want it to.
It's much more predictable to use it manually than to run it on file changes. Setup looks the same for IntelliJ IDEA, just look for `Settings` instead of `Preferences`.

##  Module Import Convention

When importing modules, use absolute imports except for:
- ```__init__``` files
- settings packages
- subpackages
