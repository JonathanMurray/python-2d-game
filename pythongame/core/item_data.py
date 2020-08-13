from typing import Set, Dict

from pythongame.core.common import *
from pythongame.core.item_inventory import ItemEquipmentCategory

ITEM_ENTITY_SIZE = (30, 30)


class ItemData:
    def __init__(self, icon_sprite: UiIconSprite, entity_sprite: Sprite, base_name: str,
                 custom_description_lines: List[str],
                 base_stats: List[StatModifierInterval],
                 is_unique: bool,
                 item_equipment_category: Optional[ItemEquipmentCategory] = None,
                 active_ability_type: Optional[AbilityType] = None):
        self.icon_sprite = icon_sprite
        self.entity_sprite = entity_sprite
        self.base_name = base_name
        self.custom_description_lines: List[str] = custom_description_lines
        self.base_stats = base_stats
        # "unique" means: when this item drops as loot, it cannot receive suffixes.
        # Other items drop as either "common" or "rare", but this one is always the same "unique"
        # "unique" items are also rendered differently in the inventory
        self.is_unique = is_unique
        self.item_equipment_category = item_equipment_category  # If category is None, the item can't be equipped
        self.active_ability_type: Optional[AbilityType] = active_ability_type  # Some items give abilities when equipped

    def __repr__(self):
        return "ItemData(%s)" % self.base_name


_item_data_by_type: Dict[ItemType, ItemData] = {}
_item_types_grouped_by_level: Dict[int, Set[ItemType]] = {}
_item_levels: Dict[ItemType, int] = {}


def int_interval(min_inclusive: int, max_inclusive: int):
    return list(range(min_inclusive, max_inclusive + 1))


def interval(min_inclusive: Union[int, float], max_inclusive: Union[int, float], step: Union[int, float]):
    result = []
    value = min_inclusive
    while value <= max_inclusive:
        result.append(value)
        value += step
    return result


