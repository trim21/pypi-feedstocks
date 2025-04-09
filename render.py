import yaml
import pathlib

project_root = pathlib.Path(__file__).parent


packages = project_root.joinpath("packages")


outputs = []

for pkg in packages.iterdir():
    outputs.append(yaml.safe_load(pkg.read_bytes()))


outputs.sort(key=lambda x: x["context"]["name"])

project_root.joinpath("recipe.yaml").write_text(yaml.dump({"outputs": outputs}))
