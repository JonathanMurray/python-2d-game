from typing import Set, Dict, Tuple

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
    ItemSuffixId.VITALITY:
        ItemSuffixData("of Vitality",
                       [StatModifierInterval(HeroStat.MAX_HEALTH, int_interval(5, 10))]),
    ItemSuffixId.REGROWTH:
        ItemSuffixData("of Regrowth",
                       [StatModifierInterval(HeroStat.HEALTH_REGEN, interval(0.1, 0.4, 0.1))]),
    ItemSuffixId.DISCIPLINE:
        ItemSuffixData("of Discipline",
                       [StatModifierInterval(HeroStat.MAX_MANA, int_interval(5, 10))]),
    ItemSuffixId.FOCUS:
        ItemSuffixData("of Focus",
                       [StatModifierInterval(HeroStat.MANA_REGEN, interval(0.1, 0.4, 0.1))]),
    ItemSuffixId.SWIFTNESS:
        ItemSuffixData("of Swiftness",
                       [StatModifierInterval(HeroStat.MOVEMENT_SPEED, interval(0.05, 0.1, 0.01))]),
    ItemSuffixId.LEECHING:
        ItemSuffixData("of Leeching",
                       [StatModifierInterval(HeroStat.LIFE_STEAL, interval(0.03, 0.06, 0.01))]),
    ItemSuffixId.POWER:
        ItemSuffixData("of Power",
                       [StatModifierInterval(HeroStat.DAMAGE, interval(0.03, 0.06, 0.01))]),
    ItemSuffixId.RECKONING:
        ItemSuffixData("of Reckoning",
                       [StatModifierInterval(HeroStat.PHYSICAL_DAMAGE, interval(0.03, 0.06, 0.01))]),
    ItemSuffixId.WIZARDRY:
        ItemSuffixData("of Wizardry",
                       [StatModifierInterval(HeroStat.MAGIC_DAMAGE, interval(0.03, 0.06, 0.01))]),
    ItemSuffixId.SPIRITS:
        ItemSuffixData("of Spirits",
                       [StatModifierInterval(HeroStat.MAGIC_RESIST_CHANCE, interval(0.05, 0.1, 0.01))]),
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


def randomized_item_id(item_type: ItemType) -> ItemId:
    data = get_item_data_by_type(item_type)
    return ItemId.randomized_base(item_type, data.base_stats)


def randomized_rare_item_id(item_type: ItemType, suffix_id: ItemSuffixId) -> ItemId:
    data = get_item_data_by_type(item_type)
    suffix_stats = get_item_suffix_data(suffix_id).stats
    return ItemId.randomized_with_suffix(item_type, data.base_stats, suffix_id, suffix_stats)


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
