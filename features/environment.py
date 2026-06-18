import json
import os

from anthropic.types import Message

MOCK_DIR = os.path.join(os.path.dirname(__file__), 'mock_responses')

def create_sequential_side_effect(base_filename):
    """
    工厂函数：生成一个用于 mock 的 side_effect 函数
    每次被调用时，自动递增读取 base_filename_0.json, base_filename_1.json...
    """
    call_count = 0
    
    def side_effect_func(*args, **kwargs):
        nonlocal call_count
        
        # 拼接当前轮次应该读取的文件名
        filename = f"{base_filename}_{call_count}.json"
        filepath = os.path.join(MOCK_DIR, filename)
        
        if not os.path.exists(filepath):
            # 如果文件不存在，说明 Agent 陷入了死循环或者测试用例没写完
            raise Exception(f"Agent 请求次数过多！找不到第 {call_count} 轮的 Mock 文件: {filepath}")
            
        # 读取文件内容
        with open(filepath, 'r', encoding='utf-8') as f:
            mock_text = f.read()
            
        print(f"[Mock 拦截器] 拦截第 {call_count} 次请求，读取文件: {filename}")
        
        # 构造 Anthropic 标准响应结构
        mock_response = Message(**json.loads(mock_text))
        
        # 调用次数加一，为下一次准备
        call_count += 1
        return mock_response
        
    return side_effect_func

def before_scenario(context, scenario):
    context.mock_side_effect = None
    context.error_to_simulate = None

    for tag in scenario.tags:
        # 使用新标签 @mock_agent_flow("基础文件名")
        if tag.startswith("mock_agent_flow"):
            base_name = tag.split("=", 1)[1].strip('"\'')
            # 将动态函数挂载到 context 上
            context.mock_side_effect = create_sequential_side_effect(base_name)
            
        elif tag.startswith("simulate_error="):
            # 错误模拟逻辑保持不变
            error_type = tag.split("=", 1)[1].strip('"\'')
            if error_type == "auth":
                context.error_to_simulate = Exception("Simulated Authentication Error")