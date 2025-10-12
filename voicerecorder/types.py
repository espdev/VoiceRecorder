from dataclasses import dataclass


@dataclass
class ItemInfo[T]:
    """Generic item with info"""

    item: T
    name: str
    description: str
