"""Validated access to the rendered project's governance rules."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class GovernanceRulesError(ValueError):
    """The governance rules file cannot safely drive enforcement."""


def _string_list(data: dict[str, Any], key: str) -> tuple[str, ...]:
    value = data.get(key)
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item for item in value
    ):
        raise GovernanceRulesError(
            f"governance-rules.yaml field '{key}' must be a list of non-empty strings"
        )
    return tuple(value)


def _prohibited_markers(data: dict[str, Any]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    prohibited = data.get("prohibited_markers")
    if not isinstance(prohibited, dict):
        raise GovernanceRulesError(
            "governance-rules.yaml field 'prohibited_markers' must be a mapping"
        )
    surfaces = _string_list(prohibited, "surfaces")
    pairs = prohibited.get("pattern_pairs")
    if not isinstance(pairs, list) or not pairs:
        raise GovernanceRulesError(
            "governance-rules.yaml field 'prohibited_markers.pattern_pairs' "
            "must be a non-empty list"
        )
    markers = tuple(_marker_from_pair(pair, index) for index, pair in enumerate(pairs))
    return surfaces, markers


def _marker_from_pair(pair: object, index: int) -> str:
    if not (
        isinstance(pair, list)
        and len(pair) == 2
        and all(isinstance(part, str) and part for part in pair)
    ):
        raise GovernanceRulesError(
            "governance-rules.yaml field "
            f"'prohibited_markers.pattern_pairs[{index}]' must contain "
            "two non-empty strings"
        )
    return pair[0] + pair[1]


@dataclass(frozen=True)
class GovernanceRules:
    required_files: tuple[str, ...]
    optional_dirs: tuple[str, ...]
    required_agents: tuple[str, ...]
    required_skills: tuple[str, ...]
    marker_surfaces: tuple[str, ...]
    markers: tuple[str, ...]

    @classmethod
    def load(cls, root: Path) -> GovernanceRules:
        path = root / "governance-rules.yaml"
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise GovernanceRulesError(f"cannot read governance-rules.yaml: {exc}") from exc
        except (UnicodeDecodeError, yaml.YAMLError) as exc:
            raise GovernanceRulesError(f"invalid governance-rules.yaml: {exc}") from exc
        if not isinstance(raw, dict):
            raise GovernanceRulesError("governance-rules.yaml must contain a mapping")

        surfaces, markers = _prohibited_markers(raw)

        return cls(
            required_files=_string_list(raw, "required_files"),
            optional_dirs=_string_list(raw, "optional_dirs"),
            required_agents=_string_list(raw, "required_agents"),
            required_skills=_string_list(raw, "required_skills"),
            marker_surfaces=surfaces,
            markers=markers,
        )
