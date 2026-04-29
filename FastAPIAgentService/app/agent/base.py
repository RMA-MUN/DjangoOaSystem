from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from langchain_core.messages import BaseMessage


class BaseAgent(ABC):
    """
    Agent 基类，定义所有 Agent 的基本接口
    """
    
    def __init__(self, name: str):
        """
        初始化 Agent
        
        :param name: Agent 名称
        """
        self.name = name
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理输入数据
        
        :param input_data: 输入数据字典
        :return: 处理结果字典
        """
        pass
    
    @abstractmethod
    def can_handle(self, task_type: str) -> bool:
        """
        判断是否能够处理特定类型的任务
        
        :param task_type: 任务类型
        :return: 是否能够处理
        """
        pass
    
    def get_name(self) -> str:
        """
        获取 Agent 名称
        
        :return: Agent 名称
        """
        return self.name


class AgentState:
    """
    Agent 状态管理类
    """
    
    def __init__(self):
        self.user_input: Optional[str] = None
        self.session_id: Optional[str] = None
        self.user_id: Optional[str] = None
        self.jwt_token: Optional[str] = None
        self.chat_history: Optional[list] = None
        self.task_type: Optional[str] = None
        self.task_subtasks: Optional[list] = None
        self.selected_agent: Optional[str] = None
        self.agent_results: Dict[str, Any] = {}
        self.final_response: Optional[str] = None
        self.error: Optional[str] = None
        # 新增字段
        self.intent: Optional[str] = None
        self.intent_confidence: float = 0.0
        self.is_intent_valid: bool = False
        self.target_tool: Optional[str] = None
        self.required_params: List[str] = []
        self.extracted_params: Dict[str, Any] = {}
        self.param_retry_count: int = 0
        self.max_param_retries: int = 3
        self.task_status: str = "pending"
        self.tool_result: Optional[str] = None
        self.user_prompt: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        :return: 状态字典
        """
        return {
            "user_input": self.user_input,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "chat_history": self.chat_history,
            "task_type": self.task_type,
            "task_subtasks": self.task_subtasks,
            "selected_agent": self.selected_agent,
            "agent_results": self.agent_results,
            "final_response": self.final_response,
            "error": self.error,
            # 新增字段
            "intent": self.intent,
            "intent_confidence": self.intent_confidence,
            "is_intent_valid": self.is_intent_valid,
            "target_tool": self.target_tool,
            "required_params": self.required_params,
            "extracted_params": self.extracted_params,
            "param_retry_count": self.param_retry_count,
            "max_param_retries": self.max_param_retries,
            "task_status": self.task_status,
            "tool_result": self.tool_result,
            "user_prompt": self.user_prompt
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentState':
        """
        从字典创建状态
        
        :param data: 状态字典
        :return: AgentState 实例
        """
        state = cls()
        state.user_input = data.get("user_input")
        state.session_id = data.get("session_id")
        state.user_id = data.get("user_id")
        state.chat_history = data.get("chat_history")
        state.task_type = data.get("task_type")
        state.task_subtasks = data.get("task_subtasks")
        state.selected_agent = data.get("selected_agent")
        state.agent_results = data.get("agent_results", {})
        state.final_response = data.get("final_response")
        state.error = data.get("error")
        # 新增字段
        state.intent = data.get("intent")
        state.intent_confidence = data.get("intent_confidence", 0.0)
        state.is_intent_valid = data.get("is_intent_valid", False)
        state.target_tool = data.get("target_tool")
        state.required_params = data.get("required_params", [])
        state.extracted_params = data.get("extracted_params", {})
        state.param_retry_count = data.get("param_retry_count", 0)
        state.max_param_retries = data.get("max_param_retries", 3)
        state.task_status = data.get("task_status", "pending")
        state.tool_result = data.get("tool_result")
        state.user_prompt = data.get("user_prompt")
        return state