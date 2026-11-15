"""Fechas y años (CLAUDE.md §4)."""
from __future__ import annotations

import datetime as dt

import pandas as pd


def fecha_a_anio(fecha) -> int:
    """Año de una fecha diaria, de 8/16 días o mensual: el año calendario de la fecha.

    Acepta 'YYYY-MM-DD', 'YYYY-MM', date/datetime o Timestamp.
    """
    if isinstance(fecha, (dt.date, dt.datetime, pd.Timestamp)):
        return int(fecha.year)
    s = str(fecha).strip()
    return int(pd.Timestamp(s if len(s) > 7 else s + "-01").year)
