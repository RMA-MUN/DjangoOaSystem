import json
import os
import re
from typing import Dict, Any, List, Optional

from app.agent.base import BaseAgent, AgentState
from app.agent.task_decomposer import TaskDecomposer
from app.agent.agent_router import AgentRouter
from app.agent.tool_agent import ToolAgent
from app.agent.knowledge_agent import KnowledgeAgent
from app.agent.memory_agent import MemoryAgent
from app.core.logger_handler import logger


class MainAgent(BaseAgent):
    """
    主调度Agent，负责协调各个子Agent的工作流程
    """
    
    def __init__(self):
        super().__init__("main_agent")
        self._llm = None  # 惰性创建，用于参数抽取
        self.task_decomposer = TaskDecomposer()
        self.agent_router = AgentRouter()
        self.tool_agent = ToolAgent()
        self.knowledge_agent = KnowledgeAgent()
        self.memory_agent = MemoryAgent()
        
        # 创建Agent映射
        self.agent_map = {
            "task_decomposer": self.task_decomposer,
            "agent_router": self.agent_router,
            "tool_agent": self.tool_agent,
            "knowledge_agent": self.knowledge_agent,
            "memory_agent": self.memory_agent
        }
    
    async def process_input(self, user_input: str, session_id: str, user_id: str) -> Dict[str, Any]:
        """
        处理用户输入，协调工作流程
        
        :param user_input: 用户输入
        :param session_id: 会话ID
        :param user_id: 用户ID
        :return: 处理结果
        """
        try:
            # 初始化状态
            state = AgentState()
            state.user_input = user_input
            state.session_id = session_id
            state.user_id = user_id
            
            logger.info(f"【主Agent】开始处理请求，用户ID: {user_id}, 会话ID: {session_id}, 输入: {user_input[:50]}...")
            
            # 步骤1: 获取会话历史
            state = await self._get_session_history(state)
            
            # 步骤2: 任务分解
            state = await self._decompose_task(state)
            
            # 如果任务分解失败，返回错误
            if not state.task_subtasks:
                return {
                    "response": "抱歉，无法理解您的请求。请重新描述您的需求。",
                    "error": "任务分解失败"
                }
            
            # 步骤3: 执行子任务
            state = await self._execute_subtasks(state)
            
            # 步骤4: 整合结果
            # 如果 final_response 已经被设置（例如，因为参数不完整而需要向用户询问），则跳过整合结果
            if not state.final_response:
                state = await self._integrate_results(state)
            
            # 步骤5: 保存记忆
            await self._save_memory(state)
            
            logger.info(f"【主Agent】处理完成，会话ID: {session_id}")
            
            return {
                "response": state.final_response or "处理完成",
                "steps": state.agent_results,
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"【主Agent】处理失败: {str(e)}", exc_info=True)
            return {
                "response": f"抱歉，处理您的请求时出现了错误: {str(e)}",
                "error": str(e)
            }
    
    async def _get_session_history(self, state: AgentState) -> AgentState:
        """获取会话历史"""
        memory_result = await self.memory_agent.process({
            "session_id": state.session_id,
            "user_id": state.user_id,
            "action": "get_history"
        })
        
        if memory_result.get("success"):
            state.chat_history = memory_result.get("history", [])
            logger.info(f"【主Agent】获取会话历史成功，记录数: {len(state.chat_history)}")
        
        return state
    
    async def _decompose_task(self, state: AgentState) -> AgentState:
        """分解任务"""
        decomposition_result = await self.task_decomposer.process({
            "user_input": state.user_input
        })
        
        if decomposition_result.get("success"):
            state.task_type = decomposition_result.get("task_type")
            state.task_subtasks = decomposition_result.get("subtasks", [])
            logger.info(f"【主Agent】任务分解成功，任务类型: {state.task_type}, 子任务数: {len(state.task_subtasks)}")
        else:
            logger.error(f"【主Agent】任务分解失败: {decomposition_result.get('error')}")
        
        return state
    
    async def _execute_subtasks(self, state: AgentState) -> AgentState:
        """执行子任务"""
        for subtask in self._sort_subtasks(state.task_subtasks or []):
            # 检查参数是否完整（尝试从历史会话和用户输入中提取参数）
            if not await self._check_params_complete(subtask, state):
                # 如果参数不完整，已经在_check_params_complete中设置了final_response
                return state
            
            # 路由到合适的Agent
            route_result = await self.agent_router.process({
                "task_type": subtask["task_type"],
                "subtask_description": subtask["description"],
                "required_params": subtask["required_params"]
            })
            
            if route_result.get("success"):
                selected_agent_id = route_result.get("selected_agent")
                agent = self.agent_map.get(selected_agent_id)
                
                if agent:
                    # 执行子任务
                    task_input = {
                        "task_description": subtask["description"],
                        "params": subtask.get("params", {}),
                        "session_id": state.session_id,
                        "user_id": state.user_id
                    }
                    
                    # 根据不同的Agent添加特定参数
                    if selected_agent_id == "knowledge_agent":
                        task_input["query"] = subtask.get("query", subtask["description"])
                    elif selected_agent_id == "memory_agent":
                        task_input["action"] = subtask.get("action", "get_history")
                    
                    agent_result = await agent.process(task_input)
                    
                    # 保存Agent执行结果
                    state.agent_results[subtask["task_id"]] = {
                        "task": subtask,
                        "agent": selected_agent_id,
                        "result": agent_result
                    }
                    
                    logger.info(f"【主Agent】子任务执行成功: {subtask['task_name']}")
                else:
                    logger.error(f"【主Agent】未找到路由到的Agent: {selected_agent_id}")
                    state.agent_results[subtask.get("task_id", "unknown")] = {
                        "task": subtask,
                        "agent": selected_agent_id,
                        "result": {"success": False, "error": f"未找到Agent: {selected_agent_id}"}
                    }
            else:
                logger.error(f"【主Agent】子任务路由失败: {route_result.get('error')}")
                state.agent_results[subtask.get("task_id", "unknown")] = {
                    "task": subtask,
                    "agent": None,
                    "result": {"success": False, "error": route_result.get("error", "路由失败")}
                }
        
        return state

    def _sort_subtasks(self, subtasks: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        """
        按依赖与优先级排序子任务。
        - **先依赖后执行**：dependencies 满足后才执行
        - **同层按 priority 升序**
        若存在依赖缺失/循环依赖，退化为按 priority 升序 + 原顺序，避免整个流程卡死。
        """
        if not subtasks:
            return []

        task_by_id: Dict[str, Dict[str, Any]] = {}
        for t in subtasks:
            tid = t.get("task_id")
            if tid:
                task_by_id[tid] = t

        # 计算入度
        indeg: Dict[str, int] = {t.get("task_id"): 0 for t in subtasks if t.get("task_id")}
        dependents: Dict[str, list[str]] = {tid: [] for tid in indeg.keys()}

        missing_dep = False
        for t in subtasks:
            tid = t.get("task_id")
            if not tid:
                continue
            deps = t.get("dependencies") or []
            for dep in deps:
                if dep not in indeg:
                    missing_dep = True
                    continue
                indeg[tid] += 1
                dependents[dep].append(tid)

        def _priority_key(tid: str):
            t = task_by_id.get(tid, {})
            pr = t.get("priority")
            return (pr if isinstance(pr, int) else 9999)

        # Kahn
        ready = sorted([tid for tid, d in indeg.items() if d == 0], key=_priority_key)
        ordered_ids: list[str] = []
        while ready:
            tid = ready.pop(0)
            ordered_ids.append(tid)
            for nxt in dependents.get(tid, []):
                indeg[nxt] -= 1
                if indeg[nxt] == 0:
                    ready.append(nxt)
                    ready.sort(key=_priority_key)

        # 检查循环依赖/缺失依赖
        if missing_dep or len(ordered_ids) != len(indeg):
            logger.warning("【主Agent】检测到依赖缺失或循环依赖，退化为按priority排序执行")
            return sorted(subtasks, key=lambda t: (t.get("priority", 9999), subtasks.index(t)))

        # 保留没有 task_id 的子任务（放到最后，按 priority）
        ordered = [task_by_id[tid] for tid in ordered_ids]
        no_id = [t for t in subtasks if not t.get("task_id")]
        if no_id:
            ordered.extend(sorted(no_id, key=lambda t: (t.get("priority", 9999))))
        return ordered
    
    def _create_param_extraction_llm(self):
        """与 TaskDecomposer 一致，用于从上下文抽取结构化参数。"""
        api_key = os.getenv("ALIYUN_ACCESS_KEY_SECRET")
        base_url = os.getenv("ALIYUN_BASE_URL")
        try:
            from langchain_community.chat_models import ChatTongyi
        except Exception as e:
            logger.error(f"【参数抽取】大模型依赖加载失败: {e}", exc_info=True)
            return None
        return ChatTongyi(
            model=os.getenv("MAIN_AGENT_PARAM_MODEL", "qwen3-max"),
            api_key=api_key,
            base_url=base_url,
            temperature=0,
        )

    def _build_context_for_extraction(self, state: AgentState) -> str:
        parts: List[str] = []
        if state.user_input:
            parts.append(f"【当前用户输入】\n{state.user_input.strip()}")
        if state.chat_history:
            lines = []
            for user_msg, assistant_msg in state.chat_history:
                if user_msg:
                    lines.append(f"用户: {user_msg}")
                if assistant_msg:
                    lines.append(f"助手: {assistant_msg}")
            if lines:
                parts.append("【历史对话】\n" + "\n".join(lines))
        return "\n\n".join(parts).strip()

    def _extract_params_from_text(self, text: str, required_params: list[str]) -> Dict[str, str]:
        """
        轻量规则提取（不调用 LLM）。用于常见中文场景与单元测试。
        """
        extracted_params: Dict[str, str] = {}

        # 提取 JWT token
        import re
        token_pattern = r'JWT token：([\w\-\.]+)'
        token_match = re.search(token_pattern, text)
        if token_match:
            token = token_match.group(1)
            # 检查是否需要 token 参数
            for param in required_params:
                if "token" in param.lower():
                    extracted_params[param] = token
                    break
            # 额外添加 token 参数（工具函数期望的参数名）
            if "token" in required_params:
                extracted_params["token"] = token
            elif "jwt_token" in extracted_params:
                # 如果提取的是 jwt_token，但工具需要 token，进行映射
                extracted_params["token"] = extracted_params["jwt_token"]

        # 参数名关键词 -> 触发词 / 正则补充
        param_patterns = {
            "日期": ["日期", "时间", "什么时候", "哪天", "几号", "从", "到", "开始", "结束"],
            "时间": ["时间", "几点", "时分", "什么时候"],
            "地点": ["地点", "在哪里", "位置", "地址", "会议室", "在"],
            "姓名": ["姓名", "名字", "叫什么", "申请人", "审批人"],
            "数量": ["数量", "多少", "几个"],
            "金额": ["金额", "价格", "费用", "多少钱"],
            "主题": ["主题", "标题", "内容"],
            "类型": ["类型", "种类", "类别", "假别", "考勤类型"],
            "状态": ["状态", "情况", "进度"],
            "部门": ["部门", "科室", "团队"],
            "项目": ["项目", "任务", "事项"],
            "token": ["token", "JWT", "认证", "授权"],
        }

        punct = ["，", "。", "！", "？", "；", "：", ",", ".", "!", "?", ";", ":"]

        def _clip(s: str) -> str:
            s = s.strip()
            for p in punct:
                if p in s:
                    s = s[: s.find(p)].strip()
            return s

        # 全文：相对日期/时间（优先匹配「明天下午3点」这类完整片段，避免只命中「明天」）
        if any("日期" in p or "时间" in p for p in required_params):
            m = re.search(
                r"(?:明天|后天|大后天|今天|昨天)(?:上午|下午|晚上|中午|早间)?\s*\d{1,2}\s*[:：点]\s*\d{0,2}|"
                r"(?:明天|后天|大后天|今天|昨天|下周|本周|周[一二三四五六日]|"
                r"\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日号]?|"
                r"\d{1,2}月\d{1,2}[日号]?|"
                r"(?:上午|下午|晚上|中午)?\s*\d{1,2}\s*[:：点]\s*\d{0,2})",
                text,
            )
            if m:
                for rp in required_params:
                    if ("日期" in rp or "时间" in rp) and rp not in extracted_params:
                        extracted_params[rp] = _clip(m.group(0))

        # 地点：取「开会/举行」前最后一个「在」后面的片段，避免「我想在明天…在会议室A」串台
        if any("地点" in p or "地址" in p or "位置" in p for p in required_params):
            for end_kw in ("开会", "举行", "进行", "见面"):
                if end_kw not in text:
                    continue
                before = text[: text.find(end_kw)]
                last_zai = before.rfind("在")
                if last_zai == -1:
                    continue
                loc = before[last_zai + len("在") :].strip()
                loc = _clip(loc)
                if loc:
                    for rp in required_params:
                        if (
                            ("地点" in rp or "地址" in rp or "位置" in rp)
                            and rp not in extracted_params
                        ):
                            extracted_params[rp] = loc
                break

        for param in required_params:
            if param in extracted_params:
                continue
            for pattern_key, patterns in param_patterns.items():
                if pattern_key not in param:
                    continue
                for pattern in patterns:
                    if pattern not in text:
                        continue
                    start_idx = text.find(pattern)
                    if start_idx == -1:
                        continue
                    extract_text = text[start_idx + len(pattern) :].strip()
                    extract_text = _clip(extract_text)
                    if extract_text:
                        extracted_params[param] = extract_text
                        break
                if param in extracted_params:
                    break

            if param in extracted_params:
                continue
            param_lower = param.lower()
            text_lower = text.lower()
            if param_lower in text_lower:
                start_idx = text_lower.find(param_lower)
                extract_text = text[start_idx + len(param_lower) :].strip()
                extract_text = _clip(extract_text)
                if extract_text:
                    extracted_params[param] = extract_text

        return extracted_params

    async def _llm_extract_params(
        self,
        *,
        required_params: List[str],
        subtask_description: str,
        task_type: str,
        context: str,
        merged_so_far: Dict[str, str],
    ) -> Dict[str, str]:
        """
        用大模型从上下文中抽取 required_params 中**尚未出现**的键。
        返回的 dict 只包含非空字符串值，键必须与 required_params 完全一致。
        """
        missing_keys = [k for k in required_params if k not in merged_so_far or not str(merged_so_far.get(k, "")).strip()]
        if not missing_keys or not context.strip():
            return {}

        if self._llm is None:
            self._llm = self._create_param_extraction_llm()
        if self._llm is None:
            return {}

        keys_json = json.dumps(missing_keys, ensure_ascii=False)
        prompt = f"""你是参数抽取助手。根据「上下文」和「子任务说明」，为下列参数名填写取值。

规则：
1. 只输出一个 JSON 对象，不要 markdown 代码块，不要其它解释。
2. JSON 的键必须且只能来自下面「待填参数名」列表，键名逐字一致（含空格与标点）。
3. 若某参数在上下文中**不存在或无法合理推断**，该键的值使用 null（不要编造）。
4. 日期时间可保留用户原话，或规范为单行字符串。
5. 若「已有部分参数」中已有某键的非空值，不要覆盖，输出时可省略该键或仍输出相同值。

待填参数名（JSON 的键集合）：
{keys_json}

子任务类型：{task_type}
子任务说明：
{subtask_description}

已有部分参数（不要覆盖）：
{json.dumps(merged_so_far, ensure_ascii=False)}

上下文：
{context}
"""
        try:
            from langchain_core.messages import HumanMessage

            msg = await self._llm.ainvoke([HumanMessage(content=prompt)])
            raw = (msg.content or "").strip()
            # 去掉可能的 ```json 包裹
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```\s*$", "", raw)
            data = json.loads(raw)
            if not isinstance(data, dict):
                return {}
            out: Dict[str, str] = {}
            for k in missing_keys:
                if k not in data:
                    continue
                v = data[k]
                if v is None:
                    continue
                if isinstance(v, (dict, list)):
                    v = json.dumps(v, ensure_ascii=False)
                s = str(v).strip()
                if s:
                    out[k] = s
            return out
        except Exception as e:
            logger.warning(f"【参数抽取】LLM 抽取失败，将沿用规则与已有参数: {e}")
            return {}

    def _strict_params_enabled(self) -> bool:
        return os.getenv("MAIN_AGENT_STRICT_REQUIRED_PARAMS", "false").lower() in (
            "1",
            "true",
            "yes",
        )

    async def _check_params_complete(self, subtask: Dict[str, Any], state: AgentState) -> bool:
        """检查参数是否完整：先规则、再 LLM；缺参时默认放行给子 Agent（可配置严格拦截）。"""
        task_type = subtask.get("task_type", "")
        # 这些类型由子 Agent / 对话本身处理，不在此用 required_params 卡死
        if task_type in (
            "knowledge_query",
            "rag_query",
            "information_summary",
            "user_interaction",
            "memory_management",
        ):
            return True

        required_params = subtask.get("required_params") or []
        if not required_params:
            return True

        existing_params = subtask.get("params") or {}
        all_text = self._build_context_for_extraction(state)

        merged_params = dict(existing_params)
        heuristic = self._extract_params_from_text(all_text, list(required_params))
        if heuristic:
            merged_params.update(heuristic)
            logger.info(f"【参数提取】规则命中: {heuristic}")

        llm_extra = await self._llm_extract_params(
            required_params=list(required_params),
            subtask_description=subtask.get("description") or "",
            task_type=task_type,
            context=all_text,
            merged_so_far=dict(merged_params),
        )
        if llm_extra:
            merged_params.update(llm_extra)
            logger.info(f"【参数提取】LLM 补充: {llm_extra}")

        # 特殊处理：如果需要token参数，尝试从历史对话和用户输入中提取
        if "token" in [p.lower() for p in required_params]:
            # 从文本中提取token
            import re
            token_pattern = r'JWT token：([\w\-\.]+)|token：([\w\-\.]+)|token=([\w\-\.]+)'
            token_match = re.search(token_pattern, all_text)
            if token_match:
                token = token_match.group(1) or token_match.group(2) or token_match.group(3)
                for param in required_params:
                    if "token" in param.lower():
                        merged_params[param] = token
                        logger.info(f"【参数提取】从文本中提取token: {token[:20]}...")

        if merged_params:
            subtask["params"] = merged_params

        missing_params = [
            p
            for p in required_params
            if p not in merged_params or not str(merged_params.get(p, "")).strip()
        ]
        if not missing_params:
            logger.info(f"【参数检查】所有参数已提取完成: {merged_params}")
            return True

        logger.info(f"【参数检查】仍缺参数: {missing_params}")

        if self._strict_params_enabled():
            state.final_response = (
                f"我需要更多信息来完成任务：{', '.join(missing_params)}"
            )
            return False

        # 默认：不阻断，交给 tool_agent 等用自然语言 + 部分 params 继续推理/调工具
        logger.warning(
            "【参数检查】缺参但未启用 STRICT，继续执行子任务；子 Agent 可结合完整描述补全"
        )
        return True
    
    async def _integrate_results(self, state: AgentState) -> AgentState:
        """整合结果"""
        # 整合所有Agent的执行结果
        results = []
        
        for task_id, task_data in state.agent_results.items():
            result = task_data.get("result", {})
            if result.get("success"):
                # 根据不同的Agent提取结果
                agent_id = task_data.get("agent")
                if agent_id == "tool_agent":
                    results.append(result.get("output", ""))
                elif agent_id == "knowledge_agent":
                    results.append(result.get("knowledge_content", ""))
                elif agent_id == "memory_agent":
                    results.append("记忆操作成功")
        
        # 生成最终回复
        if results:
            state.final_response = "\n\n".join(results)
        else:
            state.final_response = "任务执行完成，但没有返回结果。"
        
        return state
    
    async def _save_memory(self, state: AgentState) -> None:
        """保存记忆"""
        if state.user_input and state.final_response:
            await self.memory_agent.process({
                "session_id": state.session_id,
                "user_id": state.user_id,
                "action": "add_memory",
                "message": state.user_input,
                "response": state.final_response
            })
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理输入数据"""
        try:
            user_input = input_data.get("user_input") or input_data.get("query")
            session_id = input_data.get("session_id")
            user_id = input_data.get("user_id")
            
            if not all([user_input, session_id, user_id]):
                return {
                    "success": False,
                    "error": "缺少必要参数",
                    "final_response": "处理失败：缺少必要参数"
                }
            
            result = await self.process_input(user_input, session_id, user_id)
            response = result.get("response", "处理完成")
            
            return {
                "success": True,
                "response": response,
                "final_response": response,
                "steps": result.get("steps", []),
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"【主Agent】处理失败: {str(e)}", exc_info=True)
            error_msg = f"处理失败：{str(e)}"
            return {
                "success": False,
                "error": str(e),
                "final_response": error_msg
            }
    
    def can_handle(self, task_type: str) -> bool:
        """判断是否能够处理特定类型的任务"""
        return True  # 主Agent可以处理所有任务