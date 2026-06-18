Feature: 测试门禁

  @mock_agent_flow=permission/rm
  Scenario: bash高危命令rm拒绝
    Given Init Claude Agent
    And task=拒绝bash高危命令:rm
    When Agent start
    Then Permission denied.