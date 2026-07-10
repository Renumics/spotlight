---
slug: /docs/development
title: Contributing to Spotlight
---

## Setting up Spotlight for development

In order to start development in spotlight as of now the easiest method is
to checkout the repository and install development dependencies.

The spotlight backend is a [FastAPI](https://fastapi.tiangolo.com/em/) server written in `python`, serving the dataset
and the frontend.<br />
The frontend is a [React](https://reactjs.org/) application written in `typescript`.

Therefore, for development, you'll need to install both `python` together with `uv`
and `nodejs` with `pnpm` to get started.

!!! info

    If you want to contribute to spotlight in any form and struggle anywhere along the way please reach out to us.

    We are more than happy to help out and guide you through the process.

### Install dependencies

#### Developing on Linux

Install [python3](https://www.python.org/) together with [uv](https://docs.astral.sh/uv/)

```bash
sudo apt update
sudo apt install python3 python3-dev
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install [nodejs](https://nodejs.org/en/) together with [pnpm](https://pnpm.io/)

```bash
sudo apt install nodejs
curl -fsSL https://get.pnpm.io/install.sh | sh -

# check your installed node version
node -v
```

We recommend using at least node version 18.
In order to install the latest version check out [NodeSource on Github](https://github.com/nodesource/distributions)

You might need to restart your terminal in order to use `pnpm` as a command.

#### Using asdf

Alternatively, you can manage all of `python`, `uv`, `nodejs` and `pnpm` with a single
tool using [asdf](https://asdf-vm.com/).

```bash
asdf plugin add python
asdf plugin add uv
asdf plugin add nodejs
asdf plugin add pnpm
asdf install
```

The versions are read from the `.tool-versions` file in the spotlight repository.

### Setup Spotlight Repository

Visit the [spotlight repository](https://github.com/Renumics/spotlight) and click **Fork**.
Setup your forked repository by cloning it and adding spotlight as an additional remote.

```bash
git clone https://github.com/YOUR_GIT_USERNAME/spotlight.git
cd spotlight
git remote add upstream https://github.com/renumics/spotlight.git
```

Inside the spotlight repository you'll find a `Makefile` which contains all the commands to get you started.
First install development dependencies and pre-commit.

```bash
make init
```

and run the development server

```bash
make dev
```

## Submit your work

Please make sure that you have [pre-commit](https://pre-commit.com/) hooks installed and
that the hooks successfully ran for the added changes.<br />
This can be verified by creating a commit and checking if automated tests are run before the commit is created.

```bash
uv run pre-commit install --hook-type pre-commit
uv run pre-commit install --hook-type pre-push
```

Submit your improvements, fixes and new features to Spotlight by creating a
[Pull Request](https://opensource.guide/how-to-contribute/#opening-a-pull-request).

## Using [direnv](https://direnv.net/)

In order to make development easier [direnv](https://direnv.net/) can be used to automatically setup the environment
on entering the spotlight folder.

The provided [.envrc](https://github.com/Renumics/spotlight/blob/main/.envrc) file automatically activates
the uv environment and sets environment variables in .env and .env.local.
