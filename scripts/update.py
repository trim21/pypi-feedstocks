import hashlib
import pathlib
from typing import Any

import click
import httpx
import pydantic
import yaml

from scripts.common import Pypi

project_root = pathlib.Path(__file__).parent.parent

client = httpx.Client()


@click.command()
@click.argument("package", required=True, nargs=1)
@click.argument("version", required=True, nargs=1)
def main(package: str, version: str):
    data = client.get(f"https://pypi.org/pypi/{package}/json")
    pkg = pydantic.TypeAdapter(Pypi).validate_json(data.text)
    wheels = [x for x in pkg.releases[pkg.info.version] if x.filename.endswith(".whl")]
    if len(wheels) != 1:
        raise Exception("expecting one wheels", wheels)

    wheel = wheels[0]

    url = wheel.url
    if wheel.digests.sha256:
        sha256 = wheel.digests.sha256
    else:
        sha256 = hashlib.sha256(client.get(url).content).hexdigest()

    recipe_file = project_root.joinpath("packages", pkg.info.name, "recipe.yaml")

    recipe: dict[str, Any] = yaml.safe_load(recipe_file.read_text(encoding="utf-8"))

    if "source" not in recipe:
        recipe_file.write_text(
            recipe_file.read_text(encoding="utf8")
            + "\n\n"
            + "\n".join(
                [
                    "source:",
                    "  url: " + url,
                    "  sha256: " + sha256,
                ]
            ),
            encoding="utf-8",
        )
        return


if __name__ == "__main__":
    main()
