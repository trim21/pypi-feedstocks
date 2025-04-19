import hashlib
import pathlib
from typing import Any

import click
import httpx
import jmespath
import pydantic
import yaml

from scripts.common import Pypi

project_root = pathlib.Path(__file__).parent.parent

client = httpx.Client()


@click.command()
@click.argument("package", required=True, nargs=1)
def main(package: str):
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
            update_object_patch(
                recipe_file.read_text("utf8"), pkg.info.version, "context.version"
            )
            + "\n\n"
            + "\n".join(
                [
                    "source:",
                    "  url: " + url,
                    "  sha256: " + sha256,
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        return

    with_new_version = update_object_patch(
        recipe_file.read_text(encoding="utf8"),
        pkg.info.version,
        "context.version",
    )

    with_new_source_url = update_object_patch(
        with_new_version,
        url,
        "source.url",
    )

    with_new_source_sha256 = update_object_patch(
        with_new_source_url,
        sha256,
        "source.sha256",
    )

    recipe_file.write_text(with_new_source_sha256, newline="\n")


def update_object_patch(old_content: str, new_value: str, object_path: str) -> str:
    recipe = yaml.safe_load(old_content)
    current_value = jmespath.search(object_path, recipe)
    if not isinstance(current_value, str):
        raise ValueError(
            f"expecting to update str, got {current_value!r} instead: {object_path=!r}"
        )

    if old_content.count(current_value) == 1:
        new_content = old_content.replace(current_value, new_value)
        assert jmespath.search(object_path, yaml.safe_load(new_content)) == new_value
        return new_content

    s = old_content.split(current_value)

    for i in range(1, len(s)):
        new_content = current_value.join(s[:i]) + new_value + current_value.join(s[i:])
        if jmespath.search(object_path, yaml.safe_load(new_content)) == new_value:
            return new_content

    raise Exception("failed to update content")


if __name__ == "__main__":
    main()
