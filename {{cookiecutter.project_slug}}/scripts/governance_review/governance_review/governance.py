"""Validated access to the rendered project's governance rules."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class GovernanceRulesError(ValueError):
    """The governance rules file cannot safely drive enforcement."""


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

        def string_list(key: str) -> tuple[str, ...]:
            value = raw.get(key)
            if not isinstance(value, list) or not all(
                isinstance(item, str) and item for item in value
            ):
                raise GovernanceRulesError(
                    f"governance-rules.yaml field '{key}' must be a list of non-empty strings"
                )
            return tuple(value)

        prohibited: Any = raw.get("prohibited_markers")
        if not isinstance(prohibited, dict):
            raise GovernanceRulesError(
                "governance-rules.yaml field 'prohibited_markers' must be a mapping"
            )
        surfaces = prohibited.get("surfaces")
        if not isinstance(surfaces, list) or not all(
            isinstance(item, str) and item for item in surfaces
        ):
            raise GovernanceRulesError(
                "governance-rules.yaml field 'prohibited_markers.surfaces' "
                "must be a list of non-empty strings"
            )
        pairs = prohibited.get("pattern_pairs")
        if not isinstance(pairs, list) or not pairs:
            raise GovernanceRulesError(
                "governance-rules.yaml field 'prohibited_markers.pattern_pairs' "
                "must be a non-empty list"
            )
        markers: list[str] = []
        for index, pair in enumerate(pairs):
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
            markers.append(str(pair[0]) + str(pair[1]))

        return cls(
            required_files=string_list("required_files"),
            optional_dirs=string_list("optional_dirs"),
            required_agents=string_list("required_agents"),
            required_skills=string_list("required_skills"),
            marker_surfaces=tuple(surfaces),
            markers=tuple(markers),
        )
