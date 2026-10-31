import json

from pixforge.i18n import LOCALES_DIR, SUPPORTED_LOCALES, t


def test_all_locales_have_the_same_keys():
    catalogs = {
        locale: json.loads((LOCALES_DIR / f"{locale}.json").read_text(encoding="utf-8"))
        for locale in SUPPORTED_LOCALES
    }
    reference = set(catalogs["en"])
    for locale, catalog in catalogs.items():
        assert set(catalog) == reference, f"{locale} keys differ from en"


def test_translates_with_params():
    assert t("errors.insufficient_credits", "ru", cost=4) == "Недостаточно кредитов: стоимость 4."
