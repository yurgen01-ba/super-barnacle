from __future__ import annotations

import re


DOMAIN_TERMS = {
    "джира": "Jira",
    "жира": "Jira",
    "джировский": "Jira",
    "джировский таск": "Jira task",
    "джировская": "Jira",
    "конфлюенс": "Confluence",
    "конфлюэнс": "Confluence",
    "оргметер": "OrgMeter",
    "орг метр": "OrgMeter",
    "бизкап": "Bizcap",
    "эквифакс": "Equifax",
    "адванс": "Advance",
    "эдванс": "Advance",
    "фандер": "Funder",
    "фандеры": "Funders",
    "андеррайтер": "Underwriter",
    "синдикатор": "Syndicator",
    "реферер": "Referrer",
    "мерчант": "Merchant",
    "мерчанда": "Merchant",
    "таск": "task",
    "застайск": "task",
    "таска": "task",
    "тикет": "ticket",
    "инфопанель": "info panel",
    "тайкло": "title",
    "финскопов": "field scope",
    "проблем": "problem",
    "скоуп": "scope",
    "спикер": "speaker",
    "саммари": "summary",
    "самари": "summary",
    "аккаунтс": "accounts",
    "экаунтс": "accounts",
}


COMMON_REPAIRS = {
    "сигнал над здесь": "signal not there",
    "за собушкой": "за задачей",
    "ничего не помиделся": "ничего не поменялось",
    "памец": "по мне",
    "тайдлов": "titles",
    "финскопов": "финскопов",
    "стаск": "task",
    "аж блю": "as-is blue",
    "ajblue": "as-is blue",
}


def apply_domain_glossary_repair(text: str) -> str:
    if not text:
        return ""

    repaired = str(text)

    for wrong, correct in COMMON_REPAIRS.items():
        repaired = re.sub(re.escape(wrong), correct, repaired, flags=re.IGNORECASE)

    for alias, canonical in DOMAIN_TERMS.items():
        repaired = re.sub(rf"\b{re.escape(alias)}\b", canonical, repaired, flags=re.IGNORECASE)

    repaired = re.sub(r"\s+", " ", repaired).strip()
    return repaired
