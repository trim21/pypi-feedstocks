import dataclasses
import pathlib
from typing import Annotated, Any, Optional

import click
import httpx
import pkginfo
import pydantic
import yaml
from packaging.requirements import Requirement
from packaging.version import Version
from rattler import MatchSpec


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class PypiInfo:
    name: str
    author: str | None
    author_email: str | None
    description: str
    home_page: str | None
    project_url: str | None


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class Release:
    # comment_text: str
    # downloads: int
    filename: str
    has_sig: bool
    md5_digest: str
    package_type: Annotated[str, pydantic.Field(alias="packagetype")]
    python_version: str
    size: int
    url: str
    requires_python: str | None
    yanked: Optional[bool] = None
    yanked_reason: Optional[Any] = None


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class Pypi:
    info: PypiInfo
    releases: dict[str, list[Release]]


project_root = pathlib.Path(__file__).parent.parent


def quoted_presenter(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="'")


class quoted(str):
    pass


yaml.add_representer(quoted, quoted_presenter)

client = httpx.Client()


@click.command()
@click.argument("packages", required=True, nargs=-1)
def main(packages: list[str]):

    for package in packages:
        data = client.get(f"https://pypi.org/pypi/{package}/json")
        pkg = pydantic.TypeAdapter(Pypi).validate_json(data.text)
        print(pkg.info.name)
        recipe = project_root.joinpath("packages", pkg.info.name, "recipe.yaml")
        recipe.parent.mkdir(exist_ok=True)
        recipe.write_text(
            yaml.dump(build_recipe(pkg), sort_keys=False),
            encoding="utf8",
        )


def build_recipe(pkg: Pypi) -> Any:
    latest_version = max(pkg.releases.keys(), key=Version)

    latest_releases = [
        p for p in pkg.releases[latest_version] if p.package_type == "bdist_wheel"
    ]

    if len(latest_releases) != 1:
        raise Exception(
            "unexpected release counts: ",
            len(latest_releases),
            [p.filename for p in latest_releases],
        )

    wheel = latest_releases[0]

    cache = project_root.joinpath(".cache")
    wheel_path = cache.joinpath(wheel.filename)

    if (not wheel_path.exists()) or (wheel_path.stat().st_size != wheel.size):
        cache.mkdir(exist_ok=True)
        r = client.get(wheel.url)
        cache.joinpath(wheel.filename).write_bytes(r.content)

    bdist = pkginfo.wheel.Wheel(str(cache.joinpath(wheel.filename)))

    run_requirements = []

    for require in bdist.requires_dist:
        req = Requirement(require)
        if req.marker:
            continue
        run_requirements.append(quoted(normalize_spec(str(req))))

    return {
        "context": {"name": quoted(pkg.info.name), "version": quoted(latest_version)},
        "package": {
            "name": quoted("${{ name }}"),
            "version": quoted("${{ version }}"),
        },
        "build": {
            "noarch": "python",
            "number": 0,
            "script": {
                "interpreter": "nu",
                "content": quoted(
                    "PIP_NO_INDEX=false ${{ PYTHON }} -m pip install --no-deps ${{ name }}==${{ version }}"
                ),
            },
        },
        "requirements": {
            "build": ["nushell"],
            "host": [
                quoted(normalize_spec("python" + (wheel.requires_python or ""))),
                "pip",
            ],
            "run": [
                quoted(normalize_spec("python" + (wheel.requires_python or ""))),
                *run_requirements,
            ],
        },
        "tests": [{"python": {"imports": [pkg.info.name.replace("-", "_")]}}],
    }


def normalize_spec(s: str) -> str:
    return str(MatchSpec(s))


if __name__ == "__main__":
    main()
