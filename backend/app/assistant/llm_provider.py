"""
Configurable LLM Provider layer for HomeFlow AI.
Supports Gemini, OpenAI, or transparent offline rule-based fallback.
Keeps AI provider logic isolated from business tools and secrets.
"""

import os
import json
import httpx
from typing import Optional, Dict, Any, Tuple


class LLMProvider:
    """Handles external LLM inference if API keys are configured in environment."""

    @classmethod
    def get_provider_status(cls) -> Tuple[bool, str]:
        """Return whether an external LLM is configured and the provider name."""
        if os.getenv("GEMINI_API_KEY"):
            return True, "Google Gemini"
        if os.getenv("OPENAI_API_KEY"):
            return True, "OpenAI"
        return False, "Local Rule-based Intent Engine (Zero-Config Fallback)"

    @classmethod
    async def parse_with_llm(cls, query: str, current_iso_time: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to parse user request into structured tool call using LLM.
        Returns parsed dict if successful, or None to fall back to rule-based engine.
        """
        gemini_key = os.getenv("GEMINI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        tools_spec = """
Available Tools:
1. create_task(title: str, description: str = "", category: str = "general", priority: str = "medium", due_date: str = null) [due_date formatted YYYY-MM-DD]
2. list_tasks(status: str = "all", category: str = null) [status in "all", "pending", "completed"]
3. complete_task(task_id: int)
4. update_task(task_id: int, title: str = null, priority: str = null, due_date: str = null)
5. delete_task(task_id: int)
6. create_reminder(title: str, remind_at: str) [remind_at formatted ISO 8601 YYYY-MM-DDTHH:MM:SS]
7. list_reminders(include_completed: bool = false)
8. complete_reminder(reminder_id: int)
9. get_daily_summary()
10. list_simulated_entry_events(limit: int = 10)
"""
        system_instruction = f"""
You are HomeFlow AI's tool routing engine.
Current date/time reference: {current_iso_time}.
Inspect the user's household command and output ONLY a valid JSON object with:
{{
  "tool": "tool_name",
  "arguments": {{ ... }},
  "clarification_needed": null or "message asking for missing details"
}}
If the user intent is missing required parameters (e.g. asking to create a task without a title, or a reminder without a time), set clarification_needed.
Return strictly JSON, without markdown formatting or backticks.
{tools_spec}
"""

        try:
            if gemini_key:
                # Call Gemini via REST
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
                payload = {
                    "contents": [{"parts": [{"text": f"{system_instruction}\nUser request: {query}"}]}],
                    "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"},
                }
                async with httpx.AsyncClient(timeout=8.0) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data["candidates"][0]["content"]["parts"][0]["text"]
                        return json.loads(text.strip())

            elif openai_key:
                # Call OpenAI via REST
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": query},
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.1,
                }
                async with httpx.AsyncClient(timeout=8.0) as client:
                    resp = await client.post(url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data["choices"][0]["message"]["content"]
                        return json.loads(text.strip())

        except Exception as e:
            # Fall back gracefully to rule-based engine
            print(f"[LLMProvider] Notice: LLM API request failed or timed out ({e}). Falling back to rule-based engine.")

        return None
