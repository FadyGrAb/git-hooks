import json
import os
import pathlib
import shutil
import subprocess

import pytest
import toml


def test_init_mask():
    root_path = pathlib.Path(__file__).parents[1]
    subprocess.run("git-hooks init mask", shell=True)
    pre_commit_script = root_path / ".git/hooks/pre-commit"
    mask_config = root_path / "mask.config"
    gitignore = root_path / ".gitignore"

    assert pre_commit_script.exists() == True
    assert mask_config.exists() == True
    with gitignore.open(mode="r") as f:
        content = f.read()
        assert "_unmasked_*" in content
        assert "/mask.config" in content


def test_exec_mask():
    root_path = pathlib.Path(__file__).parents[1]
    test_files_path = root_path / "tests/test_files"
    if test_files_path.exists():
        shutil.rmtree(test_files_path)
    test_files_path.mkdir(exist_ok=True)

    # Load test configs
    mask_config = root_path / "mask.config"
    os.environ["ENV_VAR_1"] = "myEnvVar_1"
    os.environ["ENV_VAR_2"] = "myEnvVar_2"

    test_configs = {
        "show": {
            "123456789023423": 5,
            "lkjsdkfjsdlkvouoeijlsdljlsajfdl": 0,
            "my@email.com": 8,
            "{{ ENV_VAR_1 }}": 5,
            "{{ ENV_VAR_2 }}": 6,
            "{{ ENV_VAR_3 }}": 5,  # Not set
        },
        "ignore": {"files": ["tests/test_files/ignoreme1", "tests/hook_mask_test.py"]},
    }
    with mask_config.open(mode="w") as toml_file:
        toml.dump(test_configs, toml_file)

    # Create test files
    test_files = [
        "tests/test_files/config.json",
        "tests/test_files/ignoreme1",
        "tests/test_files/ignoreme2",
    ]
    test_data = {
        "AccountID": "123456789023423",
        "AccountKey": "lkjsdkfjsdlkvouoeijlsdljlsajfdl",
        "AccountEmail": "my@email.com",
        "MySecretValue1": "myEnvVar_1",
        "MySecretValue2": "myEnvVar_2",
    }
    masked_data = {
        "AccountID": "**********23423",
        "AccountKey": "*******************************",
        "AccountEmail": "****mail.com",
        "MySecretValue1": "*****Var_1",
        "MySecretValue2": "****vVar_2",
    }
    for file in test_files:
        with (root_path / file).open(mode="w") as f:
            json.dump(test_data, f)

    # Run mask git-hook
    subprocess.run("git add .", shell=True).check_returncode()
    subprocess.run("git-hooks exec mask", shell=True).check_returncode()
    try:
        for file in test_files:
            file_path = root_path / file
            with file_path.open(mode="r") as f:
                data = json.load(f)
            if file in test_configs["ignore"]["files"]:
                assert data == test_data
                assert not (file_path.parent / ("_unmasked_" + file_path.name)).exists()
            else:
                assert data == masked_data
                assert (file_path.parent / ("_unmasked_" + file_path.name)).exists()
    except Exception as e:
        if test_files_path.exists():
            shutil.rmtree(test_files_path)
        raise e
    finally:
        if test_files_path.exists():
            shutil.rmtree(test_files_path)
