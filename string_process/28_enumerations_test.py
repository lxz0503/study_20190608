"""this is for enumerations based on original Enum class"""
# !/usr/bin/env python3
# coding=utf-8
# https://www.cnblogs.com/bdhk/p/7506691.html     ---reference for enum
from enum import Enum, auto, unique


@unique
class Fruit(Enum):
    APPLE = 1
    BANANA = 2
    ORANGE = 3
    PEAR = auto()


def main():
    # TODO: enum has human-readable values and types
    print(Fruit.APPLE.value)    # 1
    print(type(Fruit.APPLE))    # <enum 'Fruit'>
    print(repr(Fruit.APPLE))    # <Fruit.APPLE: 1>
    # TODO: enum has name and value properties
    print(Fruit.APPLE.name, Fruit.APPLE.value)
    print(Fruit.PEAR.name, Fruit.PEAR.value)
    # TODO: hashable and used as key
    my_fruit = {}
    my_fruit[Fruit.APPLE] = 'delicious'
    print(my_fruit[Fruit.APPLE])


if __name__ == '__main__':
    main()
