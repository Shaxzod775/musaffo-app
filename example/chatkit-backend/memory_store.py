"""
In-memory store for ChatKit threads, items, and attachment metadata.

Architecture:
┌─────────────────────────────────────────────────────────────────────────┐
│                        STORAGE RESPONSIBILITIES                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   MemoryStore (Store interface)         AttachmentStore interface       │
│   ─────────────────────────────────────         ────────────────────────        │
│                                                                         │
│   • Thread metadata                     • File bytes (upload)           │
│   • Thread items (messages)             • File bytes (download)         │
│   • Attachment METADATA ◄──────────────► Coordinates with Store         │
│     (id, name, mime_type, size,                                         │
│      upload_url, preview_url)                                           │
│                                                                         │
│   Does NOT store file bytes!            Does NOT store metadata!        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from chatkit.store import NotFoundError, Store
from chatkit.types import Attachment, Page, Thread, ThreadItem, ThreadMetadata


@dataclass
class _ThreadState:
    thread: ThreadMetadata
    items: List[ThreadItem]


class MemoryStore(Store[dict[str, Any]]):
    """
    In-memory store compatible with the ChatKit server interface.

    Stores:
    - Thread metadata
    - Thread items (messages, tool calls, etc.)
    - Attachment metadata (but NOT file bytes - that's AttachmentStore's job)
    """

    def __init__(self) -> None:
        self._threads: Dict[str, _ThreadState] = {}
        self._attachments: Dict[str, Attachment] = {}  # NEW: attachment metadata storage

    @staticmethod
    def _get_thread_metadata(thread: ThreadMetadata | Thread) -> ThreadMetadata:
        """Return thread metadata without any embedded items (openai-chatkit>=1.0)."""
        has_items = isinstance(thread, Thread) or "items" in getattr(
            thread, "model_fields_set", set()
        )
        if not has_items:
            return thread.model_copy(deep=True)

        data = thread.model_dump()
        data.pop("items", None)
        return ThreadMetadata(**data).model_copy(deep=True)

    # ─────────────────────────────────────────────────────────────────────
    # Thread metadata
    # ─────────────────────────────────────────────────────────────────────

    async def load_thread(self, thread_id: str, context: dict[str, Any]) -> ThreadMetadata:
        state = self._threads.get(thread_id)
        if not state:
            # Auto-create thread if not found (handles Cloud Run container restarts)
            thread = ThreadMetadata(
                id=thread_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            await self.save_thread(thread, context)
            return thread
        return self._get_thread_metadata(state.thread)

    async def save_thread(self, thread: ThreadMetadata, context: dict[str, Any]) -> None:
        metadata = self._get_thread_metadata(thread)
        state = self._threads.get(thread.id)
        if state:
            state.thread = metadata
        else:
            self._threads[thread.id] = _ThreadState(
                thread=metadata,
                items=[],
            )

    async def load_threads(
        self,
        limit: int,
        after: str | None,
        order: str,
        context: dict[str, Any],
    ) -> Page[ThreadMetadata]:
        threads = sorted(
            (self._get_thread_metadata(state.thread) for state in self._threads.values()),
            key=lambda t: t.created_at or datetime.min,
            reverse=(order == "desc"),
        )

        if after:
            index_map = {thread.id: idx for idx, thread in enumerate(threads)}
            start = index_map.get(after, -1) + 1
        else:
            start = 0

        slice_threads = threads[start : start + limit + 1]
        has_more = len(slice_threads) > limit
        slice_threads = slice_threads[:limit]
        next_after = slice_threads[-1].id if has_more and slice_threads else None
        return Page(
            data=slice_threads,
            has_more=has_more,
            after=next_after,
        )

    async def delete_thread(self, thread_id: str, context: dict[str, Any]) -> None:
        self._threads.pop(thread_id, None)

    # ─────────────────────────────────────────────────────────────────────
    # Thread items
    # ─────────────────────────────────────────────────────────────────────

    def _items(self, thread_id: str) -> List[ThreadItem]:
        state = self._threads.get(thread_id)
        if state is None:
            state = _ThreadState(
                thread=ThreadMetadata(id=thread_id, created_at=datetime.utcnow()),
                items=[],
            )
            self._threads[thread_id] = state
        return state.items

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: dict[str, Any],
    ) -> Page[ThreadItem]:
        items = [item.model_copy(deep=True) for item in self._items(thread_id)]
        items.sort(
            key=lambda item: getattr(item, "created_at", datetime.utcnow()),
            reverse=(order == "desc"),
        )

        if after:
            index_map = {item.id: idx for idx, item in enumerate(items)}
            start = index_map.get(after, -1) + 1
        else:
            start = 0

        slice_items = items[start : start + limit + 1]
        has_more = len(slice_items) > limit
        slice_items = slice_items[:limit]
        next_after = slice_items[-1].id if has_more and slice_items else None
        return Page(data=slice_items, has_more=has_more, after=next_after)

    async def add_thread_item(
        self, thread_id: str, item: ThreadItem, context: dict[str, Any]
    ) -> None:
        self._items(thread_id).append(item.model_copy(deep=True))

    async def save_item(self, thread_id: str, item: ThreadItem, context: dict[str, Any]) -> None:
        items = self._items(thread_id)
        for idx, existing in enumerate(items):
            if existing.id == item.id:
                items[idx] = item.model_copy(deep=True)
                return
        items.append(item.model_copy(deep=True))

    async def load_item(self, thread_id: str, item_id: str, context: dict[str, Any]) -> ThreadItem:
        for item in self._items(thread_id):
            if item.id == item_id:
                return item.model_copy(deep=True)
        raise NotFoundError(f"Item {item_id} not found")

    async def delete_thread_item(
        self, thread_id: str, item_id: str, context: dict[str, Any]
    ) -> None:
        items = self._items(thread_id)
        self._threads[thread_id].items = [item for item in items if item.id != item_id]

    # ─────────────────────────────────────────────────────────────────────
    # Attachment METADATA (not file bytes!)
    # ─────────────────────────────────────────────────────────────────────
    #
    # These methods store/retrieve attachment METADATA only.
    # The actual file bytes are handled by AttachmentStore.
    #
    # Flow:
    # 1. AttachmentStore.create_attachment() creates metadata + returns upload_url
    # 2. Store.save_attachment() persists the metadata
    # 3. Client uploads bytes to upload_url (handled by your FastAPI endpoint)
    # 4. Store.load_attachment() retrieves metadata when building messages
    # ─────────────────────────────────────────────────────────────────────

    async def save_attachment(
        self,
        attachment: Attachment,
        context: dict[str, Any],
    ) -> None:
        """
        Save attachment metadata.

        Called by ChatKitServer after AttachmentStore.create_attachment().
        Does NOT save file bytes - that's AttachmentStore's job.
        """
        self._attachments[attachment.id] = attachment

    async def load_attachment(
        self,
        attachment_id: str,
        context: dict[str, Any],
    ) -> Attachment:
        """
        Load attachment metadata by ID.

        Called when ChatKitServer needs to build a message that includes
        an attachment reference.
        """
        attachment = self._attachments.get(attachment_id)
        if attachment is None:
            raise NotFoundError(f"Attachment {attachment_id} not found")
        return attachment

    async def delete_attachment(
        self,
        attachment_id: str,
        context: dict[str, Any]
    ) -> None:
        """
        Delete attachment metadata.

        Note: This only deletes metadata. The actual file bytes should be
        deleted via AttachmentStore.delete_attachment().
        """
        self._attachments.pop(attachment_id, None)
