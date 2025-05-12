import pathlib

import yaml

project_root = pathlib.Path(__file__).parent.parent

packages = []

for pkg in project_root.joinpath("packages").rglob("recipe.yaml"):
    packages.append(yaml.safe_load(pkg.read_bytes()))

packages.sort(key=lambda x: x["context"]["name"])

readme = project_root.joinpath("readme.in").read_text("utf-8").strip()

lines = [
    "",
    "",
    "| pypi | version | build |",
    "|:----:|:-------:|:-----:|",
]

for pkg in packages:
    lines.append(
        "| {name} | {version} | {build} |".format(
            **pkg["context"], build=pkg["build"]["number"]
        )
    )

lines.extend(
    [
        "## removed",
        "valkey: use https://github.com/conda-forge/valkey-py-feedstock",
    ]
)
project_root.joinpath("readme.md").write_bytes((readme + "\n".join(lines)).encode())
