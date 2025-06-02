# rm -rf / --no-preserve-root

## Requirements

- Python 3.12
- venv

## Installation

### Clone the repository

```bash
git clone git@github.com:Gregami67/TestingforLLMPrompts_nopreserveroot.git
```

### Setup environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### Apply migrations

```bash
python manage.py migrate
```

### Start app

```bash
python manage.py runserver
```
