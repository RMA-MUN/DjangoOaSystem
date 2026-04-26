from typing import Dict, Any, List
import json
from datetime import datetime, timedelta

from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.agent.base import BaseAgent
from app.core.logger_handler import logger
from app.tools.oa_tools import (
    get_attendance_types,
    get_attendance_responser,
    get_attendance_records,
    create_attendance_record,
    update_attendance_record,
    get_departments,
    get_users,
    get_informs,
    create_inform,
    update_inform,
    get_latest_informs,
    get_latest_attendance,
    get_department_staff_count
)
from app.tools.rag_tools import (
    rag_summary_tools,
    what_time_is_now,
    get_user_info_tools,
    reorder_documents_tools
)


class ToolAgent(BaseAgent):
    """
    工具执行Agent，负责调用外部工具执行任务
    """

    def __init__(self):
        super().__init__("tool_agent")
        self.tools = self._get_all_tools()

    def _fix_json_format(self, json_str: str) -> str:
        """修复JSON格式错误"""
        import re
        # 确保所有键名都用双引号包围，使用更精确的正则表达式
        # 只匹配真正的键名（字母数字下划线），不匹配值中的内容
        json_str = re.sub(r'(\{|,\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)', r'\1"\2"\3', json_str)
        # 修复未闭合的引号
        json_str = re.sub(r'"([^"]*)$', r'"\1"', json_str)
        return json_str

    def _normalize_for_strict_json(self, value: Any) -> Any:
        """递归规范化对象，尽量将可解析字符串转换为JSON对象。"""
        if isinstance(value, dict):
            return {str(k): self._normalize_for_strict_json(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._normalize_for_strict_json(item) for item in value]
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("{") or stripped.startswith("["):
                try:
                    parsed = json.loads(stripped)
                    return self._normalize_for_strict_json(parsed)
                except json.JSONDecodeError:
                    return value
            return value
        return value

    def _build_strict_json_block(self, params: Dict[str, Any]) -> str:
        """将参数统一转换为严格JSON字符串（双引号、可解析）。"""
        normalized_params = self._normalize_for_strict_json(params)
        return json.dumps(normalized_params, ensure_ascii=False, separators=(",", ":"))
    
    def _get_all_tools(self) -> List[BaseTool]:
        """获取所有可用的工具"""
        return [
            # OA工具
            get_attendance_types,
            get_attendance_responser,
            get_attendance_records,
            create_attendance_record,
            update_attendance_record,
            get_departments,
            get_users,
            get_informs,
            create_inform,
            update_inform,
            get_latest_informs,
            get_latest_attendance,
            get_department_staff_count,
            
            # RAG工具
            rag_summary_tools,
            what_time_is_now,
            get_user_info_tools,
            reorder_documents_tools
        ]

    @staticmethod
    def _resolve_date_expr(date_expr: str, is_end_time: bool = False) -> str:
        """将相对日期表达式转换为标准时间字符串。"""
        if date_expr == "today":
            return datetime.now().strftime("%Y-%m-%dT23:59:59" if is_end_time else "%Y-%m-%dT00:00:00")
        if date_expr == "tomorrow":
            base = datetime.now() + timedelta(days=1)
            return base.strftime("%Y-%m-%dT23:59:59" if is_end_time else "%Y-%m-%dT00:00:00")
        return date_expr

    def _build_leave_tool_args(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        从上游参数中提取并标准化请假工具调用参数。
        返回空字典表示参数不足或格式不可用，继续走通用Agent流程。
        """
        jwt_token = params.get("jwt_token") or params.get("token")
        raw_leave = params.get("leave_request_payload") or params.get("leave_request_data")
        if not jwt_token or not raw_leave:
            return {}

        leave_data: Dict[str, Any] = {}
        if isinstance(raw_leave, str):
            try:
                leave_data = json.loads(raw_leave)
            except json.JSONDecodeError:
                return {}
        elif isinstance(raw_leave, dict):
            leave_data = raw_leave
        else:
            return {}

        start_raw = leave_data.get("start_time") or leave_data.get("start_date")
        end_raw = leave_data.get("end_time") or leave_data.get("end_date")
        reason = leave_data.get("reason")
        leave_type = leave_data.get("type", leave_data.get("leave_type"))

        if not start_raw or not end_raw or not reason:
            return {}

        start_time = self._resolve_date_expr(str(start_raw), is_end_time=False)
        end_time = self._resolve_date_expr(str(end_raw), is_end_time=True)

        if leave_type is None:
            # 缺少明确type时，不走确定性分支，交由通用工具流程先查询类型再创建。
            return {}

        leave_type_str = str(leave_type).strip()
        if not leave_type_str.isdigit():
            # 例如“事假/病假”这类中文名称，不直接硬编码ID，避免后端类型ID不一致导致400。
            return {}

        return {
            "token": str(jwt_token),
            "type": int(leave_type_str),
            "start_time": start_time,
            "end_time": end_time,
            "reason": str(reason)
        }
    
    def _create_agent_executor(self):
        """创建Agent执行器"""
        from app.utils.prompt_loader import load_prompt
        
        # 创建聊天模型
        import os
        api_key = os.getenv("ALIYUN_ACCESS_KEY_SECRET")
        base_url = os.getenv("ALIYUN_BASE_URL")

        try:
            from langchain_community.chat_models import ChatTongyi
        except Exception as e:
            raise RuntimeError(
                "大模型客户端不可用，请检查 langchain/通义千问 依赖版本或环境配置"
            ) from e

        # 配置通义千问模型，确保工具调用参数格式正确
        llm = ChatTongyi(
            model="qwen3-max", 
            api_key=api_key, 
            base_url=base_url, 
            temperature=0.3,
            # 开启自动工具选择；不强制 json_object，避免 Tongyi 对 messages 的 json 关键词校验报错
            tool_choice="auto"
        )
        
        # 创建提示词模板
        system_prompt = load_prompt('tool_agent_prompt')
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # 创建Agent
        agent = create_tool_calling_agent(llm, self.tools, prompt)

        # 自定义错误处理函数
        def custom_error_handler(e):
            error_str = str(e)
            logger.error(f"Tool parsing error: {error_str}")

            # 如果无法修复，返回错误消息
            return f"Error: {error_str}. Please make sure to use valid JSON format for tool arguments."

        # 创建Executor
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True,
            handle_parsing_errors=custom_error_handler)

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理输入数据，执行工具调用"""
        try:
            task_description = input_data.get("task_description", "")
            params = input_data.get("params", {})

            # 对“请假申请创建”场景走确定性调用，避免LLM工具参数JSON格式不稳定导致失败。
            deterministic_leave_args = self._build_leave_tool_args(params)
            if deterministic_leave_args:
                logger.info(f"【工具执行】命中确定性请假流程，参数: {deterministic_leave_args}")
                direct_result = await create_attendance_record.ainvoke(deterministic_leave_args)
                return {
                    "success": True,
                    "output": direct_result,
                    "steps": [{
                        "tool": "create_attendance_record",
                        "tool_input": deterministic_leave_args,
                        "tool_output": direct_result,
                        "thought": "使用确定性流程直接创建请假考勤记录，避免工具参数JSON格式错误。"
                    }],
                    "tool_used": ["create_attendance_record"]
                }

            # 每次请求创建全新的 executor，避免跨会话状态污染
            agent_executor = self._create_agent_executor()

            # 构建工具调用输入：附带严格JSON参数块，减少模型生成非法arguments的概率
            tool_input = task_description
            if params:
                strict_json_params = self._build_strict_json_block(params)
                tool_input += (
                    "\n参数（严格JSON，仅可使用该格式组装工具arguments）：\n"
                    f"{strict_json_params}"
                )
            
            logger.info(f"【工具执行】开始执行工具，输入: {tool_input}")
            logger.info(f"【工具执行】参数: {params}")

            # 执行工具调用
            try:
                result = await agent_executor.ainvoke({
                    "input": tool_input,
                    "chat_history": []
                })
            except Exception as e:
                error_str = str(e)
                logger.error(f"【工具执行】执行失败: {error_str}")

                # 检查是否是JSON格式错误
                if "JSON format" in error_str or "function.arguments" in error_str:
                    logger.warning(f"JSON格式错误，尝试修复并重新执行")
                    # 重新构建工具输入，强调JSON格式要求
                    retry_input = (
                        tool_input
                        + "\n\n重要提示：\n"
                        + "1. function.arguments必须是严格有效JSON\n"
                        + "2. 键名和字符串值必须使用双引号\n"
                        + "3. 不允许出现注释、单引号、尾逗号\n"
                        + "4. 仅从上面的“参数（严格JSON）”中选取字段构造arguments\n"
                        + "5. 创建考勤记录仅需: token,type,start_time,end_time,reason\n"
                    )
                    result = await agent_executor.ainvoke({
                        "input": retry_input,
                        "chat_history": []
                    })
                elif "缺少必需参数" in error_str:
                    logger.warning(f"缺少必需参数，尝试重新执行")
                    # 重新构建工具输入，强调必需参数
                    retry_input = tool_input + "\n\n重要提示：\n创建考勤记录时，必须提供以下所有参数：\n- token: JWT token字符串\n- type: 考勤类型ID（整数）\n- start_time: 开始时间（格式：2026-04-26T00:00:00）\n- end_time: 结束时间（格式：2026-04-27T23:59:59）\n- reason: 请假原因（字符串）\n\n审批人由系统自动获取，无需传入responser参数。"
                    result = await agent_executor.ainvoke({
                        "input": retry_input,
                        "chat_history": []
                    })
                else:
                    raise
            
            output = result.get("output", "")
            intermediate_steps = result.get("intermediate_steps", [])
            
            # 记录工具调用步骤
            steps = []
            for action, observation in intermediate_steps:
                steps.append({
                    "tool": action.tool,
                    "tool_input": action.tool_input,
                    "tool_output": observation,
                    "thought": action.log
                })
            
            logger.info(f"【工具执行】成功执行工具，输出: {output[:100]}...")
            
            return {
                "success": True,
                "output": output,
                "steps": steps,
                "tool_used": [step["tool"] for step in steps]
            }
            
        except Exception as e:
            logger.error(f"【工具执行】失败: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def can_handle(self, task_type: str) -> bool:
        """判断是否能够处理特定类型的任务"""
        tool_task_types = [
            "tool_execution",
            "oa_operation",
            "api_call",
            "attendance",
            "department",
            "user",
            "inform",
            "rag_query"
        ]
        return task_type in tool_task_types
    
    def get_available_tools(self) -> List[BaseTool]:
        """获取可用的工具列表"""
        return self.tools