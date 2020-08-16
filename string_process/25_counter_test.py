"""this is for counter which can solve counting string"""
# !/usr/bin/env python3
# coding=utf-8
from collections import Counter


def main():
    # list of students in class 1
    class1 = ['Bob', 'Sam', 'Emma', 'Cindy', 'Sam', 'Cindy', 'Emma', 'Cindy']
    class2 = ['Billy', 'Barry', 'Wilson', 'Sam', 'Emma', 'Cindy', 'Cindy']
    # TODO: Create a Counter for class1 and class2
    c1 = Counter(class1)
    c2 = Counter(class2)
    # TODO: How many students are named Cindy in class1
    print(c1['Cindy'])
    # TODO: How many students are in class1
    print(sum(c1.values()), ' students in class1')
    # TODO: Combine the two classes
    c1.update(class2)
    print(sum(c1.values()), ' students in class1')
    # TODO: What is the most common name in class1
    print(c1.most_common())
    # TODO: Separate class2 from class1
    c1.subtract(class2)
    print(c1.most_common(), ' ordered students')
    # TODO: What is common between class1 and class2
    print(c1 & c2)


if __name__ == '__main__':
    main()