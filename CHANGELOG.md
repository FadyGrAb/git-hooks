# Changelog  
***
All notable change to this tool will be documented in this file.  
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
## Unreleased
---
There aren't currently any unreleased features.
## 0.0.4 - 2023-05-07
---
### Added
- "pytest" to the list of dependencies in setup.py.
- Test case for "-r/--reverse" option for the mask hook.

### Fixed
- Added newline before "mask.config" in ".gitignore" when initializing mask hook.

### Changed
- The "-f/--file" flag is not mandatory anymore when using the "-r/--reverse" flag. If not set, the effect of the hook will be reversed on all of the file currently in the .ghunmask in the repo's root.
- Slimming down the clean_up module for tests.

### Removed
- The ".masked" file which appears in each changed file directory.

## 0.0.3 - 2023-05-05
---
### Added
- Ability to unmask a previously masked file.
- The `-r`/`--reverse` option for reversing a hook.
- The `-f`/`--file` option to specify the file for the reverse hook.
- A `.masked` file will appear in the same directory as the original masked file listing all the files that were masked in this directory.

### Fixed
- The mask hook will ignore "." directories if passed as a changed file from git.

