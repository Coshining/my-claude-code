Feature: 测试门禁

  @tool_call=permission.bash_deny_cmd
  Scenario: bash高危命令拒绝
    Given Init Claude Agent
    And task=拒绝bash高危命令
    When Tool call start
    Then Permission denied.#Permission denied.#Permission denied.#Permission denied.#Permission denied.#Permission denied.#Permission denied.#Permission denied.

  @tool_call=permission.dangerous_cmd
  Scenario Outline: 请求用户确认命令
    Given Init Claude Agent
    And task=<name>
    And allow=<allow>
    When Tool call start
    Then <response>

    Examples:
      | name         | allow | response                                                                                       |
      | 拒绝危险命令  | n     | Permission denied.#Permission denied.#Permission denied.#Permission denied.#Permission denied. |
      | 通过危险命令  | y     | Error: Path escapes workspace: z:\yyy#Error: Path escapes workspace: z:\yyy#Permission denied.#Permission denied.#Permission denied. |
