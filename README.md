Removes both the specified package and its orphans from the current environment.

## Install

- `pipx install pip-remove`

It is recommended you use `pipx` (pip install pipx) so that you can use `pip-remove` in any environment without having to install it on it

## Usage

`pip-remove package_name`

You can add the `-y` flag to skip the confirmation prompts

`pip-remove -y package_name`


Run `pip-remove` in the environment you want to remove the package from
Also, if you run `pip-remove` from the global environment it will not check for used orphans and simply ask to remove all of them


## Features
- ✅ Detects Python environment from the shell you run it in, only need to install once
- ✅ Ignores files ignored by git
- ✅ Checks for orphans still being used in the codebase (if in virtual environment)