"""En BD todo se guarda en UTC sin zona; los filtros se interpretan en APP_TZ (Colombia)."""
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo


def a_utc_naive(dt):
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def parsear_fecha_evento(valor):
    """ISO 8601 ('2026-11-19T15:30:00Z'), formato Laravel ('2026-11-19 15:30:00') o timestamp.
    Sin zona se asume UTC. Sin valor -> ahora."""
    if valor in (None, ""):
        return datetime.now(timezone.utc).replace(tzinfo=None)
    if isinstance(valor, (int, float)):
        return datetime.fromtimestamp(valor, tz=timezone.utc).replace(tzinfo=None)
    texto = str(valor).strip().replace("Z", "+00:00")
    return a_utc_naive(datetime.fromisoformat(texto))


def parsear_parametro(valor, tz_nombre, fin_de_dia=False):
    """'YYYY-MM-DD' (día en hora local) o fecha-hora ISO -> UTC sin zona.
    fin_de_dia=True: la fecha se toma como el inicio del día siguiente (límite exclusivo)."""
    tz = ZoneInfo(tz_nombre)
    texto = valor.strip()
    if len(texto) == 10:
        d = date.fromisoformat(texto)
        if fin_de_dia:
            d = d + timedelta(days=1)
        return datetime(d.year, d.month, d.day, tzinfo=tz).astimezone(timezone.utc).replace(tzinfo=None)
    dt = datetime.fromisoformat(texto.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz)
    return a_utc_naive(dt)


def iso_utc(dt):
    return None if dt is None else dt.isoformat(timespec="seconds") + "Z"
