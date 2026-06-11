"""Procedural pixel-art icons for every item and equipment ID."""

from __future__ import annotations

import hashlib
import math
from typing import Any, Dict, Tuple

import pygame

from wordworld.data.equipment_data import EQUIPMENT_DATA

Color = Tuple[int, int, int]

TIER_COLORS: Dict[str, Color] = {
    "iron": (154, 160, 169), "refined": (91, 193, 133),
    "spirit": (82, 164, 232), "treasure": (174, 105, 232),
    "earth": (222, 151, 62), "heaven": (239, 209, 83),
    "mystic": (71, 222, 218), "saint": (245, 121, 183),
    "emperor": (246, 86, 74), "divine": (255, 244, 190),
}
_ICON_CACHE: Dict[Tuple[str, int, bool], pygame.Surface] = {}


def visual_signature(item_id: str) -> int:
    """Return the stable 32-bit identity encoded into an icon's border."""
    return int.from_bytes(
        hashlib.blake2s(item_id.encode("utf-8"), digest_size=4).digest(), "big"
    )


def _mix(color: Color, other: Color, amount: float) -> Color:
    return tuple(
        max(0, min(255, int(value + (target - value) * amount)))
        for value, target in zip(color, other)
    )


def _family(item_id: str, rule: Dict[str, Any]) -> str:
    equipment = EQUIPMENT_DATA.get(item_id)
    if equipment:
        return str(equipment.get("subtype") or equipment.get("slot") or "equipment")
    text = " ".join(str(rule.get(key, "")).lower() for key in ("type", "name", "description", "use_effect"))
    groups = (
        ("pill", ("pill", "丹", "丸")),
        ("potion", ("potion", "water", "dew", "药剂", "露", "水")),
        ("herb", ("herb", "flower", "leaf", "草", "花", "叶")),
        ("crystal", ("ore", "stone", "crystal", "矿", "石", "晶")),
        ("scroll", ("scroll", "book", "map", "卷", "书", "图")),
        ("flame", ("fire", "flame", "火", "焰")),
        ("token", ("token", "coin", "silver", "令", "币", "银")),
        ("bomb", ("bomb", "powder", "dust", "弹", "粉", "散")),
    )
    return next((family for family, keys in groups if any(key in text for key in keys)), "relic")


def _weapon(surface: pygame.Surface, family: str, main: Color, accent: Color, seed: int) -> None:
    cx = cy = 16
    dark = _mix(main, (0, 0, 0), 0.55)
    if family in {"bow", "whip", "fan", "claw"}:
        pygame.draw.arc(surface, accent, (7, 7, 18, 18), 0.5, 4.8, 2)
        for offset in (-5, 0, 5):
            pygame.draw.line(surface, main, (cx - 4, cy + 6), (cx + offset, cy - 7), 1 if family == "fan" else 2)
        return
    pygame.draw.line(surface, dark, (cx - 7, cy + 8), (cx + 6, cy - 8), 4)
    pygame.draw.line(surface, main, (cx - 7, cy + 8), (cx + 6, cy - 8), 2)
    pygame.draw.polygon(surface, accent, [(cx + 6, cy - 9), (cx + 8, cy - 3), (cx + 2, cy - 5)])
    pygame.draw.line(surface, accent, (cx - 7, cy + 2), (cx, cy + 8), 2)
    if seed & 1:
        pygame.draw.circle(surface, accent, (cx + 5, cy - 6), 2)


def _equipment(surface: pygame.Surface, family: str, main: Color, accent: Color) -> None:
    cx = cy = 16
    dark = _mix(main, (0, 0, 0), 0.55)
    if family in {"ring", "bracelet"}:
        pygame.draw.circle(surface, dark, (cx, cy), 8, 4)
        pygame.draw.circle(surface, main, (cx, cy), 8, 2)
        pygame.draw.circle(surface, accent, (cx, cy - 8), 2)
    elif family in {"pendant", "jade", "amulet", "accessory"}:
        pygame.draw.line(surface, accent, (cx - 6, cy - 8), (cx, cy - 3), 1)
        pygame.draw.line(surface, accent, (cx + 6, cy - 8), (cx, cy - 3), 1)
        pygame.draw.polygon(surface, main, [(cx, cy - 5), (cx + 7, cy), (cx + 3, cy + 8), (cx - 3, cy + 8), (cx - 7, cy)])
        pygame.draw.circle(surface, accent, (cx, cy + 1), 2)
    elif family == "boots":
        pygame.draw.polygon(surface, main, [(9, 8), (15, 8), (16, 21), (24, 23), (9, 23)])
    elif family == "belt":
        pygame.draw.rect(surface, main, (7, 13, 18, 6))
        pygame.draw.rect(surface, accent, (13, 11, 6, 10), 2)
    elif family == "helmet":
        pygame.draw.polygon(surface, main, [(8, 23), (10, 12), (16, 7), (22, 12), (24, 23)])
        pygame.draw.line(surface, accent, (16, 8), (16, 21), 2)
    else:
        pygame.draw.polygon(surface, dark, [(7, 10), (12, 7), (16, 11), (20, 7), (25, 10), (22, 24), (10, 24)])
        pygame.draw.polygon(surface, main, [(9, 11), (13, 9), (16, 13), (19, 9), (23, 11), (20, 22), (12, 22)])
        pygame.draw.line(surface, accent, (16, 13), (16, 22), 2)


