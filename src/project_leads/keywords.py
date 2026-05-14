from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Keyword:
    text: str
    weight: int
    group: str


KEYWORDS: tuple[Keyword, ...] = (
    Keyword("steel bridge", 4, "bridge"),
    Keyword("bridge", 3, "bridge"),
    Keyword("viaduct", 3, "bridge"),
    Keyword("railway", 3, "railway"),
    Keyword("highway", 3, "highway"),
    Keyword("port", 3, "port"),
    Keyword("wharf", 3, "port"),
    Keyword("tender", 3, "procurement"),
    Keyword("procurement", 3, "procurement"),
    Keyword("EPC", 3, "procurement"),
    Keyword("桥梁", 3, "bridge"),
    Keyword("钢桥", 4, "bridge"),
    Keyword("钢结构", 3, "steel_structure"),
    Keyword("铁路", 3, "railway"),
    Keyword("公路", 3, "highway"),
    Keyword("港口", 3, "port"),
    Keyword("码头", 3, "port"),
    Keyword("招标", 3, "procurement"),
    Keyword("采购", 3, "procurement"),
)

PROJECT_TYPE_LABELS = {
    "bridge": "Bridge / 桥梁",
    "steel_structure": "Steel Structure / 钢结构",
    "railway": "Railway / 铁路",
    "highway": "Highway / 公路",
    "port": "Port / 港口",
    "procurement": "Tender / Procurement / 招采",
}

INFRA_GROUPS = {"bridge", "steel_structure", "railway", "highway", "port"}
PROCUREMENT_GROUPS = {"procurement"}


def match_keywords(text: str) -> list[Keyword]:
    haystack = text.lower()
    matches: list[Keyword] = []
    for keyword in KEYWORDS:
        needle = keyword.text.lower()
        if _contains_keyword(haystack, needle):
            matches.append(keyword)
    return matches


def _contains_keyword(haystack: str, needle: str) -> bool:
    if all(char.isascii() and (char.isalnum() or char.isspace()) for char in needle):
        pattern = r"(?<![a-z0-9])" + re.escape(needle).replace(r"\ ", r"\s+") + r"(?![a-z0-9])"
        return re.search(pattern, haystack, flags=re.IGNORECASE) is not None
    return needle in haystack


def score_text(text: str) -> tuple[int, list[Keyword]]:
    matches = match_keywords(text)
    score = sum(keyword.weight for keyword in matches)
    return score, matches


def relevance_level(text: str) -> tuple[str | None, list[Keyword]]:
    score, matches = score_text(text)
    groups = {keyword.group for keyword in matches}

    if not matches:
        return None, []
    if score >= 8 or (groups & INFRA_GROUPS and groups & PROCUREMENT_GROUPS):
        return "High", matches
    if score >= 4:
        return "Medium", matches
    return "Low", matches


def detect_project_type(text: str, fallback_category: str = "") -> str:
    _, matches = score_text(text)
    groups = [keyword.group for keyword in matches if keyword.group != "procurement"]
    if groups:
        return PROJECT_TYPE_LABELS.get(groups[0], groups[0])

    procurement_match = next((keyword.group for keyword in matches), "")
    if procurement_match:
        return PROJECT_TYPE_LABELS.get(procurement_match, procurement_match)

    return fallback_category or "General"


def follow_up_advice(level: str, matched_keywords: list[Keyword], source_name: str) -> str:
    keyword_text = ", ".join(dict.fromkeys(keyword.text for keyword in matched_keywords))
    if level == "High":
        return f"优先核实招标文件、业主联系人和截止日期；关键词：{keyword_text}。"
    if level == "Medium":
        return f"建议人工复核项目范围，并确认是否有桥梁/钢结构/交通港口相关标段；来源：{source_name}。"
    return f"保留观察，后续用更具体关键词复查；来源：{source_name}。"
