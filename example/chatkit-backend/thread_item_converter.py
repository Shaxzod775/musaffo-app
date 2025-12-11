"""
Конвертер для преобразования ChatKit ThreadItems в формат для OpenAI Agent
"""
from __future__ import annotations

from typing import Any

from chatkit.types import (
    AssistantMessageItem,
    ThreadItem,
    UserMessageItem,
)
from openai.types.responses import ResponseInputTextParam
from openai.types.responses.response_input_item_param import Message


class SimpleThreadItemConverter:
    """
    Простой конвертер для преобразования thread items
    """

    async def to_agent_input(
        self, items: ThreadItem | list[ThreadItem]
    ) -> list[Message]:
        """
        Преобразует thread items в формат для агента
        """
        if not isinstance(items, list):
            items = [items]

        result: list[Message] = []

        for item in items:
            if isinstance(item, UserMessageItem):
                # Пользовательское сообщение
                content_parts = []

                if isinstance(item.content, str):
                    content_parts.append(
                        ResponseInputTextParam(type="input_text", text=item.content)
                    )
                elif isinstance(item.content, list):
                    for part in item.content:
                        if hasattr(part, "text"):
                            content_parts.append(
                                ResponseInputTextParam(type="input_text", text=part.text)
                            )

                result.append(
                    Message(
                        type="message",
                        role="user",
                        content=content_parts,
                    )
                )

            elif isinstance(item, AssistantMessageItem):
                # Сообщение ассистента - конвертируем в текстовый формат
                text_content = ""

                if isinstance(item.content, str):
                    text_content = item.content
                elif isinstance(item.content, list):
                    text_parts = []
                    for part in item.content:
                        if hasattr(part, "text"):
                            text_parts.append(part.text)
                    text_content = "\n".join(text_parts)

                if text_content:
                    result.append(
                        Message(
                            type="message",
                            role="assistant",
                            content=[ResponseInputTextParam(type="output_text", text=text_content)],
                        )
                    )

        return result
