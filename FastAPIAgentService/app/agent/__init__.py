"""
多智能体架构模块
"""
from app.agent.agent_router import AgentRouter
from app.agent.base import BaseAgent, AgentState
from app.agent.knowledge_agent import KnowledgeAgent
from app.agent.main_agent import MainAgent
from app.agent.memory_agent import MemoryAgent
from app.agent.param_extraction_agent import ParamExtractionAgent
from app.agent.task_decomposer import TaskDecomposer
from app.agent.tool_agent import ToolAgent
from app.agent.workflow import run_agent_workflow

__all__ = [
    "BaseAgent",
    "AgentState",
    "TaskDecomposer",
    "AgentRouter",
    "ToolAgent",
    "KnowledgeAgent",
    "MemoryAgent",
    "ParamExtractionAgent",
    "MainAgent",
    "run_agent_workflow",
]




def __getattr__(name: str):
    if name == "TaskDecomposer":
        from app.agent.task_decomposer import TaskDecomposer as _T
        return _T
    if name == "AgentRouter":
        from app.agent.agent_router import AgentRouter as _T
        return _T
    if name == "ToolAgent":
        from app.agent.tool_agent import ToolAgent as _T
        return _T
    if name == "KnowledgeAgent":
        from app.agent.knowledge_agent import KnowledgeAgent as _T
        return _T
    if name == "MemoryAgent":
        from app.agent.memory_agent import MemoryAgent as _T
        return _T
    if name == "ParamExtractionAgent":
        from app.agent.param_extraction_agent import ParamExtractionAgent as _T
        return _T
    if name == "MainAgent":
        from app.agent.main_agent import MainAgent as _T
        return _T
    if name == "run_agent_workflow":
        from app.agent.workflow import run_agent_workflow as _T
        return _T
    raise AttributeError(name)