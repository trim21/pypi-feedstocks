import hashlib
import pathlib
from typing import Any

import click
import httpx
import jmespath
import pkginfo
import pydantic
import yaml
from packaging.requirements import Requirement
from rattler import MatchSpec

from scripts.common import Pypi, normalize_spec

project_root = pathlib.Path(__file__).parent.parent

client = httpx.Client()


@click.command()
@click.argument("packages", nargs=-1)
def main(packages: list[str]):
    if not packages:
        packages = [f.name for f in project_root.joinpath("packages").iterdir()]

    for package in packages:
        data = client.get(f"https://pypi.org/pypi/{package}/json")
        pkg = pydantic.TypeAdapter(Pypi).validate_json(data.text)

        recipe_file = project_root.joinpath("packages", pkg.info.name, "recipe.yaml")

        recipe_content = recipe_file.read_text("utf8")

        wheels = [
            x for x in pkg.releases[pkg.info.version] if x.filename.endswith(".whl")
        ]
        if len(wheels) != 1:
            raise Exception("expecting one wheels", wheels)

        wheel = wheels[0]

        cache_wheel_name = project_root.joinpath(".cache").joinpath(wheel.filename)
        cache_wheel_name.parent.mkdir(exist_ok=True)

        if cache_wheel_name.exists() and cache_wheel_name.stat().st_size == wheel.size:
            wheel_content = cache_wheel_name.read_bytes()
        else:
            wheel_content = client.get(wheel.url).content
            cache_wheel_name.write_bytes(wheel_content)

        sha256 = hashlib.sha256(wheel_content).hexdigest()
        if wheel.digests.sha256:
            assert (
                sha256 == wheel.digests.sha256
            ), f"sha256 should match, expecting {wheel.digests.sha256}, got {sha256} instead"

        bdist = pkginfo.wheel.Wheel(str(cache_wheel_name))

        run_requirements = []

        if bdist.requires_python:
            run_requirements.append(
                normalize_spec(str("python " + bdist.requires_python))
            )
            recipe_content = update_host_requirements(
                package, recipe_content, bdist.requires_python
            )
        else:
            run_requirements.append("python")
            recipe_content = update_host_requirements(package, recipe_content, "")

        for require in bdist.requires_dist:
            req = Requirement(require)
            if req.marker:
                continue
            run_requirements.append(normalize_spec(str(req)))

        recipe_content = update_run_requirements(
            package, recipe_content, run_requirements
        )

        recipe: dict[str, Any] = yaml.safe_load(recipe_content)

        if "source" not in recipe:
            recipe_file.write_text(
                update_object_patch(recipe_content, pkg.info.version, "context.version")
                + "\n\n"
                + "\n".join(
                    [
                        "source:",
                        "  url: " + wheel.url,
                        "  sha256: " + sha256,
                    ]
                ),
                encoding="utf-8",
                newline="\n",
            )
            continue

        with_new_version = update_object_patch(
            recipe_content,
            pkg.info.version,
            "context.version",
        )

        with_new_source_url = update_object_patch(
            with_new_version,
            wheel.url,
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


def update_host_requirements(pkg: str, content: str, requires_python: str) -> str:
    run_requires = yaml.safe_load(content)["requirements"]["host"]

    new_deps = {
        "python": "python" + requires_python,
        "pip": "pip",
    }

    for i, r in enumerate(run_requires):
        m = MatchSpec(r)
        if m.name.normalized in new_deps:
            expected = new_deps[m.name.normalized]
            if r != expected:
                print(f"update requirements.run {r!r} => {expected!r}")
                content = update_object_patch(
                    content,
                    expected,
                    f"requirements.host[{i}]",
                )
            continue

        raise ValueError(
            f"extra requirements.host {r!r} in {pkg}, please remove manually"
        )

    return content


def update_run_requirements(pkg: str, content: str, from_pypi: list[str]) -> str:
    print(pkg, from_pypi)
    new_deps = {
        name_alias.get(name, name): replace_pkg_name(value)
        for name, value in {MatchSpec(r).name.normalized: r for r in from_pypi}.items()
    }

    run_requires = yaml.safe_load(content)["requirements"]["run"]

    current_deps = {MatchSpec(r).name.normalized: r for r in run_requires}

    for name, dep in new_deps.items():
        if name not in current_deps:
            raise ValueError(f"please add requirements.run {dep!r} to {pkg} manually")

    for i, r in enumerate(run_requires):
        m = MatchSpec(r)
        if m.name.normalized in new_deps:
            expected = new_deps[m.name.normalized]
            if r != expected:
                print(f"update requirements.run {r!r} => {expected!r}")
                content = update_object_patch(
                    content,
                    expected,
                    f"requirements.run[{i}]",
                )
            continue

        raise ValueError(
            f"extra requirements.run {r!r} in {pkg}, please remove manually"
        )

    return content


# TODO: use a pypi-conda mapping to fix names
def replace_pkg_name(spec: str):
    m = MatchSpec(spec)
    version = m.version
    if not version:
        return name_alias.get(m.name.normalized, m.name.normalized)
    return name_alias.get(m.name.normalized, m.name.normalized) + " " + version


name_alias = {"opencv-python": "py-opencv"}


if __name__ == "__main__":
    main()
