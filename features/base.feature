Feature: Claude Code base function

  @mock_agent_flow=success_fibonacci
  Scenario: 成功请求 Claude 生成 Python 函数
    Given Init Claude Agent
    And 展示出斐波那契数列的Python实现
    When Agent start
    Then def fibonacci