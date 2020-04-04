from typing import Set, Dict

from pythongame.core.common import *
from pythongame.core.item_inventory import ItemEquipmentCategory

ITEM_ENTITY_SIZE = (30, 30)


class ItemData:
    def __init__(self, icon_sprite: UiIconSprite, entity_sprite: Sprite, base_name: str,
                 custom_description_lines: List[str],
                 base_stats: List[StatModifierInterval],
                 is_unique: bool,
                 item_equipment_category: Optional[ItemEquipmentCategory] = None):
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


_item_suffix_data_by_id: Dict[ItemSuffixId, ItemSuffixData] = {
    ItemSuffixId.MAX_HEALTH_1:
        ItemSuffixData("of Health", (1, 5),
                       [StatModifierInterval(HeroStat.MAX_HEALTH, int_interval(5, 15))]),
    ItemSuffixId.MAX_HEALTH_2:
        ItemSuffixData("of Vigor", (4, 9),
                       [StatModifierInterval(HeroStat.MAX_HEALTH, int_interval(15, 30))]),
    ItemSuffixId.HEALTH_REGEN_1:
        ItemSuffixData("of Rejuvenation", (1, 5),
                       [StatModifierInterval(HeroStat.HEALTH_REGEN, interval(0.2, 0.4, 0.1))]),
    ItemSuffixId.HEALTH_REGEN_2:
        ItemSuffixData("of Regrowth", (4, 9),
                       [StatModifierInterval(HeroStat.HEALTH_REGEN, interval(0.5, 1, 0.1))]),
    ItemSuffixId.MAX_MANA_1:
        ItemSuffixData("of Discipline", (1, 5),
                       [StatModifierInterval(HeroStat.MAX_MANA, int_interval(10, 20))]),
    ItemSuffixId.MAX_MANA_2:
        ItemSuffixData("of Resolve", (4, 9),
                       [StatModifierInterval(HeroStat.MAX_MANA, int_interval(20, 40))]),
    ItemSuffixId.MANA_REGEN_1:
        ItemSuffixData("of Focus", (1, 5),
                       [StatModifierInterval(HeroStat.MANA_REGEN, interval(0.2, 0.4, 0.1))]),
    ItemSuffixId.MANA_REGEN_2:
        ItemSuffixData("of Presence", (4, 9),
                       [StatModifierInterval(HeroStat.MANA_REGEN, interval(0.4, 0.8, 0.1))]),
    ItemSuffixId.MOVEMENT_SPEED:
        ItemSuffixData("of Swiftness", (1, 9),
                       [StatModifierInterval(HeroStat.MOVEMENT_SPEED, interval(0.05, 0.15, 0.01))]),
    ItemSuffixId.LIFE_STEAL:
        ItemSuffixData("of Leeching", (1, 9),
                       [StatModifierInterval(HeroStat.LIFE_STEAL, interval(0.02, 0.06, 0.01))]),
    ItemSuffixId.DAMAGE_1:
        ItemSuffixData("of Power", (1, 5),
                       [StatModifierInterval(HeroStat.DAMAGE, interval(0.02, 0.06, 0.01))]),
    ItemSuffixId.DAMAGE_2:
        ItemSuffixData("of Might", (4, 9),
                       [StatModifierInterval(HeroStat.DAMAGE, interval(0.05, 0.1, 0.01))]),
    ItemSuffixId.PHYSICAL_DAMAGE_1:
        ItemSuffixData("of Reckoning", (1, 5),
                       [StatModifierInterval(HeroStat.PHYSICAL_DAMAGE, interval(0.03, 0.08, 0.01))]),
    ItemSuffixId.PHYSICAL_DAMAGE_2:
        ItemSuffixData("of Destruction", (4, 9),
                       [StatModifierInterval(HeroStat.PHYSICAL_DAMAGE, interval(0.08, 0.15, 0.01))]),
    ItemSuffixId.MAGIC_DAMAGE_1:
        ItemSuffixData("of Wizardry", (1, 5),
                       [StatModifierInterval(HeroStat.MAGIC_DAMAGE, interval(0.03, 0.08, 0.01))]),
    ItemSuffixId.MAGIC_DAMAGE_2:
        ItemSuffixData("of Chaos", (4, 9),
                       [StatModifierInterval(HeroStat.MAGIC_DAMAGE, interval(0.08, 0.15, 0.01))]),
    ItemSuffixId.MAGIC_RESIST:
        ItemSuffixData("of Spirits", (1, 9),
                       [StatModifierInterval(HeroStat.MAGIC_RESIST_CHANCE, interval(0.08, 0.15, 0.01))]),
    ItemSuffixId.DODGE_CHANCE:
        ItemSuffixData("of Evasion", (1, 9),
                       [StatModifierInterval(HeroStat.DODGE_CHANCE, interval(0.03, 0.06, 0.01))]),
    ItemSuffixId.BLOCK_CHANCE:
        ItemSuffixData("of Confidence", (1, 9),
                       [StatModifierInterval(HeroStat.BLOCK_CHANCE, interval(0.04, 0.08, 0.01))]),
    ItemSuffixId.MOVEMENT_IMPAIR_IMMUNE:
        ItemSuffixData("of Persistence", (1, 9),
                       [StatModifierInterval(HeroStat.MOVEMENT_IMPAIRING_RESIST_CHANCE, [1])]),
    ItemSuffixId.INCREASED_LOOT_MONEY:
        ItemSuffixData("of Greed", (1, 9),
                       [StatModifierInterval(HeroStat.INCREASED_LOOT_MONEY_CHANCE, interval(0.25, 0.35, 0.01))]),
    ItemSuffixId.MANA_ON_KILL:
        ItemSuffixData("of Sadism", (1, 9), [StatModifierInterval(HeroStat.MANA_ON_KILL, [1])]),
    ItemSuffixId.LIFE_ON_KILL_1:
        ItemSuffixData("of Fury", (1, 5), [StatModifierInterval(HeroStat.LIFE_ON_KILL, int_interval(1, 2))]),
    ItemSuffixId.LIFE_ON_KILL_2:
        ItemSuffixData("of Madness", (4, 9), [StatModifierInterval(HeroStat.LIFE_ON_KILL, int_interval(2, 4))]),

}


