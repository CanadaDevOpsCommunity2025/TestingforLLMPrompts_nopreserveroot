# rm -rf / --no-preserve-root

## Purpose

Platform for testing similar llm prompts against eachother

## Needed

- What prompts we will test
- Create frontend like chatgpt
- No need for detailed feedback, something simple and to the point

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

### Create super user

```bash
python manage.py createsuperuser
```

### Start app

```bash
python manage.py runserver
```
