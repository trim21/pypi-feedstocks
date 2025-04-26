# pypi conda mirrors

release some pypi packages to conda ecosystem

<https://prefix.dev/channels/pypi-mirrors>

## policy

- Only pure python package, which means it has `*-py3-none-any.whl` wheel on pypi so we do not need to build anything.
- If a package is also packed by conda-forge, we will drop it from here

## packages

|         pypi         | version  | build |
| :------------------: | :------: | :---: |
|      durationpy      |   0.9    |   1   |
|   qbittorrent-api    | 2025.4.1 |   0   |
| rapidocr-onnxruntime |  1.4.4   |   2   |
|        sslog         | 0.0.0a52 |   1   |
|   transmission-rpc   |  7.0.11  |   1   |
