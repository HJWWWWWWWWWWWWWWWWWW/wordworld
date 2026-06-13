"""Upgrade technique_data.py: tier differentiation, pricing, effect scaling.
Counts position within each element group to assign tiers.
"""
import re

with open('src/wordworld/data/technique_data.py', 'r', encoding='utf-8') as f:
    content = f.read()

price_map = {
    'refined': (500, 250),
    'spirit': (1500, 750),
    'treasure': (3000, 1500),
    'earth': (6000, 3000),
    'heaven': (12000, 6000),
}

effect_mult = {
    'refined': 1.0,
    'spirit': 1.3,
    'treasure': 1.6,
    'earth': 2.0,
    'heaven': 2.5,
}

tier_pct_bonus = {
    'refined': 0,
    'spirit': 5,
    'treasure': 10,
    'earth': 15,
    'heaven': 20,
}

# Tier distribution per element: 6 refined, 6 spirit, 5 treasure, 3 earth
Tier_DIST = (
    ['refined'] * 6 +
    ['spirit'] * 6 +
    ['treasure'] * 5 +
    ['earth'] * 3
)


def upgrade_block(match) -> str:
    """Upgrade a single technique dict block, using position counter."""
    global elem_counter, current_element

    block = match.group(0)
    id_match = re.search(r'"id":\s*"(tech_\w+)"', block)
    if not id_match:
        return block

    tech_id = id_match.group(1)
    # Extract element from id: tech_火_焚天诀 -> 火
    parts = tech_id.split('_')
    if len(parts) < 2:
        return block
    elem = parts[1]

    # Reset counter when element changes
    if elem != current_element:
        current_element = elem
        elem_counter = 0

    # Assign tier based on position within element group
    new_tier = Tier_DIST[min(elem_counter, len(Tier_DIST) - 1)]
    elem_counter += 1

    # Update tier
    block = re.sub(r'"tier":\s*"\w+"', f'"tier": "{new_tier}"', block)

    # Update prices
    buy, sell = price_map[new_tier]
    block = re.sub(r'"price_buy":\s*\d+', f'"price_buy": {buy}', block)
    block = re.sub(r'"price_sell":\s*\d+', f'"price_sell": {sell}', block)

    # Enhance effects
    mult = effect_mult[new_tier]
    pct_extra = tier_pct_bonus[new_tier]

    effect_match = re.search(r'"effect":\s*"([^"]*)"', block)
    if effect_match:
        effect_str = effect_match.group(1)
        new_parts = []
        for token in effect_str.split(','):
            token = token.strip()
            if not token:
                continue
            em = re.match(r'^([a-z_]+):\+(\d+)(%?)$', token)
            if em:
                stat = em.group(1)
                val = int(em.group(2))
                is_pct = em.group(3) == '%'
                if is_pct:
                    new_val = val + pct_extra
                else:
                    new_val = max(1, int(val * mult))
                suffix = '%' if is_pct else ''
                new_parts.append(f'{stat}:+{new_val}{suffix}')
            else:
                new_parts.append(token)
        new_effect = ', '.join(new_parts)
        block = block.replace(f'"{effect_str}"', f'"{new_effect}"')

    return block


# Track position within element group
current_element = None
elem_counter = 0

# Match each technique dict entry
pattern = r'\{\s*"id":\s*"tech_\w+".*?\},'
content = re.sub(pattern, upgrade_block, content, flags=re.DOTALL)

with open('src/wordworld/data/technique_data.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done upgrading techniques.')