_item_affix_data_by_id: Dict[ItemAffixId, ItemSuffixData] = {
    ItemAffixId.MAX_HEALTH_1:
        ItemSuffixData("Healthy", "of Health", (1, 5),
                       [StatModifierInterval(HeroStat.MAX_HEALTH, int_interval(5, 15))]),
    ItemAffixId.MAX_HEALTH_2:
        ItemSuffixData("Vigorous", "of Vigor", (4, 9),
                       [StatModifierInterval(HeroStat.MAX_HEALTH, int_interval(15, 30))]),
    ItemAffixId.HEALTH_REGEN_1:
        ItemSuffixData(None, "of Rejuvenation", (1, 5),
                       [StatModifierInterval(HeroStat.HEALTH_REGEN, interval(0.2, 0.4, 0.1))]),
    ItemAffixId.HEALTH_REGEN_2:
        ItemSuffixData(None, "of Regrowth", (4, 9),
                       [StatModifierInterval(HeroStat.HEALTH_REGEN, interval(0.6, 1.5, 0.1))]),
    ItemAffixId.MAX_MANA_1:
        ItemSuffixData("Strange", "of Discipline", (1, 5),
                       [StatModifierInterval(HeroStat.MAX_MANA, int_interval(10, 20))]),
    ItemAffixId.MAX_MANA_2:
        ItemSuffixData("Mystic", "of Resolve", (4, 9),
                       [StatModifierInterval(HeroStat.MAX_MANA, int_interval(20, 40))]),
    ItemAffixId.MANA_REGEN_1:
        ItemSuffixData(None, "of Focus", (1, 5),
                       [StatModifierInterval(HeroStat.MANA_REGEN, interval(0.2, 0.4, 0.1))]),
    ItemAffixId.MANA_REGEN_2:
        ItemSuffixData(None, "of Presence", (4, 9),
                       [StatModifierInterval(HeroStat.MANA_REGEN, interval(0.4, 0.8, 0.1))]),
    ItemAffixId.MOVEMENT_SPEED:
        ItemSuffixData("Quick", "of Swiftness", (1, 9),
                       [StatModifierInterval(HeroStat.MOVEMENT_SPEED, interval(0.08, 0.2, 0.01))]),
    ItemAffixId.LIFE_STEAL:
        ItemSuffixData("Vampire", "of Leeching", (1, 9),
                       [StatModifierInterval(HeroStat.LIFE_STEAL, interval(0.02, 0.06, 0.01))]),
    ItemAffixId.DAMAGE_1:
        ItemSuffixData("Powerful", None, (1, 5),
                       [StatModifierInterval(HeroStat.DAMAGE, interval(0.04, 0.08, 0.01))]),
    ItemAffixId.DAMAGE_2:
        ItemSuffixData("Mighty", None, (4, 9),
                       [StatModifierInterval(HeroStat.DAMAGE, interval(0.09, 0.13, 0.01))]),
    ItemAffixId.PHYSICAL_DAMAGE_1:
        ItemSuffixData("Reckless", None, (1, 5),
                       [StatModifierInterval(HeroStat.PHYSICAL_DAMAGE, interval(0.05, 0.1, 0.01))]),
    ItemAffixId.PHYSICAL_DAMAGE_2:
        ItemSuffixData("Destructive", None, (4, 9),
                       [StatModifierInterval(HeroStat.PHYSICAL_DAMAGE, interval(0.11, 0.18, 0.01))]),
    ItemAffixId.MAGIC_DAMAGE_1:
        ItemSuffixData("Arcane", None, (1, 5),
                       [StatModifierInterval(HeroStat.MAGIC_DAMAGE, interval(0.05, 0.1, 0.01))]),
    ItemAffixId.MAGIC_DAMAGE_2:
        ItemSuffixData("Chaotic", None, (4, 9),
                       [StatModifierInterval(HeroStat.MAGIC_DAMAGE, interval(0.11, 0.18, 0.01))]),
    ItemAffixId.MAGIC_RESIST:
        ItemSuffixData("Spirituous", "of Spirits", (1, 9),
                       [StatModifierInterval(HeroStat.MAGIC_RESIST_CHANCE, interval(0.08, 0.15, 0.01))]),
    ItemAffixId.DODGE_CHANCE:
        ItemSuffixData(None, "of Evasion", (1, 9),
                       [StatModifierInterval(HeroStat.DODGE_CHANCE, interval(0.03, 0.06, 0.01))]),
    ItemAffixId.BLOCK_CHANCE:
        ItemSuffixData(None, "of Confidence", (1, 9),
                       [StatModifierInterval(HeroStat.BLOCK_CHANCE, interval(0.04, 0.08, 0.01))]),
    ItemAffixId.MOVEMENT_IMPAIR_IMMUNE:
        ItemSuffixData(None, "of Persistence", (1, 9),
                       [StatModifierInterval(HeroStat.MOVEMENT_IMPAIRING_RESIST_CHANCE, [1])]),
    ItemAffixId.INCREASED_LOOT_MONEY:
        ItemSuffixData(None, "of Greed", (1, 9),
                       [StatModifierInterval(HeroStat.INCREASED_LOOT_MONEY_CHANCE, interval(0.25, 0.35, 0.01))]),
    ItemAffixId.MANA_ON_KILL:
        ItemSuffixData("Sadist", "of Sadism", (1, 9), [StatModifierInterval(HeroStat.MANA_ON_KILL, [1])]),
    ItemAffixId.LIFE_ON_KILL_1:
        ItemSuffixData("Furious", "of Fury", (1, 5), [StatModifierInterval(HeroStat.LIFE_ON_KILL, int_interval(1, 2))]),
    ItemAffixId.LIFE_ON_KILL_2:
        ItemSuffixData("Mad", "of Madness", (4, 9), [StatModifierInterval(HeroStat.LIFE_ON_KILL, int_interval(2, 4))]),
    ItemAffixId.INCREASED_LOOT_RARE_OR_UNIQUE_CHANCE:
        ItemSuffixData(None, "of Discovery", (1, 9),
                       [StatModifierInterval(HeroStat.INCREASED_LOOT_RARE_OR_UNIQUE_CHANCE,
                                             interval(0.15, 0.25, 0.01))]),

}


class DescriptionLine:
    def __init__(self, text: str, from_affix: bool = False):
        self.text = text
        self.from_affix = from_affix

    def __repr__(self):
        return self.text


def create_item_description(item_id: ItemId) -> List[DescriptionLine]:
    data = get_item_data_by_type(item_id.item_type)
    lines = []
    if item_id.base_stats:
        for modifier in item_id.base_stats:
            lines.append(DescriptionLine(modifier.get_description()))
    lines += [DescriptionLine(line) for line in data.custom_description_lines]
    for modifier in item_id.affix_stats:
        lines.append(DescriptionLine(modifier.get_description(), from_affix=True))
    return lines


def create_item_description_for_type(item_type: ItemType) -> List[str]:
    data = get_item_data_by_type(item_type)
    lines = []
    if data.base_stats:
        for modifier in data.base_stats:
            lines.append(modifier.get_interval_description())
    lines += data.custom_description_lines
    return lines


def _build_item_name(item_type: ItemType, prefix: Optional[ItemAffixId],
                     suffix: Optional[ItemAffixId]) -> str:
    data = get_item_data_by_type(item_type)
    name = ""
    if prefix:
        name += get_item_affix_data(prefix).name_prefix + " "
    name += data.base_name
    if suffix:
        name += " " + get_item_affix_data(suffix).name_suffix
    return name


