import json

import anthropic
from fastapi import HTTPException

from core.database import settings
from core.logging import get_logger
from modules.ai.prompts import SYSTEM_PROMPT
from modules.ai.schemas import AIChatRequest, AIChatResponse, AIAction

logger = get_logger(__name__)
client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)


async def chat(body: AIChatRequest) -> AIChatResponse:
    canvas_context = (
        f"Current canvas:\nNodes: {json.dumps(body.nodes, indent=2)}\n"
        f"Edges: {json.dumps(body.edges, indent=2)}\n\n"
        f"User: {body.message}"
    )
    try:
        response = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": canvas_context}],
        )
        raw = response.content[0].text.strip()
        data = json.loads(raw)
        actions = [AIAction(**a) for a in data.get("actions", [])]
        logger.info("AI chat completed: %d action(s)", len(actions))
        return AIChatResponse(message=data.get("message", ""), actions=actions)
    except json.JSONDecodeError:
        logger.error("AI returned invalid JSON: %s", raw[:200])
        raise HTTPException(status_code=500, detail="AI returned an invalid response format")
    except Exception as e:
        logger.exception("AI chat failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
