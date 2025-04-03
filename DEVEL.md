
# Development Notes

This is because I cannot remember this very well:

Install project in editable mode and add development dependencies

```sh
pip install -e ".[dev]"
```

Install pre-commit hook. Test tools manually.

```sh
pre-commit install
black src/
isort src/
```

Run pytest to see whether everything works

```sh
pytest
```