def register_item_data(item_type: ItemType, item_data: ItemData):
    _item_data_by_type[item_type] = item_data


def get_item_data(item_id: ItemId) -> ItemData:
    item_type = item_id.item_type
    return _item_data_by_type[item_type]


def get_item_data_by_type(item_type: ItemType) -> ItemData:
    return _item_data_by_type[item_type]


def get_item_affix_data(affix_id: ItemAffixId) -> ItemSuffixData:
    return _item_affix_data_by_id[affix_id]


def get_item_affixes_at_level(level: int) -> List[ItemAffixId]:
    return [item_id for item_id in ItemAffixId
            if _item_affix_data_by_id[item_id].level_interval[0]
            <= level
            <= _item_affix_data_by_id[item_id].level_interval[1]]


def randomized_item_id(item_type: ItemType) -> ItemId:
    data = get_item_data_by_type(item_type)
    name = _build_item_name(item_type, None, None)
    return ItemId.randomized_base(item_type, name, data.base_stats)


def randomized_affixed_item_id(item_type: ItemType, prefix_id: Optional[ItemAffixId],
                               suffix_id: Optional[ItemAffixId]) -> ItemId:
    if prefix_id is None and suffix_id is None:
        raise Exception("Either prefix or suffix must be set!")
    data = get_item_data_by_type(item_type)
    affix_stats = []
    if prefix_id:
        affix_stats += get_item_affix_data(prefix_id).stats
    if suffix_id:
        affix_stats += get_item_affix_data(suffix_id).stats
    name = _build_item_name(item_type, prefix_id, suffix_id)
    return ItemId.randomized_with_affix(item_type, name, data.base_stats, affix_stats)


def random_item_one_affix(item_level: int) -> ItemId:
    item_type = random.choice([i for i in get_items_with_level(item_level) if not get_item_data_by_type(i).is_unique])
    affixes_at_level = get_item_affixes_at_level(item_level)
    if affixes_at_level:
        affix_id = random.choice(affixes_at_level)
    else:
        print("WARN: No item affix available for level " + str(item_level) + ". Falling back to random affix.")
        affix_id = random.choice([affix_id for affix_id in ItemAffixId])

    prefix_id = None
    suffix_id = None
    data = get_item_affix_data(affix_id)
    if data.name_prefix:
        prefix_id = affix_id
    else:
        suffix_id = affix_id
    return randomized_affixed_item_id(item_type, prefix_id, suffix_id)


def random_item_two_affixes(item_level: int) -> ItemId:
    item_type = random.choice([i for i in get_items_with_level(item_level) if not get_item_data_by_type(i).is_unique])
    affixes_at_level = get_item_affixes_at_level(item_level)
    if not affixes_at_level:
        print("ERROR: No item affix available for level " + str(item_level) + ". Falling back to random prefix.")
        prefix_id = random.choice([affix_id for affix_id in ItemAffixId])
        return randomized_affixed_item_id(item_type, prefix_id, None)

    # Pick random prefix
    prefix_id = random.choice([affix_id for affix_id in affixes_at_level
                               if get_item_affix_data(affix_id).name_prefix])

    # pick random suffix that isn't identical to the prefix! (we don't want items like "Vigorous sword of Vigor")
    suffix_id = random.choice([affix_id for affix_id in affixes_at_level
                               if get_item_affix_data(affix_id).name_suffix
                               and affix_id != prefix_id])
    return randomized_affixed_item_id(item_type, prefix_id, suffix_id)


def plain_item_id(item_type: ItemType) -> ItemId:
    data = get_item_data_by_type(item_type)
    if len(data.base_stats) > 0:
        raise Exception("Item %s has stats! Cannot create plain version!" % item_type)
    return ItemId(item_type, data.base_name, [], [])


def register_item_level(item_type: ItemType, item_level: int):
    item_types = _item_types_grouped_by_level.setdefault(item_level, set())
    item_types.add(item_type)
    _item_levels[item_type] = item_level


def get_items_with_level(item_level: int) -> List[ItemType]:
    return list(_item_types_grouped_by_level.get(item_level, set()))


def get_items_within_levels(min_level: int, max_level: int) -> List[ItemType]:
    items = []
    for level in range(min_level, max_level + 1):
        items += get_items_with_level(level)
    return items


def get_optional_item_level(item_type: ItemType) -> Optional[int]:
    return _item_levels.get(item_type, None)


def get_items_with_category(category: Optional[ItemEquipmentCategory]) -> List[Tuple[ItemType, ItemData]]:
    return [(item_type, item_data)
            for (item_type, item_data) in _item_data_by_type.items()
            if item_data.item_equipment_category == category]
