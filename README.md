# Extractify API

This is the repository for the extractify_api service.

# Development

## Python version management

Install pyenv with Homebrew [pyenv](https://github.com/pyenv/pyenv#homebrew-in-macos):

```bash
### installing
brew update
brew install pyenv

### setup path https://github.com/pyenv/pyenv#set-up-your-shell-environment-for-pyenv
```

## Python

Install Python 3.10.7 using [pyenv](https://github.com/pyenv/pyenv):

```bash
pyenv install 3.10.7
```

## Poetry

We are using [Poetry](https://python-poetry.org/) as a tool for Python packaging and dependency management. <br/><br/>
Windows installation:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

macOS installation:

```bash
brew install poetry
```

## Set up

We recommend using [PyCharm](https://www.jetbrains.com/pycharm/) as an IDE, but others are available as well.

After installing Poetry you can clone the repository and install the dependencies:

```bash
$ git clone git@github.com:peerpower/<project_name>.git
$ cd <project_name>
$ poetry install
```

### Ensure correct Python version used for virtual environment

Retrieve Python 3.10.7 absolute path:

```bash
echo $(pyenv shell 3.10.7; pyenv which python)
### the result will be like this
/Users/xxx/.pyenv/versions/3.10.7/bin/python
```

Create virtual environment with specified Python version:

```bash
poetry env use <python-3.10.7-absolute-path>
```

Activate virtual environment:

```bash
$ poetry shell
```

> When running with poetry shell, you should see prefix similar to this one `(<project_name>-Hs04dj-F-py3.10)`

If you need to find the project interpreter in your IDE, you can find it in these locations depending on your platform:

- Linux: ~/.cache/pypoetry/virtualenvs/
- macOS: ~/Library/Application Support/pypoetry/virtualenvs/

### Setup pre-commit

The formatters and linters are run using the [pre-commit](https://pre-commit.com/) framework. `pre-commit` is automatically installed as a development dependency with Poetry.
Each `git commit` will then automatically run code formatting before you
even commit the code.

### Installation

Install pre-commit:

```bash
pre-commit install
```

Try to run pre-commit hook:

```bash
pre-commit run --all-files
```

### Environment Variables

Copy `.env.example` to `.env`

### Django Secret Key

Generate a unique secret key by running the following command:

```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Add the secret key generated in the command line to the `DJANGO_SECRET_KEY` variable in the `.env` file.

## Django

We use [Django](https://docs.djangoproject.com/en/4.1/) as a web framework.

Activate the Poetry virtual environment:

```bash
$ poetry shell
```

You can check that Django is working correctly by running the server:

```bash
$ python manage.py runserver
```

The server is running at [localhost](http://127.0.0.1:8000/).

## Docker

### Installation:

You can run the project inside a docker. To install the prerequisites, follow the links below.

#### macOS

https://docs.docker.com/docker-for-mac/install/

or just:

```bash
$ brew cask install docker
```

#### Ubuntu

https://docs.docker.com/install/linux/docker-ce/ubuntu/

### Running Inside a Docker:

```bash
$ docker-compose build
$ docker-compose up
```

Server should be running at address http://0.0.0.0:8000/.

## Code Style

We use several code formatters to follow the PEP-8 guidelines. See dedicated docs for [code style](./docs/code-style.md) and for instructions on setting up autocorrection and project formatting.

## Tests

We use [pytest](https://docs.pytest.org/en/7.1.x/) framework for unit testing.

To run all tests:

```bash
$ poetry run pytest
```
