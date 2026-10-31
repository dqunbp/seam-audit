"""User-facing strings. Every message shown to a user comes from `locales/*.json`."""
import json
from pathlib import Path

LOCALES_DIR = Path(__file__).parent / "locales"
SUPPORTED_LOCALES = ("en", "ru")
DEFAULT_LOCALE = "en"

_catalogs = {
    locale: json.loads((LOCALES_DIR / f"{locale}.json").read_text(encoding="utf-8"))
    for locale in SUPPORTED_LOCALES
}


def t(key: str, locale: str = DEFAULT_LOCALE, **params) -> str:
    """Translate `key` into `locale`, falling back to the default locale."""
    catalog = _catalogs.get(locale, _catalogs[DEFAULT_LOCALE])
    template = catalog.get(key) or _catalogs[DEFAULT_LOCALE].get(key)
    if template is None:
        raise KeyError(f"missing translation key: {key}")
    return template.format(**params)
