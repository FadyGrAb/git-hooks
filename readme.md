# Git Hooks CLI tool for custom hooks
> This is still a proof of concept. I've created it for educational purposes. Further work is still needed.
## How git hooks work:
When using git, it can execute scripts before and after some git commands. You can read all about them form [here](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks).  

The ***pre-commit*** hook is run first, before you even type in a commit message. It’s used to inspect the snapshot that’s about to be committed.  

## Currently Supported Hooks:
- **mask**: A check that is run before a git `git commit` command to mask the user's pre-defined sensitive data.
- (more are yet to come 😉)


## Setup and usage:
1. The cli tool is written in **Python** which will need Python installed on your system.  
2. Clone this repo into your local machine
```sh
git clone https://github.com/FadyGrAb/git-hooks.git
```
3. cd into to the package directory
```sh
cd git-hooks
```
4. Install the package using pip. This will install it in for the current Python environment.
```sh
pip install .
```
5. To show the tool's help, use
```sh
git-hooks --help
```
or to show commands related help, use
```sh
git-hooks COMMAND --help
```

6. List the currently supported hooks 
```sh
git-hooks list
```
(currently only the `mask` hook is supported)  

7. Initiate a hook with the `init` command.You must execute this inside a git repo. For the mask hook, This will create the *pre-commit* hook inside your repo's `.git/hooks` directory, create the *mask.config* in your repo's root directory and add *\_unmasked_\** and *\mask.config* to your *.gitignore* file. If you want to commit your *mask.config*, remove it from *.gitignore* (⚠️not recommended if you wrote your secrets in plaintext inside it)
```sh
git-hooks init HOOK
```
8. Disable a hook with the `disable` command. The hook must be initiated first.
```sh
git-hooks disable HOOK
```
9. Enable a hook with the `enable` command.
```sh
git-hooks enable HOOK
```
10.  Get the status of your hooks with the `status` command. The status is either *Enabled*, *Disabled* or *Not initialized*.
```sh
git-hooks status
```
### The Mask Git-hook:
#### Motivation:
When I commit code to public repos, I usually mask my sensitive data manually which is not practical nor scalable. So I needed a way to automate that at each git commit.

#### Implementation details:
It's actually a straight forward process, the "***pre-commit***" script in your project's `.git/hooks` directory will read the "***mask.config***" config file which is basically telling the script *what* and *how* to mask your data with an optional *ignore* files list that won't be skipped from the checks.  
The script will check only the modified files. If it finds data that needs to be masked, it will make a copy of original unmasked file adding the "*\_unmasked\_\*" prefix to the file name in the same directory and then mask the original. That way you will always have access to the unmasked data which is ignored by git as the "\_unmasked\_\*" entry is already in *.gitignore*.  
 You don't have to put any files in the `.git/hooks` directory, the cli tool will do it for you.

#### Mask.conig structure:
```toml
[show]                      # The sensitive data you want to mask.
1234565678 = 4              # This will show only the last 4 characters i.e. "****5678"
lksjdfljalkjdfllkjsa = 0    # This will show 0 characters i.e. full mask "********************"
{{ ENV_VAR }} = 4           # You can reference environment variables inside the file.

[ignore]                    # The list of files to ignore
files=["ignoreme.html", "ignoreme2.html"]
```
You write your secrets in the [show] table and specify how many characters you want to show from them (from the right). If you write 0, it will be a full mask. To reference environnement variables, put the variable's name inside a pair of curly braces `{{ <variable name> }}`. If the variable is not set, it will be ignored and a warning message will show up. The `mask.config` file almost resembles toml syntax.  
💡 If you have referenced all your secrets with env vars, you can safely remove `mask.config` from *.gitignore* and commit it.

To activate the mask git hook script, just commit as usual (if there are untracked files, you should add them first to the git staging area `git add example.file`)
```sh
git commit -am "test commit"
```

#### Mask Git hook Example:
1. Install the tool as *Setup and usage* section.
2. Create a new directory and CD into it
```sh
mkdir my-project
cd my-project
```
2. Run `git init` in this directory. Notice the new `.git` directory that is created.
3. Run `git-hooks init mask`. 
4. Edit the "***mask.config***" as follows (located in your repo's root directory):
```toml
[show]
123456789 = 4            
00f0264d065dd4ee7922dfe6 = 0
{{  SECRET_API_KEY  }} = 8

[ignore]
files=[]
```
5. Set the *SECRET_API_KEY* env var:
```sh
# bash
export SECRET_API_KEY="laskdjflkasjdfloiaudsfiuo"
```
```powershell
# windows powershell
$ENV:SECRET_API_KEY="laskdjflkasjdfloiaudsfiuo"
```
6. Add the following file (config.json) to your project's root directory:
```json
{
    "MyAccountNumber": "123456789",
    "MySecretKey": "00f0264d065dd4ee7922dfe6",
    "ApiKey": "laskdjflkasjdfloiaudsfiuo"
}
```
7. Run `git add .`
8. Commit your changes `git commit -m "mask commit"`
9. After the commit you will get the a message for every file that was processed If you didn't receive any, then none contained sensitive data matching your configuration. Your file will be as follows:
```json
{
    "MyAccountNumber": "*****6789",
    "MySecretKey": "************************",
    "ApiKey": "*****************audsfiuo"
}
```
## Testing:
The test scripts are using the *pytest* package. to install it:
```sh
pip install pytest
```
To run the tests:
```sh
pytest -v ./tests
```
## Things to consider:
- This tool is developed on a windows machine and supposed to be os agnostic. I did't fully test it on other OSs.
- This script lacks proper exception handling (for now) so please don't strain it too much :)
- To disable this script, just rename it or add a file extension to it.
- You can add the full path of a file to be ignored in the [ignore] table starting from your project's root directory.
- The `.git` directory isn't pushed to Github with a push, [check here](https://github.com/git-guides/git-push). So in theory, my sensitive data should be safe. But further research is needed.
## Further work to be done:
- [ ] Proper exception handling.
- [x] Packaging.
- [x] Testing.
- [ ] Add more features to mask.config.



