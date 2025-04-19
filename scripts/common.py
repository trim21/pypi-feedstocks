import dataclasses
from typing import Annotated, Any, Optional

import pydantic
from rattler import MatchSpec


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class PypiInfo:
    name: str
    author: str | None
    author_email: str | None
    description: str
    home_page: str | None
    project_url: str | None
    version: str


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class Digest:
    sha256: str | None = None


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class Release:
    digests: Digest
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


def normalize_spec(s: str) -> str:
    return str(MatchSpec(s))
