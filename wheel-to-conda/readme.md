convert pure python wheel (pkg-py3-none-any.wheel) to conda package

for example,

expected files:

```
  - site-packages/transmission_rpc/__init__.py
  - site-packages/transmission_rpc/client.py
  - site-packages/transmission_rpc/constants.py
  - site-packages/transmission_rpc/error.py
  - site-packages/transmission_rpc/py.typed
  - site-packages/transmission_rpc/session.py
  - site-packages/transmission_rpc/torrent.py
  - site-packages/transmission_rpc/types.py
  - site-packages/transmission_rpc/utils.py
  - site-packages/transmission_rpc-7.0.11.dist-info/INSTALLER
  - site-packages/transmission_rpc-7.0.11.dist-info/LICENSE # with content: conda
  - site-packages/transmission_rpc-7.0.11.dist-info/METADATA
  - site-packages/transmission_rpc-7.0.11.dist-info/RECORD
  - site-packages/transmission_rpc-7.0.11.dist-info/REQUESTED
  - site-packages/transmission_rpc-7.0.11.dist-info/WHEEL
  - info/about.json
  - info/hash_input.json
  - info/index.json
  - info/link.json
  - info/paths.json
  - info/recipe/recipe.yaml
  - info/recipe/rendered_recipe.yaml
  - info/recipe/variant_config.yaml
  - info/tests/tests.yaml
```
