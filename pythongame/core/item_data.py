from typing import Set, Dict, Tuple

from pythongame.core.common import *
from pythongame.core.item_inventory import ItemEquipmentCategory

ITEM_ENTITY_SIZE = (30, 30)


class ItemData:
    def __init__(self, icon_sprite: UiIconSprite, entity_sprite: Sprite, base_name: str,
                 custom_description_lines: List[str],
                 base_stats: List[StatModifierInterval],
                 item_equipment_category: Optional[ItemEquipmentCategory] = None):
        self.icon_sprite = icon_sprite
        self.entity_sprite = entity_sprite
        self.base_name = base_name
        self.custom_description_lines: List[str] = custom_description_lines
        self.base_stats = base_stats
        self.item_equipment_category = item_equipment_category  # If category is None, the item can't be equipped

    def __repr__(self):
        return "ItemData(%s)" % self.base_name


_item_data_by_type: Dict[ItemType, ItemData] = {}
_item_types_grouped_by_level: Dict[int, Set[ItemType]] = {}
_item_levels: Dict[ItemType, int] = {}

# TODO register this elsewhere
_item_suffix_data_by_id: Dict[ItemSuffixId, ItemSuffixData] = {
    ItemSuffixId.RECKONING:
        ItemSuffixData("of reckoning",
                       [StatModifierInterval(HeroStat.PHYSICAL_DAMAGE, [0.1, 0.11, 0.12]),
                        StatModifierInterval(HeroStat.LIFE_STEAL, [0.1, 0.11, 0.12])]),
    ItemSuffixId.VITALITY:
        ItemSuffixData("of vitality",
                       [StatModifierInterval(HeroStat.MAX_HEALTH, [10, 20, 30])])
}


def create_item_description(item_id: ItemId) -> List[str]:
    data = get_item_data_by_type(item_id.item_type)
    lines = list(data.custom_description_lines)
    if item_id.base_stats:
        for modifier in item_id.base_stats:
            lines.append(modifier.get_description())
    if item_id.suffix_id:
        for modifier in item_id.suffix_stats:
            lines.append(modifier.get_description())
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
    # TODO this should be much more sophisticated
    # There should be some logic around how suffixes are chosen as loot
    # suffixes should have levels that match up with the item
    # loot tables should configure how likely a suffix is to drop
    if random.random() < 0.5:
        return ItemId.randomized_base(item_type, data.base_stats)
    else:
        suffix_id = random.choice([suffix_id for suffix_id in ItemSuffixId])
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
