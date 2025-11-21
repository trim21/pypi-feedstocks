# pypi conda mirrors

release some pypi packages to conda ecosystem

you can find packages at these channels:

- <https://prefix.dev/channels/pypi-mirrors> (recommended)
- <https://anaconda.org/pypi-mirrors/repo> (daily mirrored from previous channel)

## policy

- Only pure python package, which means it has `*-py3-none-any.whl` wheel on pypi so we do not need to build anything.
- If a package is also packed by conda-forge, we will drop it from here

## packages

|         pypi         |  version  | build |
| :------------------: | :-------: | :---: |
|      durationpy      |   0.10    |   1   |
|   qbittorrent-api    | 2025.11.1 |   0   |
| rapidocr-onnxruntime |   1.4.4   |   4   |
|        sslog         | 0.0.0a52  |   2   |
|   transmission-rpc   |  7.0.11   |   3   |

## removed

valkey: use https://github.com/conda-forge/valkey-py-feedstock
