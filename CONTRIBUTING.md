### Installation

1. Clone the repository. You must have your SSH public key added to GitHub as the repository is private.

```sh
git clone https://github.com/isd-2026/project-assignment-iotbay-marketplace-superawesometeamname a1-isd

cd a1-isd
```

2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) to simplify project management:

```sh
# macos/linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

3. Optionally install the [EditorConfig](https://marketplace.visualstudio.com/items?itemName=EditorConfig.EditorConfig) extension for VSCode. This ensures our code is consistent across different authors.

4. Install dependencies and pre-commit hooks for auto code formatting:

```sh
uv sync
uv run pre-commit install
```

### Commands

1. Test the program:

```sh
uv run pytest
```

2. Run the program:

```sh
uv run dev
```


### Setting up your branch

> [!IMPORTANT]
> Never commit feature code to the main branch!

You should develop your feature on your own branch. To do this, follow these steps:

1. Ensure the repository is up to date:

```sh
git pull
```

2. Create and switch to a branch:

```sh
git switch -c tomas/example-feature-00
```

3. Make your changes, then commit them:

```sh
# stage your files
git add -A

# commit them
git commit -m "a descriptive message"
```

4. Push your branch to GitHub:

```sh
# The -u flag tells GitHub to remember that "origin" is the
# destination for `git push`. Subsequent pushes can be done using
# just `git push`.
git push -u origin tomas/example-feature-00
```

4. Once all your changes have been made, go to [this page](https://github.com/isd-2026/project-assignment-iotbay-marketplace-superawesometeamname/compare) to make a pull request, change the compared branch to the branch you made, and follow the steps to create and merge it in to the main branch.
