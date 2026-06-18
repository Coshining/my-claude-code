from behave import given, when, then
from unittest.mock import patch
import sys, os

import constants
from main import one_query_for_test
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

@given("Init Claude Agent")
def step_impl(context):
    context.client = constants.CLIENT

@given("{task}")
def step_impl(context, task: str):
    context.task = task

@when("Agent start")
def step_impl(context):
    context.caught_exception = None
    
    # 关键点：使用 side_effect 而不是 return_value
    # patch 会在 messages.create 每次被调用时，执行 context.mock_side_effect 函数
    with patch.object(context.client.messages, 'create', 
                      side_effect=context.mock_side_effect) as mock_create:
        try:
            context.final_result = one_query_for_test(context.task)
        except Exception as e:
            context.caught_exception = e

@then("{ans}")
def step_impl(context, ans: str):
    assert context.caught_exception is None, f"智能体执行异常: {context.caught_exception}"
    assert ans in context.final_result, f"未获得预期最终结果。实际结果: {context.final_result}"