"""AI agent service for email generation."""

import json
import logging
import os
from typing import Dict, Optional
from shared.models.client import Client
from shared.models.task import Task
from shared.models.agent import Agent
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class AIAgent:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "500"))
    
    def _build_prompt(self, client: Client, task: Task, agent: Agent, agent_instructions: Optional[str] = None) -> str:
        prompt_parts = [
            "You are a professional real estate agent assistant.",
            "Write personalized, professional follow-up emails.",
            f"Client: {client.name}, Property: {client.property_address}, Stage: {client.stage}",
            f"Agent: {agent.name}, {agent.title or 'Real Estate Agent'}",
            f"Follow-up Type: {task.followup_type}",
        ]
        if agent_instructions:
            prompt_parts.append(f"Custom Instructions: {agent_instructions}")
        prompt_parts.append("Return JSON: {\"subject\": \"...\", \"body\": \"...\"}")
        return "\n".join(prompt_parts)
    
    async def generate_email(self, client: Client, task: Task, agent: Agent, agent_instructions: Optional[str] = None) -> Dict[str, str]:
        try:
            prompt = self._build_prompt(client, task, agent, agent_instructions)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": "You are a professional real estate agent assistant."},
                         {"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            data = json.loads(content.strip().replace("```json", "").replace("```", ""))
            return {"subject": data.get("subject", "Follow-up"), "body": data.get("body", "")}
        except Exception as e:
            logger.error(f"Error generating email: {e}")
            return self._get_fallback_email(client, task)
    
    async def generate_email_preview(self, client: Client, task: Task, agent: Agent, agent_instructions: Optional[str] = None) -> Dict[str, str]:
        return await self.generate_email(client, task, agent, agent_instructions)
    
    def _get_fallback_email(self, client: Optional[Client], task: Optional[Task]) -> Dict[str, str]:
        subject = f"Following up on {client.property_address if client else 'your inquiry'}"
        body = f"Hi {client.name if client else ''},\n\nI wanted to follow up with you.\n\nBest regards,\nYour Real Estate Agent"
        return {"subject": subject, "body": body, "preview": body[:200]}