def _item(surface: pygame.Surface, family: str, main: Color, accent: Color, seed: int) -> None:
    cx = cy = 16
    dark = _mix(main, (0, 0, 0), 0.55)
    if family == "pill":
        pygame.draw.circle(surface, dark, (cx, cy), 8)
        pygame.draw.circle(surface, main, (cx, cy), 6)
        pygame.draw.arc(surface, accent, (11, 11, 10, 10), 0.2, 2.5, 2)
    elif family == "potion":
        pygame.draw.rect(surface, accent, (12, 7, 8, 4))
        pygame.draw.polygon(surface, dark, [(11, 11), (8, 24), (24, 24), (21, 11)])
        pygame.draw.polygon(surface, main, [(12, 16), (10, 23), (22, 23), (20, 16)])
    elif family == "herb":
        pygame.draw.line(surface, accent, (16, 24), (16, 8), 2)
        for dx, dy in ((-5, -4), (5, -1), (-5, 2), (4, 5)):
            pygame.draw.ellipse(surface, main, (cx + dx - 3, cy + dy - 2, 6, 4))
    elif family == "crystal":
        pygame.draw.polygon(surface, dark, [(16, 7), (23, 14), (20, 24), (11, 23), (9, 14)])
        pygame.draw.polygon(surface, main, [(16, 9), (20, 15), (18, 22), (13, 21), (11, 15)])
        pygame.draw.line(surface, accent, (16, 10), (14, 20), 1)
    elif family == "scroll":
        pygame.draw.rect(surface, main, (9, 9, 14, 14))
        pygame.draw.circle(surface, accent, (9, 10), 3)
        pygame.draw.circle(surface, accent, (23, 22), 3)
        pygame.draw.line(surface, dark, (13, 14), (20, 14), 1)
        pygame.draw.line(surface, dark, (13, 18), (19, 18), 1)
    elif family == "flame":
        pygame.draw.polygon(surface, main, [(16, 7), (23, 16), (20, 24), (11, 24), (9, 16)])
        pygame.draw.polygon(surface, accent, [(17, 11), (20, 17), (16, 22), (12, 17)])
    elif family == "token":
        pygame.draw.circle(surface, dark, (cx, cy), 9)
        pygame.draw.circle(surface, main, (cx, cy), 7)
        pygame.draw.rect(surface, accent, (13, 13, 6, 6), 1)
    elif family == "bomb":
        pygame.draw.circle(surface, dark, (cx, cy + 2), 8)
        pygame.draw.circle(surface, main, (cx, cy + 2), 6)
        pygame.draw.line(surface, accent, (19, 11), (23, 7), 2)
        pygame.draw.circle(surface, accent, (24, 7), 2)
    else:
        sides = 5 + seed % 4
        points = [
            (cx + int(math.cos(-math.pi / 2 + i * math.tau / sides) * 8),
             cy + int(math.sin(-math.pi / 2 + i * math.tau / sides) * 8))
            for i in range(sides)
        ]
        pygame.draw.polygon(surface, dark, points)
        pygame.draw.polygon(surface, main, points, 2)
        pygame.draw.circle(surface, accent, (cx, cy), 2)


def _render_icon(item_id: str, rule: Dict[str, Any], size: int, selected: bool) -> pygame.Surface:
    seed = visual_signature(item_id)
    equipment = EQUIPMENT_DATA.get(item_id, {})
    tier = str(equipment.get("tier") or rule.get("tier") or "iron")
    main = TIER_COLORS.get(tier, TIER_COLORS["iron"])
    accent = _mix(main, ((seed >> 16) & 0xFF, (seed >> 8) & 0xFF, seed & 0xFF), 0.6)
    base = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.rect(base, _mix(main, (7, 8, 14), 0.82), (2, 2, 28, 28), border_radius=6)
    pygame.draw.rect(base, _mix(main, (255, 255, 255), 0.25), (2, 2, 28, 28), 1, border_radius=6)
    if selected:
        pygame.draw.rect(base, (*accent, 120), (0, 0, 32, 32), 3, border_radius=8)
    family = _family(item_id, rule)
    slot = equipment.get("slot")
    if slot == "weapon":
        _weapon(base, family, main, accent, seed)
    elif slot in {"armor", "accessory"}:
        _equipment(base, family, main, accent)
    else:
        _item(base, family, main, accent, seed)
    # The 32-bit border constellation is the item's unique visual identity.
    for bit in range(32):
        if (seed >> bit) & 1:
            edge, offset = bit // 8, 4 + (bit % 8) * 3
            point = ((offset, 2), (29, offset), (31 - offset, 29), (2, 31 - offset))[edge]
            base.set_at(point, (*accent, 255))
    return pygame.transform.scale(base, (size, size))


def item_icon(item_id: str, rule: Dict[str, Any], size: int = 24, selected: bool = False) -> pygame.Surface:
    """Return a cached icon surface for an item."""
    key = (item_id, size, selected)
    if key not in _ICON_CACHE:
        _ICON_CACHE[key] = _render_icon(item_id, rule, size, selected)
    return _ICON_CACHE[key]


def draw_item_icon(
    target: pygame.Surface, item_id: str, rule: Dict[str, Any],
    x: int, y: int, size: int = 24, selected: bool = False,
) -> None:
    target.blit(item_icon(item_id, rule, size, selected), (x, y))
