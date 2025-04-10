import yaml
import pathlib

project_root = pathlib.Path(__file__).parent.parent


packages = project_root.joinpath("packages")


outputs = []

for pkg in packages.rglob("recipe.yaml"):
    outputs.append(yaml.safe_load(pkg.read_bytes()))


outputs.sort(key=lambda x: x["context"]["name"])


readme = project_root.joinpath("readme.in").read_text("utf-8").strip()


lines = [
    "",
    "| pypi | version | build |",
    "| :--: | :-----: | :---: |",
]

for pkg in outputs:
    lines.append(
        "| {name} | {version} | {build} |".format(
            **pkg["context"], build=pkg["build"]["number"]
        )
    )


project_root.joinpath("readme.md").write_text(
    readme + "\n".join(lines), encoding="utf-8"
)
