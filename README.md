[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/psqlpy?style=for-the-badge)](https://pypi.org/project/psqlpy/)

# psqlpy-piccolo

This is a third-party Rust engine for [Piccolo ORM](https://github.com/piccolo-orm/piccolo).  
Under the hood, this engine uses [PSQLPy](https://github.com/qaspen-python/psqlpy), which is Rust-based and blazingly fast 🔥.

## Installation

You can install package with `pip` or `poetry`.

poetry:

```bash
$ poetry add psqlpy-piccolo
```

pip:

```bash
$ pip install psqlpy-piccolo
```

## Usage

Usage is as easy as possible.  
PSQLPy based engine has the same interface as other engines from piccolo.

```python
from psqlpy_piccolo import PSQLPyEngine


DB = PSQLPyEngine(
    config={
        "host": "127.0.0.1",
        "port": 5432,
        "user": "postgres",
        "password": "postgres",
        "database": "psqlpy-piccolo",
    },
)
```
