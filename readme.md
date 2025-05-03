# pypi conda mirrors

release some pypi packages to conda ecosystem

you can find packages at these channels:

- <https://anaconda.org/pypi-mirrors/repo>
- <https://prefix.dev/channels/pypi-mirrors>

## policy

- Only pure python package, which means it has `*-py3-none-any.whl` wheel on pypi so we do not need to build anything.
- If a package is also packed by conda-forge, we will drop it from here

## packages

|         pypi         | version  | build |
| :------------------: | :------: | :---: |
|      durationpy      |   0.9    |   2   |
|   qbittorrent-api    | 2025.5.0 |   0   |
| rapidocr-onnxruntime |  1.4.4   |   3   |
|        sslog         | 0.0.0a52 |   2   |
|   transmission-rpc   |  7.0.11  |   2   |
