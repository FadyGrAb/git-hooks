from setuptools import setup, find_packages
import pathlib

template_files = [str(file) for file in pathlib.Path("githooks/templates").iterdir()]

setup(
    name="git-hooks",
    version="0.0.2",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["Click", "toml", "colorama", "jinja2"],
    data_files=[("", template_files)],
    entry_points={
        "console_scripts": ["git-hooks = githooks.scripts.git_hooks:cli"],
    },
)
