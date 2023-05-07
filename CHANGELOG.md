# Changelog  
***
All notable change to this tool will be documented in this file.  
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
## Unreleased
---
There aren't currently any unreleased features.
## 0.0.4 - 2023-05-05
---
### Added
- Ability to unmask a previously masked file.
- The `-r`/`--reverse` option for reversing a hook.
- The `-f`/`--file` option to specify the file for the reverse hook.
- A `.masked` file will appear in the same directory as the originial masked file listing all the files that were masked in this directory.

### Fixed
- The mask hook will ignore "." directories if passed as a changed file from git.

### Changed
### Removed
