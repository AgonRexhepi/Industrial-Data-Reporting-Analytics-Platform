"""
File parsers – return a pandas DataFrame from a raw file path.
"""
from __future__ import annotations

import io
import json

import pandas as pd


def parse_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def parse_excel(path: str) -> pd.DataFrame:
    return pd.read_excel(path, engine="openpyxl")


def parse_json(path: str) -> pd.DataFrame:
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    if isinstance(raw, list):
        return pd.DataFrame(raw)
    if isinstance(raw, dict):
        return pd.DataFrame([raw])
    raise ValueError("Unsupported JSON structure — expected list or dict")


def parse_parquet(path: str) -> pd.DataFrame:
    return pd.read_parquet(path)


def parse_xml(path: str) -> pd.DataFrame:
    return pd.read_xml(path)


_PARSERS = {
    "csv": parse_csv,
    "excel": parse_excel,
    "json": parse_json,
    "parquet": parse_parquet,
    "xml": parse_xml,
}


def parse_file(path: str, file_format: str) -> pd.DataFrame:
    parser = _PARSERS.get(file_format)
    if parser is None:
        raise ValueError(f"Unsupported format: {file_format}")
    return parser(path)
