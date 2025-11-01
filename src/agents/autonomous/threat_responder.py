
"""Autonomous Threat Response Agent."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Dict, List

from src.brain.ai_brain import SecurityEvent


class AutonomousThreatResponder:
    """Executes response playbooks for security incidents."""

    name = "autonomous_threat_responder"

    async def handle_event(self, event: SecurityEvent, analysis: Dict[str, Any]) -> Dict[str, Any]:
        threat_type = self._classify_threat_type(event)
        handler = getattr(self, f"_execute_{threat_type}_playbook", self._execute_generic_playbook)
        actions = await handler(event, analysis)
        return {
            "playbook": threat_type,
            "actions_executed": actions,
            "handled_at": datetime.utcnow().isoformat(),
        }

    def _classify_threat_type(self, event: SecurityEvent) -> str:
        description = event.description.lower()
        if any(token in description for token in ("ransomware", "encrypt")):
            return "ransomware"
        if any(token in description for token in ("phishing", "credential")):
            return "phishing"
        if any(token in description for token in ("lateral", "movement", "psexec")):
            return "lateral_movement"
        if any(token in description for token in ("exfiltration", "data leak")):
            return "data_exfiltration"
        return "generic"

    async def _execute_ransomware_playbook(self, event: SecurityEvent, _: Dict[str, Any]) -> List[Dict[str, Any]]:
        await asyncio.sleep(0)
        return [
            {"action": "isolate_endpoints", "details": event.raw_data.get("endpoints", [])},
            {"action": "block_processes", "details": event.raw_data.get("processes", [])},
            {"action": "trigger_backups", "details": True},
        ]

    async def _execute_phishing_playbook(self, event: SecurityEvent, _: Dict[str, Any]) -> List[Dict[str, Any]]:
        await asyncio.sleep(0)
        return [
            {"action": "block_urls", "details": event.raw_data.get("malicious_urls", [])},
            {"action": "reset_credentials", "details": event.raw_data.get("compromised_accounts", [])},
        ]

    async def _execute_lateral_movement_playbook(self, event: SecurityEvent, _: Dict[str, Any]) -> List[Dict[str, Any]]:
        await asyncio.sleep(0)
        return [
            {"action": "disable_accounts", "details": event.raw_data.get("accounts", [])},
            {"action": "quarantine_hosts", "details": event.raw_data.get("hosts", [])},
        ]

    async def _execute_data_exfiltration_playbook(self, event: SecurityEvent, _: Dict[str, Any]) -> List[Dict[str, Any]]:
        await asyncio.sleep(0)
        return [
            {"action": "block_egress", "details": event.raw_data.get("destinations", [])},
            {"action": "collect_forensics", "details": True},
        ]

    async def _execute_generic_playbook(self, event: SecurityEvent, _: Dict[str, Any]) -> List[Dict[str, Any]]:
        await asyncio.sleep(0)
        return [
            {"action": "notify_human", "details": event.source},
        ]
