#!/usr/bin/env python3

class Base:
    def execute(self):
        print("Executing Base")


class A(Base):
    def execute(self):
        print("Executing A")


class B(Base):
    def execute(self):
        print("Executing B")


class Child(A, B):
    pass


# Create an instance of Child
obj = Child()
obj.execute()
