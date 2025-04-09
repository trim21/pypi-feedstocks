import yaml
import pathlib

project_root = pathlib.Path(__file__).parent


packages = project_root.joinpath("packages")


for pkg in packages.iterdir():
    package = yaml.safe_load(pkg.read_bytes())
    if package["context"]["name"] != pkg.stem:
        raise ValueError(
            f"file {package} and '$.context.name' must be same and it should be package's pypi name"
        )
