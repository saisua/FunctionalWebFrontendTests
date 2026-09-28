#!/usr/bin/env bash
uv run --group docs python -m sphinx -M html docs docs/_build "$@"