class DescriptionLine:
    def __init__(self, text: str, from_suffix: bool = False):
        self.text = text
        self.from_suffix = from_suffix

    def __repr__(self):
        return self.text


def create_item_description(item_id: ItemId) -> List[DescriptionLine]:
    data = get_item_data_by_type(item_id.item_type)
    lines = []
    if item_id.base_stats:
        for modifier in item_id.base_stats:
            lines.append(DescriptionLine(modifier.get_description()))
    lines += [DescriptionLine(line) for line in data.custom_description_lines]
    if item_id.suffix_id:
        for modifier in item_id.suffix_stats:
            lines.append(DescriptionLine(modifier.get_description(), from_suffix=True))
    return lines


def create_item_description_for_type(item_type: ItemType) -> List[str]:
    data = get_item_data_by_type(item_type)
    lines = []
    if data.base_stats:
        for modifier in data.base_stats:
            lines.append(modifier.get_interval_description())
    lines += data.custom_description_lines
    return lines


def build_item_name(item_id: ItemId) -> str:
    data = get_item_data_by_type(item_id.item_type)
    name = data.base_name
    if item_id.suffix_id:
        name += " " + get_item_suffix_data(item_id.suffix_id).name_suffix
    return name


def register_item_data(item_type: ItemType, item_data: ItemData):
    _item_data_by_type[item_type] = item_data


def get_item_data(item_id: ItemId) -> ItemData:
    item_type = item_id.item_type
    return _item_data_by_type[item_type]


def get_item_data_by_type(item_type: ItemType) -> ItemData:
    return _item_data_by_type[item_type]


def get_item_suffix_data(item_suffix_id: ItemSuffixId) -> ItemSuffixData:
    return _item_suffix_data_by_id[item_suffix_id]


def get_item_suffixes_at_level(level: int) -> List[ItemSuffixId]:
    return [id for id in ItemSuffixId
            if _item_suffix_data_by_id[id].level_interval[0] <= level <= _item_suffix_data_by_id[id].level_interval[1]]


def randomized_item_id(item_type: ItemType) -> ItemId:
    data = get_item_data_by_type(item_type)
    return ItemId.randomized_base(item_type, data.base_stats)


def randomized_suffixed_item_id(item_type: ItemType, suffix_id: ItemSuffixId) -> ItemId:
    data = get_item_data_by_type(item_type)
    suffix_stats = get_item_suffix_data(suffix_id).stats
    return ItemId.randomized_with_suffix(item_type, data.base_stats, suffix_id, suffix_stats)


def random_rare_item(item_level: int) -> ItemId:
    item_type = random.choice([i for i in get_items_with_level(item_level) if not get_item_data_by_type(i).is_unique])
    suffixes_at_level = get_item_suffixes_at_level(item_level)
    if suffixes_at_level:
        suffix_id = random.choice(suffixes_at_level)
    else:
        print("WARN: No item suffix available for level " + str(item_level) + ". Falling back to random suffix.")
        suffix_id = random.choice([suffix_id for suffix_id in ItemSuffixId])
    return randomized_suffixed_item_id(item_type, suffix_id)


def plain_item_id(item_type: ItemType) -> ItemId:
    data = get_item_data_by_type(item_type)
    if len(data.base_stats) > 0:
        raise Exception("Item %s has stats! Cannot create plain version!" % item_type)
    return ItemId(item_type, [], None, [])


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
