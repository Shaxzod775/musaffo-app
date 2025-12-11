"""
Firebase service for saving ChatKit messages to Firestore.
Integrates with existing Firebase project structure.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any, Optional

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import AsyncClient
from google.oauth2 import service_account

logger = logging.getLogger(__name__)


class FirebaseService:
    """Service for interacting with Firebase Firestore."""

    def __init__(self):
        """Initialize Firebase Admin SDK."""
        self._initialized = False
        self._db: Optional[AsyncClient] = None
        self._cred_path: Optional[str] = None
        self._init_firebase()

    def _init_firebase(self):
        """
        Initialize Firebase Admin SDK if not already initialized.

        Initialization methods (in order of preference):
        1. Service account key file via GOOGLE_APPLICATION_CREDENTIALS env var
        2. Application Default Credentials (for Google Cloud environments)
        3. Skip initialization (app will work without Firebase persistence)
        """
        try:
            # Check if Firebase is already initialized
            if firebase_admin._apps:
                logger.info("Firebase already initialized in another instance")
                # Use the existing app's credentials
                base_dir = os.path.dirname(os.path.abspath(__file__))
                default_cred_path = os.path.join(base_dir, "credentials.json")
                cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", default_cred_path)
                if os.path.exists(cred_path):
                    gcloud_creds = service_account.Credentials.from_service_account_file(cred_path)
                    self._db = AsyncClient(credentials=gcloud_creds, project=gcloud_creds.project_id)
                else:
                    self._db = AsyncClient()
                self._initialized = True
                return

            # Method 1: Try credentials.json in the same directory first
            base_dir = os.path.dirname(os.path.abspath(__file__))
            default_cred_path = os.path.join(base_dir, "credentials.json")
            cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", default_cred_path)

            if os.path.exists(cred_path):
                logger.info(f"Found service account key at: {cred_path}")
                self._cred_path = cred_path
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                logger.info("✅ Firebase initialized with service account credentials")

                # Get Firestore AsyncClient with explicit credentials
                gcloud_creds = service_account.Credentials.from_service_account_file(cred_path)
                self._db = AsyncClient(credentials=gcloud_creds, project=gcloud_creds.project_id)
                self._initialized = True
                logger.info("✅ Firestore client ready")
                return
            else:
                logger.warning(f"Service account key file not found at: {cred_path}")
                logger.info("Trying Application Default Credentials...")

                # Method 2: Try Application Default Credentials (Google Cloud)
                try:
                    firebase_admin.initialize_app()
                    self._db = firestore.AsyncClient()
                    self._initialized = True
                    logger.info("✅ Firebase initialized with Application Default Credentials")
                    return
                except Exception as adc_error:
                    logger.warning(f"Application Default Credentials not available: {adc_error}")
                    logger.info("ℹ️  This is normal for local development without gcloud auth")

            # Method 3: Graceful degradation - no Firebase
            logger.warning("⚠️  Firebase not initialized - messages will NOT be saved to Firestore")
            logger.info("💡 To enable Firebase persistence:")
            logger.info("   1. Get service account key from Firebase Console")
            logger.info(f"   2. Save it as: {default_cred_path}")
            logger.info("   3. Or set GOOGLE_APPLICATION_CREDENTIALS env var")
            logger.info("   4. Restart the server")
            self._initialized = False

        except Exception as e:
            logger.error(f"❌ Unexpected error during Firebase initialization: {e}")
            logger.exception("Full traceback:")
            self._initialized = False

    async def save_message(
        self,
        chat_id: str,
        message_text: str,
        role: str,  # 'user' or 'assistant'
        user_id: Optional[str] = None,
        model: str = "chatkit",
        metadata: Optional[dict] = None,
    ) -> bool:
        """
        Save a message to Firestore.

        Args:
            chat_id: Chat/thread ID
            message_text: Message content
            role: 'user' or 'assistant'
            user_id: User ID (optional)
            model: Model name used
            metadata: Additional metadata (attachments, etc.)

        Returns:
            True if successful, False otherwise
        """
        if not self._initialized or not self._db:
            logger.warning("Firebase not initialized, skipping message save")
            return False

        try:
            # Create message document matching existing structure
            message_data = {
                "content": message_text,  # 'content' for compatibility with existing structure
                "role": role,
                "timestamp": firestore.SERVER_TIMESTAMP,
                "model": model,
                "modernArchitecture": True,
                "pending": False,
            }

            # Add optional fields
            if metadata:
                if metadata.get("usage"):
                    message_data["usage"] = metadata["usage"]
                if metadata.get("webSearchUsed"):
                    message_data["webSearchUsed"] = metadata["webSearchUsed"]
                if metadata.get("webSearchResources"):
                    message_data["webSearchResources"] = metadata["webSearchResources"]
                if metadata.get("tools_used"):
                    message_data["toolsUsed"] = metadata["tools_used"]

            # Save to Firestore: users/{userId}/chats/{chatId}/messages/{auto-generated-id}
            if user_id and chat_id:
                doc_ref = (self._db.collection("users")
                          .document(user_id)
                          .collection("chats")
                          .document(chat_id)
                          .collection("messages")
                          .document())
            elif user_id:
                # Fallback if no chat_id
                doc_ref = self._db.collection("users").document(user_id).collection("chatkitMessages").document()
            else:
                # Fallback to old structure if no user_id
                doc_ref = self._db.collection("chats").document(chat_id).collection("messages").document()

            await doc_ref.set(message_data)

            logger.info(f"✅ Saved {role} message for user {user_id}, chat {chat_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving message to Firebase: {e}")
            return False

    async def save_user_message(
        self,
        chat_id: str,
        message_text: str,
        user_id: Optional[str] = None,
        attachments: Optional[list] = None,
    ) -> bool:
        """Save a user message to Firestore."""
        metadata = {}
        if attachments:
            metadata["attachments"] = attachments

        return await self.save_message(
            chat_id=chat_id,
            message_text=message_text,
            role="user",
            user_id=user_id,
            metadata=metadata if metadata else None,
        )

    async def save_assistant_message(
        self,
        chat_id: str,
        message_text: str,
        model: str = "gpt-5-mini",
        tools_used: Optional[list] = None,
        user_id: Optional[str] = None,
        widget_type: Optional[str] = None,
    ) -> bool:
        """Save an assistant message to Firestore."""
        metadata = {}
        if tools_used:
            metadata["tools_used"] = tools_used
        if widget_type:
            metadata["widget_type"] = widget_type

        return await self.save_message(
            chat_id=chat_id,
            message_text=message_text,
            role="assistant",
            user_id=user_id,
            model=model,
            metadata=metadata if metadata else None,
        )

    async def load_chat_history(
        self,
        user_id: str,
        limit: int = 20,
    ) -> list:
        """
        Load chat history for a user from Firestore.

        Args:
            user_id: User ID
            limit: Maximum number of messages to load

        Returns:
            List of messages sorted by timestamp (oldest first)
        """
        if not self._initialized or not self._db:
            logger.warning("Firebase not initialized, cannot load chat history")
            return []

        try:
            # Load messages from users/{userId}/chatkitMessages
            messages_ref = (
                self._db.collection("users")
                .document(user_id)
                .collection("chatkitMessages")
                .order_by("timestamp", direction="DESCENDING")
                .limit(limit)
            )

            docs = await messages_ref.get()
            messages = []
            for doc in docs:
                data = doc.to_dict()
                messages.append({
                    "role": data.get("role", "user"),
                    "text": data.get("text", ""),
                    "metadata": data.get("metadata"),
                })

            # Reverse to get oldest first (chronological order)
            messages.reverse()
            logger.info(f"Loaded {len(messages)} messages for user {user_id}")
            return messages

        except Exception as e:
            logger.error(f"Error loading chat history: {e}")
            return []

    async def update_chat_metadata(
        self,
        chat_id: str,
        user_id: Optional[str] = None,
        title: Optional[str] = None,
        last_message: Optional[str] = None,
        model: Optional[str] = None,
    ) -> bool:
        """
        Update chat metadata (last message time, title, etc.).

        Args:
            chat_id: Chat ID
            user_id: User ID
            title: Chat title
            last_message: Preview of last message
            model: Model used

        Returns:
            True if successful
        """
        if not self._initialized or not self._db:
            return False

        try:
            chat_data = {
                "lastMessageTime": firestore.SERVER_TIMESTAMP,
                "updatedAt": firestore.SERVER_TIMESTAMP,
                "modernArchitecture": True,
            }

            if title:
                chat_data["title"] = title[:50] + ("..." if len(title) > 50 else "")

            if last_message:
                chat_data["lastMessage"] = last_message[:100] + ("..." if len(last_message) > 100 else "")

            if model:
                chat_data["model"] = model

            # Update or create chat document in users/{userId}/chats/{chatId}
            if user_id:
                chat_ref = self._db.collection("users").document(user_id).collection("chats").document(chat_id)
            else:
                chat_ref = self._db.collection("chats").document(chat_id)

            await chat_ref.set(chat_data, merge=True)

            logger.info(f"✅ Updated chat metadata for {chat_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating chat metadata: {e}")
            return False

    async def save_chat_messages_batch(
        self,
        user_id: str,
        chat_id: str,
        user_message: str,
        assistant_message: str,
        model: str = "gpt-5",
        sources: Optional[list] = None,
    ) -> bool:
        """
        Save both user and assistant messages in a single batch operation.
        This is more efficient than saving separately.

        Args:
            user_id: User ID
            chat_id: Chat/conversation ID
            user_message: User's message text
            assistant_message: AI's response text
            model: Model name used
            sources: Web search sources if any

        Returns:
            True if successful
        """
        if not self._initialized or not self._db:
            logger.warning("Firebase not initialized, skipping batch save")
            return False

        try:
            from google.cloud.firestore_v1 import WriteBatch

            batch = self._db.batch()

            # Reference to messages collection
            messages_ref = (self._db.collection("users")
                           .document(user_id)
                           .collection("chats")
                           .document(chat_id)
                           .collection("messages"))

            # User message
            user_doc_ref = messages_ref.document()
            user_data = {
                "content": user_message,
                "role": "user",
                "timestamp": firestore.SERVER_TIMESTAMP,
                "modernArchitecture": True,
            }
            batch.set(user_doc_ref, user_data)

            # Assistant message
            assistant_doc_ref = messages_ref.document()
            assistant_data = {
                "content": assistant_message,
                "role": "assistant",
                "timestamp": firestore.SERVER_TIMESTAMP,
                "model": model,
                "modernArchitecture": True,
                "pending": False,
            }

            if sources:
                assistant_data["webSearchUsed"] = True
                assistant_data["webSearchResources"] = sources

            batch.set(assistant_doc_ref, assistant_data)

            # Update chat metadata
            chat_ref = self._db.collection("users").document(user_id).collection("chats").document(chat_id)
            chat_data = {
                "title": user_message[:50] + ("..." if len(user_message) > 50 else ""),
                "lastMessage": assistant_message[:100] + ("..." if len(assistant_message) > 100 else ""),
                "lastMessageTime": firestore.SERVER_TIMESTAMP,
                "model": model,
                "modernArchitecture": True,
                "messageCount": firestore.Increment(1),
            }
            batch.set(chat_ref, chat_data, merge=True)

            # Commit batch
            await batch.commit()

            logger.info(f"✅ Batch saved messages for user {user_id}, chat {chat_id}")
            return True

        except Exception as e:
            logger.error(f"Error in batch save: {e}", exc_info=True)
            return False

    async def update_user_limits(
        self,
        user_id: str,
        model_tier: str = "free",  # "free" or "premium"
    ) -> bool:
        """
        Update user daily limits after AI response.
        Increments the 'used' count for the appropriate model tier.

        Args:
            user_id: User ID
            model_tier: "free" for free models, "premium" for premium models

        Returns:
            True if successful
        """
        if not self._initialized or not self._db:
            logger.warning("Firebase not initialized, cannot update limits")
            return False

        try:
            # Determine which limit field to update
            limit_field = "premium-models" if model_tier == "premium" else "free-models"

            user_ref = self._db.collection("users").document(user_id)

            # Get current user data
            user_doc = await user_ref.get()

            if not user_doc.exists:
                logger.warning(f"User {user_id} not found, cannot update limits")
                return False

            user_data = user_doc.to_dict()
            daily_limits = user_data.get("dailyLimits", {})
            current_limit = daily_limits.get(limit_field, {})

            # Get current reset time (19:00 UTC = 00:00 Tashkent)
            import time
            from datetime import datetime, timezone

            now = datetime.now(timezone.utc)
            today_reset = now.replace(hour=19, minute=0, second=0, microsecond=0)

            if now >= today_reset:
                # Reset time is tomorrow at 19:00 UTC
                from datetime import timedelta
                next_reset = today_reset + timedelta(days=1)
            else:
                next_reset = today_reset

            reset_time_ms = int(next_reset.timestamp() * 1000)
            current_reset_time = current_limit.get("resetTime", 0)

            # Check if we need to reset limits (new day)
            if reset_time_ms > current_reset_time:
                # Reset for new day
                new_used = 1
                new_reset_time = reset_time_ms
                logger.info(f"Resetting limits for user {user_id} (new day)")
            else:
                # Increment existing
                new_used = current_limit.get("used", 0) + 1
                new_reset_time = current_reset_time

            # Update limits
            await user_ref.update({
                f"dailyLimits.{limit_field}.used": new_used,
                f"dailyLimits.{limit_field}.resetTime": new_reset_time,
                "stats.totalRequests": firestore.Increment(1),
                "stats.lastRequestAt": firestore.SERVER_TIMESTAMP,
            })

            logger.info(f"Updated limits for user {user_id}: {limit_field}.used = {new_used}")
            return True

        except Exception as e:
            logger.error(f"Error updating user limits: {e}")
            return False

    async def check_user_limits(
        self,
        user_id: str,
        model_tier: str = "free",
    ) -> dict:
        """
        Check if user has remaining limits.

        Args:
            user_id: User ID
            model_tier: "free" or "premium"

        Returns:
            dict with 'allowed', 'used', 'total', 'remaining'
        """
        if not self._initialized or not self._db:
            # If Firebase not initialized, allow by default
            return {"allowed": True, "used": 0, "total": 999, "remaining": 999}

        try:
            user_ref = self._db.collection("users").document(user_id)
            user_doc = await user_ref.get()

            if not user_doc.exists:
                return {"allowed": True, "used": 0, "total": 10, "remaining": 10}

            user_data = user_doc.to_dict()
            subscription = user_data.get("subscription", {})
            is_premium = subscription.get("tier") == "premium"

            # Check subscription expiration
            expires_at = subscription.get("expiresAt")
            if expires_at:
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc)
                if isinstance(expires_at, str):
                    expiration = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                else:
                    expiration = expires_at
                if now > expiration:
                    is_premium = False

            daily_limits = user_data.get("dailyLimits", {})
            limit_field = "premium-models" if model_tier == "premium" else "free-models"
            current_limit = daily_limits.get(limit_field, {})

            # Default limits
            if is_premium:
                default_total = 30 if model_tier == "premium" else 50
            else:
                default_total = 10 if model_tier == "free" else 0

            used = current_limit.get("used", 0)
            total = current_limit.get("total", default_total)
            remaining = max(0, total - used)

            # Check if reset time has passed
            import time
            from datetime import datetime, timezone

            now = datetime.now(timezone.utc)
            today_reset = now.replace(hour=19, minute=0, second=0, microsecond=0)

            if now >= today_reset:
                from datetime import timedelta
                next_reset = today_reset + timedelta(days=1)
            else:
                next_reset = today_reset

            reset_time_ms = int(next_reset.timestamp() * 1000)
            current_reset_time = current_limit.get("resetTime", 0)

            if reset_time_ms > current_reset_time:
                # Limits should be reset
                used = 0
                remaining = total

            allowed = remaining > 0 or (model_tier == "premium" and not is_premium)

            return {
                "allowed": allowed,
                "used": used,
                "total": total,
                "remaining": remaining,
                "is_premium": is_premium,
            }

        except Exception as e:
            logger.error(f"Error checking user limits: {e}")
            return {"allowed": True, "used": 0, "total": 10, "remaining": 10}


# Global singleton instance
_firebase_service: Optional[FirebaseService] = None


def get_firebase_service() -> FirebaseService:
    """
    Get or create Firebase service instance.

    Note: Service is initialized once at application startup via lifespan().
    This function returns the existing instance or creates it if needed (e.g., for testing).
    """
    global _firebase_service
    if _firebase_service is None:
        _firebase_service = FirebaseService()
    return _firebase_service
