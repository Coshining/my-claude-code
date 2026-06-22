from behave import given, when, then
from unittest.mock import patch
import sys, os

import constants
from main import one_query_for_test
from utils import excute_tool_calls

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


@given("Init Claude Agent")
def init(context):
    context.client = constants.CLIENT


@given("task={task}")
def task(context, task: str):
    context.task = task


@given("allow={allow}")
def allow(context, allow: str):
    # 保存 allow 值到 context，供 tool_call_start 步骤使用
    context.allow = allow


@when("Agent start")
def agent_start(context):
    context.caught_exception = None

    # 关键点：使用 side_effect 而不是 return_value
    # patch 会在 messages.create 每次被调用时，执行 context.mock_side_effect 函数
    with patch.object(
        context.client.messages, "create", side_effect=context.mock_side_effect
    ) as mock_create:
        try:
            context.final_result = one_query_for_test(context.task)
        except Exception as e:
            context.caught_exception = e


@when("Tool call start")
def tool_call_start(context):
    context.caught_exception = None

    # 模拟input函数，自动允许
    def mock_input_func(prompt: str) -> str:
        print(prompt, end="")
        # 从 context 中获取 allow 值（由 @given allow= 步骤设置）
        allow_value = getattr(context, "allow", "y")
        return allow_value

    with patch("builtins.input", side_effect=mock_input_func):
        try:
            results = excute_tool_calls(context.mock_response.content)
            final_results = []
            for result in results:
                final_results.append(result["content"])

            context.final_result = "#".join(final_results)
        except Exception as e:
            context.caught_exception = e


@then("{ans}")
def step_impl(context, ans: str):
    assert (
        context.caught_exception is None
    ), f"智能体执行异常: {context.caught_exception}"
    assert (
        ans in context.final_result
    ), f"未获得预期最终结果。实际结果: {context.final_result}"
