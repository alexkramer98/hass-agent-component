"""The Custom Hass Agent."""
from __future__ import annotations
from typing import Literal

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    conversation.async_set_agent(hass, entry, HassAgent(hass, entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data[DOMAIN].pop(entry.entry_id)
    conversation.async_unset_agent(hass, entry)
    return True

class HassAgent(conversation.AbstractConversationAgent):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.history: dict[str, list[dict]] = {}

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        return MATCH_ALL

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        response = await self.hass.services.async_call(
            "rest_command",
            "conversate",
            {"msg_id":user_input.conversation_id, "dev_id":user_input.device_id, "msg":user_input.text},
            blocking=True,
            return_response=True,
        )

        intent_response = intent.IntentResponse(language=user_input.language)
        intent_response.async_set_speech(response['content']['msg'])
        return conversation.ConversationResult(
            response=intent_response, conversation_id=response['content']['id']
        )
