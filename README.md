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
        "host": os.environ.get("PG_HOST", "127.0.0.1"),
        "port": os.environ.get("PG_PORT", 5432),
        "user": os.environ.get("PG_USER", "postgres"),
        "password": os.environ.get("PG_PASSWORD", "postgres"),
        "database": os.environ.get("PG_DATABASE", "piccolo"),
    },
)
```
