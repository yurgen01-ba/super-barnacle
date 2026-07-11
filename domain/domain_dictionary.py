from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class DomainTerm:
    canonical: str
    term_type: str
    ru_label: str
    en_label: str
    aliases: tuple[str, ...] = field(default_factory=tuple)
    description: str = ""


class DomainDictionary:
    """
    OrgMeter domain dictionary.

    The dictionary is the source of truth for canonical terms.
    LLM is not allowed to invent translations or new domain entities.
    """

    def __init__(self):
        self.terms: dict[str, DomainTerm] = {
            "Advance": DomainTerm(
                canonical="Advance",
                term_type="entity",
                ru_label="кредит / Advance",
                en_label="Advance",
                aliases=("advance", "credit", "mca", "mca advance", "loan", "адванс", "кредит"),
                description="Merchant Cash Advance / financing record.",
            ),
            "Merchant": DomainTerm(
                canonical="Merchant",
                term_type="actor",
                ru_label="мерчант / заемщик",
                en_label="Merchant",
                aliases=("merchant", "borrower", "мерчант", "заемщик", "заёмщик"),
                description="Business receiving financing.",
            ),
            "Funder": DomainTerm(
                canonical="Funder",
                term_type="actor",
                ru_label="кредитор / funder",
                en_label="Funder",
                aliases=("funder", "lender", "фандер", "кредитор", "fundr"),
                description="Party providing financing.",
            ),
            "ISO": DomainTerm(
                canonical="ISO",
                term_type="actor",
                ru_label="ISO / партнерская организация",
                en_label="ISO",
                aliases=("iso", "исо", "изо", "partner organization"),
                description="Partner organization involved in merchant acquisition.",
            ),
            "Referrer": DomainTerm(
                canonical="Referrer",
                term_type="actor",
                ru_label="реферер / referral partner",
                en_label="Referrer",
                aliases=("referrer", "реферер", "рефер", "referral partner"),
                description="Referral partner.",
            ),
            "Syndicator": DomainTerm(
                canonical="Syndicator",
                term_type="actor",
                ru_label="синдикатор / funding participant",
                en_label="Syndicator",
                aliases=("syndicator", "синдикатор", "participant"),
                description="Participant in funding.",
            ),
            "Underwriter": DomainTerm(
                canonical="Underwriter",
                term_type="actor",
                ru_label="андеррайтер",
                en_label="Underwriter",
                aliases=("underwriter", "андеррайтер", "underwriting"),
                description="Role responsible for review and underwriting.",
            ),
            "Draw": DomainTerm(
                canonical="Draw",
                term_type="entity",
                ru_label="draw / транш финансирования",
                en_label="Draw",
                aliases=("draw", "транш", "funding draw"),
                description="Funding draw under an Advance.",
            ),
            "Fee": DomainTerm(
                canonical="Fee",
                term_type="entity",
                ru_label="комиссия / fee",
                en_label="Fee",
                aliases=("fee", "комиссия", "fees"),
                description="Generic fee.",
            ),
            "Bounce Fee": DomainTerm(
                canonical="Bounce Fee",
                term_type="entity",
                ru_label="комиссия за bounced payment",
                en_label="Bounce Fee",
                aliases=("bounce fee", "bounced fee", "баунс фи"),
                description="Fee for failed/bounced payment.",
            ),
            "Voluntary Payback": DomainTerm(
                canonical="Voluntary Payback",
                term_type="process",
                ru_label="добровольное погашение / Voluntary Payback",
                en_label="Voluntary Payback",
                aliases=("voluntary payback", "manual repayment", "добровольное погашение"),
                description="Manual/voluntary repayment process.",
            ),
            "Merchant Payback History": DomainTerm(
                canonical="Merchant Payback History",
                term_type="entity",
                ru_label="история погашений мерчанта",
                en_label="Merchant Payback History",
                aliases=("merchant payback history",),
                description="Merchant repayment history.",
            ),
            "Participation Payout History": DomainTerm(
                canonical="Participation Payout History",
                term_type="entity",
                ru_label="история выплат участникам",
                en_label="Participation Payout History",
                aliases=("participation payout history", "payout history"),
                description="Funding participant payout history.",
            ),
            "Equifax": DomainTerm(
                canonical="Equifax",
                term_type="integration",
                ru_label="Equifax",
                en_label="Equifax",
                aliases=("equifax", "эквифакс"),
                description="External business report provider.",
            ),
            "Bizcap": DomainTerm(
                canonical="Bizcap",
                term_type="integration",
                ru_label="Bizcap",
                en_label="Bizcap",
                aliases=("bizcap", "бизкап"),
                description="External lender/funder integration.",
            ),
            "Pipeline": DomainTerm(
                canonical="Pipeline",
                term_type="process",
                ru_label="пайплайн",
                en_label="Pipeline",
                aliases=("pipeline", "пайплайн"),
                description="Operational pipeline / workflow view.",
            ),
            "Funder Migration": DomainTerm(
                canonical="Funder Migration",
                term_type="process",
                ru_label="миграция кредитора / funder migration",
                en_label="Funder Migration",
                aliases=("funder migration", "switch funder", "change funder", "migration"),
                description="Changing or migrating funder configuration.",
            ),
            "Underwriting": DomainTerm(
                canonical="Underwriting",
                term_type="process",
                ru_label="андеррайтинг",
                en_label="Underwriting",
                aliases=("underwriting", "review", "approval", "андеррайтинг"),
                description="Review and approval process.",
            ),
            "Payback Allocation": DomainTerm(
                canonical="Payback Allocation",
                term_type="process",
                ru_label="распределение погашений",
                en_label="Payback Allocation",
                aliases=("payback allocation", "allocation", "repayment allocation"),
                description="Allocation of repayment/payback amounts.",
            ),
        }
        self.alias_index = self._build_alias_index()

    def _build_alias_index(self) -> dict[str, str]:
        index = {}
        for canonical, term in self.terms.items():
            index[canonical.lower()] = canonical
            for alias in term.aliases:
                index[alias.lower()] = canonical
        return index

    def resolve_text(self, text: str) -> list[DomainTerm]:
        text_l = (text or "").lower()
        resolved = []
        seen = set()

        for alias, canonical in self.alias_index.items():
            if alias and alias in text_l and canonical not in seen:
                resolved.append(self.terms[canonical])
                seen.add(canonical)

        return resolved

    def get(self, canonical: str) -> DomainTerm | None:
        return self.terms.get(canonical)

    def canonical_labels_for_prompt(self) -> str:
        lines = []
        for term in self.terms.values():
            aliases = ", ".join(term.aliases[:8])
            lines.append(f"- {term.canonical} ({term.term_type}): ru='{term.ru_label}', aliases=[{aliases}]")
        return "\n".join(lines)


domain_dictionary = DomainDictionary()
