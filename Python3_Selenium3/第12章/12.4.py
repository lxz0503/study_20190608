
###
###配套视频已出版，学习有疑问联系作者qq:2574674466###
###
#coding=utf-8
from behave import given, when, then, step

@given('we have behave installed')
def step_impl(context):
    pass
#注意，以下的实现函数在校验语句中将>1改成>10
@when('we implement {number:d} tests')
def step_impl(context, number):
    assert number > 10 or number == 0
    context.tests_count = number
@then('behave will test them for us!')
def step_impl(context):
    assert context.failed is False
    assert context.tests_count >= 0
