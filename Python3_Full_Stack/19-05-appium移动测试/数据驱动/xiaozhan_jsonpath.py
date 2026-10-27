#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:8/18/2022 8:45 PM
@file:xiaozhan_jsonpath.py
@project:xiaozhan_git
"""
from jsonpath import jsonpath
if __name__ == "__main__":
    book_info = {"store": {
        "book": [    # book is a key
            {"category": "reference",
             "author": "Nigel Rees",
             "title": "Sayings of the Century",
             "price": 8.95
             },
            {"category": "fiction",
             "author": "Evelyn Waugh",
             "title": "Sword of Honour",
             "price": 12.99
             },
            {"category": "fiction",
             "author": "Herman Melville",
             "title": "Moby Dick",
             "isbn": "0-553-21311-3",
             "price": 8.99
             },
            {"category": "fiction",
             "author": "J. R. R. Tolkien",
             "title": "The Lord of the Rings",
             "isbn": "0-395-19395-8",
             "price": 22.99
             }
        ],
        "bicycle": {    # bicycle is a key after book
            "color": "red",
            "price": 19.95
        }
    }
    }

    print(type(book_info))   # this is a dict
    print(jsonpath(book_info, "$.store.bicycle[color,price]"))  # ['red', 19.95]
    print(jsonpath(book_info, "$..book[0:2]"))
    print(jsonpath(book_info, "$..book[?(@.price<=8.99)]"))
    print(jsonpath(book_info, "$..bicycle"))   # [{'color': 'red', 'price': 19.95}]

    test = {'beijing': 1000, 'shanghai': 2000}
    print(type(test))
    print(jsonpath(test, '$..[beijing,shanghai]'))   # [1000, 2000]
