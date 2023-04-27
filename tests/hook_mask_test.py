import json
import pathlib
import shutil
import subprocess

import pytest
import toml


def test_init_mask():
    root_path = pathlib.Path(__file__).parents[1]
    subprocess.run("git-hooks init mask", shell=True)
    pre_commit_script = root_path / ".git/hooks/pre-commit"
    config_toml = root_path / ".git/hooks/mask.toml"
    gitignore = root_path / ".gitignore"

    assert pre_commit_script.exists() == True
    assert config_toml.exists() == True
    with gitignore.open(mode="r") as f:
        assert "_unmasked_*" in f.read()


def test_exec_mask():
    root_path = pathlib.Path(__file__).parents[1]
    test_files_path = root_path / "tests/test_files"
    if test_files_path.exists():
        shutil.rmtree(test_files_path)
    test_files_path.mkdir(exist_ok=True)

    # Load test configs
    config_toml = root_path / ".git/hooks/mask.toml"
    test_configs = {
        "show": {
            "123456789023423": 5,
            "lkjsdkfjsdlkvouoeijlsdljlsajfdl": 0,
            "my@email.com": 8,
        },
        "ignore": {"files": ["tests/test_files/ignoreme1", "tests/hook_mask_test.py"]},
    }
    with config_toml.open(mode="w") as toml_file:
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
    }
    masked_data = {
        "AccountID": "**********23423",
        "AccountKey": "*******************************",
        "AccountEmail": "****mail.com",
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
