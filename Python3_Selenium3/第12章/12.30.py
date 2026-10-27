#coding=utf-8
from behave import given, when, then, step
@given('we have behave installed')
def step_impl(context):
    pass
# 数字类型number将会转换成整数类型
#以下函数是为了获取在场景文件中设置的数字 5，然后做出判断等操作。
@when('we implement {number:d} tests')
def step_impl(context, number):
    assert number > 1 or number == 0
    context.tests_count = number
@then('behave will test them for us!')
def step_impl(context):
    assert context.failed is False
    assert context.tests_count >= 0
