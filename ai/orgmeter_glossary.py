from __future__ import annotations

import re


ORG_METER_CANONICAL_TERMS = {
    "offer": ["офер", "оффер", "оферсент", "offersent"],
    "contract": ["контракт", "контракцент", "контрактцент", "contractcent"],
    "advance": ["адванс", "эдванс", "advance"],
    "merchant": ["мерчант", "merchant"],
    "funder": ["фандер", "фандра", "фангр", "fundr", "funder"],
    "internal funder": ["интерналл фангр", "internal funder"],
    "external funder": ["экстрамалл фангр", "external funder"],
    "ISO": ["айсо", "изо", "iso"],
    "referrer": ["рефер", "реферер", "referrer"],
    "syndicator": ["синдикатор", "syndicator"],
    "underwriter": ["андеррайтер", "underwriter"],
    "commission": ["комиссия", "commission"],
    "fee": ["фи", "fee"],
    "bounce fee": ["баунс фи", "bounce fee"],
    "voluntary payback": ["волонтари пэйбек", "voluntary payback"],
    "participation payout history": ["participation payout history", "партисипейшн payout history"],
    "merchant payback history": ["merchant payback history", "мерчант payback history"],
    "pipeline": ["пайплайн", "pipeline"],
    "Equifax": ["эквифакс", "equifax"],
    "Bizcap": ["бизкап", "bizcap"],
    "BRC": ["брс", "brc"],
    "LLC": ["элэлси", "llc"],
    "LC count": ["lc count", "элси каунт"],
}

NOISE_REPLACEMENTS = {
    "речьек": "rejected",
    "совосились": "approved",
    "ферфлайс": "fee rules",
    "элосии": "allocation",
    "дэйли": "daily",
    "климансли": "weekly/monthly",
}


def repair_orgmeter_terms(text: str) -> str:
    if not text:
        return ""

    repaired = str(text)

    for canonical, variants in ORG_METER_CANONICAL_TERMS.items():
        for variant in variants:
            repaired = re.sub(
                rf"\b{re.escape(variant)}\b",
                canonical,
                repaired,
                flags=re.IGNORECASE,
            )

    for wrong, replacement in NOISE_REPLACEMENTS.items():
        repaired = re.sub(
            rf"\b{re.escape(wrong)}\b",
            replacement,
            repaired,
            flags=re.IGNORECASE,
        )

    repaired = re.sub(r"\s+", " ", repaired).strip()
    return repaired


def contains_orgmeter_domain_terms(text: str) -> bool:
    text_l = (text or "").lower()
    terms = set(ORG_METER_CANONICAL_TERMS.keys())
    terms.update(variant.lower() for variants in ORG_METER_CANONICAL_TERMS.values() for variant in variants)
    return any(term.lower() in text_l for term in terms)
