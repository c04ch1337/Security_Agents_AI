
            """Central AI Brain - coordinates analysis and responses."""

            from __future__ import annotations

            import asyncio
            import json
            import logging
            from dataclasses import dataclass
            from datetime import datetime
            from enum import Enum
            from typing import Any, Dict, List


            class ThreatSeverity(Enum):
                LOW = "low"
                MEDIUM = "medium"
                HIGH = "high"
                CRITICAL = "critical"


            @dataclass
            class SecurityEvent:
                """Standardised structure shared across agents."""

                event_id: str
                severity: ThreatSeverity
                source: str
                description: str
                timestamp: datetime
                raw_data: Dict[str, Any]


            class SecurityAIBrain:
                """Central orchestrator for AI agents."""

                def __init__(self) -> None:
                    self.logger = logging.getLogger("ai_brain")
                    self.logger.setLevel(logging.INFO)
                    self.agent_registry: Dict[str, Any] = {}
                    self.memory_manager = None
                    self.llm_provider = None
                    self._initialize_components()

                def _initialize_components(self) -> None:
                    self.logger.info("Initialising AI brain components")
                    try:
                        from src.connectors.llm.openrouter_client import OpenRouterClient
                        from src.brain.memory_manager import MemoryManager

                        self.llm_provider = OpenRouterClient()
                        self.memory_manager = MemoryManager()
                    except ImportError as exc:
                        self.logger.error("Component initialisation failed: %s", exc)
                        raise

                async def analyze_security_event(self, event: SecurityEvent) -> Dict[str, Any]:
                    self.logger.info("Analysing event: %s", event.event_id)
                    similar_events: List[Dict[str, Any]] = []
                    if self.memory_manager:
                        similar_events = await self.memory_manager.find_similar_events(event)

                    ai_analysis = await self._perform_ai_analysis(event, similar_events)
                    response_plan = await self._coordinate_agent_response(event, ai_analysis)

                    if self.memory_manager:
                        await self._learn_from_event(event, ai_analysis, response_plan)

                    return {
                        "event_id": event.event_id,
                        "ai_analysis": ai_analysis,
                        "response_plan": response_plan,
                        "similar_events_count": len(similar_events),
                        "confidence_score": ai_analysis.get("confidence", 0.0),
                    }

                async def _perform_ai_analysis(self, event: SecurityEvent, similar_events: List[Dict[str, Any]]) -> Dict[str, Any]:
                    if not self.llm_provider:
                        return {"error": "LLM provider not configured", "confidence": 0.0}

                    prompt = self._build_analysis_prompt(event, similar_events)
                    try:
                        response = await self.llm_provider.query(prompt=prompt, model="complex_analysis")
                        return self._parse_ai_response(response)
                    except Exception as exc:  # noqa: BLE001
                        self.logger.error("AI analysis failed: %s", exc)
                        return {"error": str(exc), "severity": event.severity.value, "confidence": 0.0}

                def _build_analysis_prompt(self, event: SecurityEvent, similar_events: List[Dict[str, Any]]) -> str:
                    similar_section = ""
                    if similar_events:
                        similar_section = f"SIMILAR EVENTS:
{json.dumps(similar_events[:3], indent=2)}
"

                    body = {
                        "event_id": event.event_id,
                        "severity": event.severity.value,
                        "source": event.source,
                        "description": event.description,
                        "timestamp": event.timestamp.isoformat(),
                    }
                    return (
                        "ROLE: You are a senior cybersecurity analyst.
"
                        "Analyse the following event and respond using the requested JSON schema.
"
                        f"EVENT DATA:
{json.dumps(body, indent=2)}
"
                        f"{similar_section}"
                        "RESPONSE FORMAT:
"
                        '{"assessed_severity": "high", "confidence": 0.8, "recommended_agents": []}'
                    )

                def _parse_ai_response(self, response: str) -> Dict[str, Any]:
                    try:
                        return json.loads(response)
                    except json.JSONDecodeError:
                        return {"raw_response": response, "confidence": 0.0}

                async def _coordinate_agent_response(self, event: SecurityEvent, analysis: Dict[str, Any]) -> Dict[str, Any]:
                    plan = {
                        "event_id": event.event_id,
                        "activated_agents": [],
                        "actions_planned": [],
                    }

                    for agent_name in analysis.get("recommended_agents", []):
                        agent = self.agent_registry.get(agent_name)
                        if not agent:
                            continue
                        task = await agent.handle_event(event, analysis)
                        plan["activated_agents"].append(agent_name)
                        plan["actions_planned"].extend(task.get("actions_executed", []))
                    return plan

                async def _learn_from_event(self, event: SecurityEvent, analysis: Dict[str, Any], response: Dict[str, Any]) -> None:
                    if not self.memory_manager:
                        return
                    payload = {
                        "event": event.__dict__,
                        "analysis": analysis,
                        "response": response,
                        "learned_at": datetime.utcnow().isoformat(),
                    }
                    await self.memory_manager.store_learning(payload)

                async def register_agent(self, name: str, agent_instance: Any) -> None:
                    self.agent_registry[name] = agent_instance

                async def run(self) -> None:
                    self.logger.info("AI brain started")
                    while True:
                        await asyncio.sleep(10)
