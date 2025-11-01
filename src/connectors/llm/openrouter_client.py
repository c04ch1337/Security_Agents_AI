
            """OpenRouter AI client used by the AI brain."""

            from __future__ import annotations

            import asyncio
            import json
            import os
            from typing import Any, Dict, Optional

            import aiohttp


            class OpenRouterClient:
                """Minimal async client for OpenRouter's chat completions API."""

                def __init__(self) -> None:
                    self.api_key = os.getenv("OPENROUTER_API_KEY")
                    self.base_url = "https://openrouter.ai/api/v1"
                    self.default_model = os.getenv("OPENROUTER_DEFAULT_MODEL", "anthropic/claude-3-sonnet")

                async def query(
                    self,
                    *,
                    prompt: str,
                    model: Optional[str] = None,
                    max_tokens: Optional[int] = None,
                    temperature: Optional[float] = None,
                ) -> str:
                    if not self.api_key:
                        raise ValueError("OPENROUTER_API_KEY environment variable not configured")

                    payload = {
                        "model": model or self.default_model,
                        "messages": [{"role": "user", "content": prompt}],
                    }
                    if max_tokens is not None:
                        payload["max_tokens"] = max_tokens
                    if temperature is not None:
                        payload["temperature"] = temperature

                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    }

                    async with aiohttp.ClientSession() as session:
                        try:
                            async with session.post(
                                f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=30
                            ) as response:
                                if response.status != 200:
                                    raise RuntimeError(
                                        f"OpenRouter API error {response.status}: {await response.text()}"
                                    )
                                data: Dict[str, Any] = await response.json()
                                return data["choices"][0]["message"]["content"]
                        except asyncio.TimeoutError as exc:  # noqa: PERF203
                            raise RuntimeError("OpenRouter request timed out") from exc

                async def analyze_security_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
                    prompt = (
                        "ROLE: You are a senior cybersecurity incident responder.
"
                        f"INCIDENT DATA:
{json.dumps(incident, indent=2)}
"
                        "Respond using JSON with keys: severity, confidence, containment_actions."
                    )
                    raw = await self.query(prompt=prompt)
                    try:
                        return json.loads(raw)
                    except json.JSONDecodeError:
                        return {"raw_response": raw}
