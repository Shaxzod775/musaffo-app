"""
AttachmentStore implementation for ChatKit with local file storage.

IMPORTANT: This store must share the attachment metadata dictionary with
the MemoryStore to ensure ChatKitServer can find attachments after creation.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, TYPE_CHECKING

from chatkit.store import AttachmentStore
from chatkit.types import (
    Attachment,
    AttachmentCreateParams,
    FileAttachment,
    ImageAttachment,
)

if TYPE_CHECKING:
    from memory_store import MemoryStore


class LocalFileAttachmentStore(AttachmentStore[dict[str, Any]]):
    """
    AttachmentStore implementation that stores files on local disk.
    
    CRITICAL: This store receives a reference to MemoryStore and saves
    attachment metadata directly to it. This ensures ChatKitServer can
    find attachments via store.load_attachment().
    
    Flow:
    ┌─────────────────────────────────────────────────────────────────────┐
    │                      ATTACHMENT CREATE FLOW                         │
    ├─────────────────────────────────────────────────────────────────────┤
    │                                                                     │
    │   1. Client: attachments.create({name, mime_type, size})           │
    │                           │                                         │
    │                           ▼                                         │
    │   2. ChatKitServer calls AttachmentStore.create_attachment()       │
    │                           │                                         │
    │                           ▼                                         │
    │   3. We create Attachment with upload_url                          │
    │                           │                                         │
    │                           ▼                                         │
    │   4. We save metadata to BOTH:                                     │
    │      • self._attachments (for our own use)                         │
    │      • memory_store._attachments (for ChatKitServer)  ◄── KEY!     │
    │                           │                                         │
    │                           ▼                                         │
    │   5. Return Attachment to client with upload_url                   │
    │                           │                                         │
    │                           ▼                                         │
    │   6. Client POSTs file bytes to upload_url                         │
    │                           │                                         │
    │                           ▼                                         │
    │   7. We save file bytes to disk                                    │
    │                                                                     │
    └─────────────────────────────────────────────────────────────────────┘
    """

    def __init__(
        self, 
        memory_store: "MemoryStore",
        upload_dir: str = "./uploads",
        base_url: str = "http://localhost:8080"
    ) -> None:
        """
        Initialize the attachment store.
        
        Args:
            memory_store: Reference to the MemoryStore (for sharing metadata)
            upload_dir: Directory to store uploaded files
            base_url: Base URL for generating upload/download URLs
        """
        self.memory_store = memory_store
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = base_url.rstrip("/")
        
        # Local reference for our own metadata lookups
        self._attachments: Dict[str, Attachment] = {}

    def generate_attachment_id(self, mime_type: str, context: dict[str, Any]) -> str:
        """Generate a unique attachment ID."""
        return f"atc_{uuid.uuid4().hex[:12]}"

    async def create_attachment(
        self, 
        input: AttachmentCreateParams, 
        context: dict[str, Any]
    ) -> Attachment:
        """
        Create attachment metadata and return it with an upload URL.
        
        CRITICAL: We save the metadata to BOTH our local dict AND the
        MemoryStore's dict so ChatKitServer can find it later.
        """
        # Generate unique ID
        attachment_id = self.generate_attachment_id(input.mime_type, context)
        
        # Build URLs
        upload_url = f"{self.base_url}/api/attachments/{attachment_id}/upload"
        download_url = f"{self.base_url}/api/attachments/{attachment_id}/download"
        
        # Determine if this is an image or file
        is_image = input.mime_type.startswith("image/")
        
        now = datetime.utcnow()
        
        if is_image:
            attachment = ImageAttachment(
                id=attachment_id,
                name=input.name,
                mime_type=input.mime_type,
                size=input.size,
                upload_url=upload_url,
                preview_url=download_url,
                created_at=now,
            )
        else:
            attachment = FileAttachment(
                id=attachment_id,
                name=input.name,
                mime_type=input.mime_type,
                size=input.size,
                upload_url=upload_url,
                download_url=download_url,
                created_at=now,
            )
        
        # ═══════════════════════════════════════════════════════════════════
        # CRITICAL: Save to BOTH stores!
        # ═══════════════════════════════════════════════════════════════════
        # Save to our local dict (for get_attachment_metadata, etc.)
        self._attachments[attachment_id] = attachment
        
        # Save to MemoryStore's dict (so ChatKitServer can find it via load_attachment)
        self.memory_store._attachments[attachment_id] = attachment
        # ═══════════════════════════════════════════════════════════════════
        
        return attachment

    async def delete_attachment(
        self, 
        attachment_id: str, 
        context: dict[str, Any]
    ) -> None:
        """Delete attachment metadata and file bytes."""
        # Remove from both stores
        self._attachments.pop(attachment_id, None)
        self.memory_store._attachments.pop(attachment_id, None)
        
        # Remove file from disk
        file_path = self._get_file_path(attachment_id)
        if file_path.exists():
            file_path.unlink()

    # ─────────────────────────────────────────────────────────────────────
    # Helper methods for file storage
    # ─────────────────────────────────────────────────────────────────────

    def _get_file_path(self, attachment_id: str) -> Path:
        """Get the file path for an attachment."""
        attachment = self._attachments.get(attachment_id)
        if attachment and attachment.name:
            ext = Path(attachment.name).suffix
            return self.upload_dir / f"{attachment_id}{ext}"
        return self.upload_dir / attachment_id

    async def save_file_bytes(
        self, 
        attachment_id: str, 
        file_bytes: bytes,
        context: dict[str, Any]
    ) -> None:
        """Save file bytes to storage."""
        file_path = self._get_file_path(attachment_id)
        file_path.write_bytes(file_bytes)

    async def get_file_bytes(
        self, 
        attachment_id: str,
        context: dict[str, Any]
    ) -> bytes:
        """Retrieve file bytes from storage."""
        file_path = self._get_file_path(attachment_id)
        if not file_path.exists():
            raise FileNotFoundError(f"Attachment {attachment_id} not found")
        return file_path.read_bytes()

    async def get_attachment_metadata(
        self, 
        attachment_id: str,
        context: dict[str, Any]
    ) -> Attachment | None:
        """Get attachment metadata."""
        return self._attachments.get(attachment_id)

    def file_exists(self, attachment_id: str) -> bool:
        """Check if file bytes exist for an attachment."""
        return self._get_file_path(attachment_id).exists()
