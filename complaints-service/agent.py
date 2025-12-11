"""
Claude Haiku Agent for analyzing environmental violations
Uses AWS Bedrock for Claude API access with Bearer Token authentication
"""

import boto3
from botocore.config import Config
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import requests
import json
import base64
import os
import logging
from typing import Optional, List, Dict
from knowledge_base import VIOLATIONS, get_all_violations_summary, calculate_reward

logger = logging.getLogger(__name__)


class ComplaintAnalyzerAgent:
    """AI Agent for analyzing environmental complaint images using Claude Haiku"""
    
    def __init__(self):
        self.bearer_token = os.getenv('AWS_BEARER_TOKEN_BEDROCK')
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        
        logger.info(f"Initializing ComplaintAnalyzerAgent with region: {self.region}")
        
        # Claude 3.5 Haiku model ID for Bedrock
        self.model_id = "anthropic.claude-haiku-4-5-20251001-v1:0"
        self.endpoint = f"https://bedrock-runtime.{self.region}.amazonaws.com"
        
        # System prompt with knowledge base
        self.system_prompt = f"""Ты — ИИ-эксперт по экологическим нарушениям в Узбекистане.
Твоя задача — анализировать фотографии нарушений и определять:
1. Тип нарушения
2. Потенциальный размер штрафа согласно законодательству
3. Возможное вознаграждение заявителю (15% от штрафа)

{get_all_violations_summary()}

ИНСТРУКЦИИ:
- Внимательно изучи ВСЕ предоставленные изображения
- Определи тип нарушения из списка выше
- Если нарушение не относится к экологии, укажи это
- Оцени серьёзность нарушения (низкая/средняя/высокая)
- Рассчитай диапазон штрафа и вознаграждения
- Дай рекомендации по подаче жалобы

Отвечай на русском языке, структурированно и понятно для обычного гражданина.
"""

        # Spam detection prompt
        self.spam_check_prompt = """Ты — модератор жалоб на экологические нарушения.
Твоя задача — определить, является ли присланная жалоба спамом или нерелевантным контентом.

КРИТЕРИИ СПАМА:
1. Фотографии не связаны с экологией (селфи, еда, случайные объекты, мемы)
2. Фотографии одинаковые или почти идентичные
3. Описание не соответствует фотографиям
4. Фотографии явно не из Узбекистана или не показывают реальную ситуацию
5. Изображения низкого качества, размытые, или невозможно понять что на них
6. Скриншоты, рисунки, или явно отредактированные изображения (не реальные фото)

КРИТЕРИИ ВАЛИДНОЙ ЖАЛОБЫ:
1. Фотографии показывают реальную экологическую проблему
2. Виден контекст места (улица, здание, природа)
3. Описание логически связано с фотографиями
4. Разные ракурсы одного нарушения (не копии)

Отвечай ТОЛЬКО в формате JSON:
{"is_spam": true/false, "spam_reason": "причина если спам", "confidence": 0.0-1.0}
"""

    async def analyze_images(
        self,
        images_data: List[Dict],
        description: Optional[str] = None,
        address: Optional[str] = None
    ) -> dict:
        """
        Analyze multiple images for environmental violations with spam detection

        Args:
            images_data: List of dicts with 'data', 'type', 'filename' keys
            description: User description of the violation
            address: Address where violation occurred

        Returns:
            Analysis result with violation type, fine estimate, reward, and spam check
        """
        logger.info(f"Starting analysis of {len(images_data)} images")

        # Step 1: Spam check
        spam_result = await self._check_spam(images_data, description)
        if spam_result.get('is_spam', False):
            logger.warning(f"Spam detected: {spam_result.get('spam_reason')}")
            return {
                "success": False,
                "is_spam": True,
                "spam_reason": spam_result.get('spam_reason', 'Контент определён как спам'),
                "violation_detected": False
            }

        # Step 2: Main violation analysis
        logger.info("Spam check passed, proceeding with violation analysis")
        return await self._analyze_violation(images_data, description, address)

    async def _check_spam(self, images_data: List[Dict], description: Optional[str]) -> dict:
        """Check if the submission is spam"""
        logger.info("Running spam check")

        # Build content with all images
        content = []
        for i, img in enumerate(images_data[:5]):  # Check first 5 images for spam
            image_base64 = base64.b64encode(img['data']).decode('utf-8')
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": img['type'],
                    "data": image_base64
                }
            })

        prompt = f"Проверь эти {len(images_data)} фотографий на спам.\n"
        if description:
            prompt += f"Описание от пользователя: {description}\n"
        prompt += "\nЭто спам или валидная жалоба на экологическое нарушение?"

        content.append({"type": "text", "text": prompt})

        try:
            url = f"{self.endpoint}/model/{self.model_id}/invoke"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.bearer_token}",
                "Accept": "application/json"
            }

            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 512,
                "system": self.spam_check_prompt,
                "messages": [{"role": "user", "content": content}]
            }

            response = requests.post(url, headers=headers, json=body, timeout=30)
            response.raise_for_status()

            response_body = response.json()
            result_text = response_body['content'][0]['text']

            # Parse JSON response
            try:
                # Find JSON in response
                import re
                json_match = re.search(r'\{[^}]+\}', result_text)
                if json_match:
                    spam_data = json.loads(json_match.group())
                    return spam_data
            except json.JSONDecodeError:
                pass

            # If can't parse, assume not spam
            return {"is_spam": False}

        except Exception as e:
            logger.error(f"Spam check error: {e}")
            # If spam check fails, allow through
            return {"is_spam": False}

    async def _analyze_violation(
        self,
        images_data: List[Dict],
        description: Optional[str],
        address: Optional[str]
    ) -> dict:
        """Main violation analysis"""
        logger.info("Running violation analysis")

        # Build content with all images
        content = []
        for img in images_data:
            image_base64 = base64.b64encode(img['data']).decode('utf-8')
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": img['type'],
                    "data": image_base64
                }
            })

        content.append({
            "type": "text",
            "text": self._build_analysis_prompt(description, address, len(images_data))
        })

        try:
            url = f"{self.endpoint}/model/{self.model_id}/invoke"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.bearer_token}",
                "Accept": "application/json"
            }

            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2048,
                "system": self.system_prompt,
                "messages": [{"role": "user", "content": content}]
            }

            response = requests.post(url, headers=headers, json=body, timeout=60)
            response.raise_for_status()

            response_body = response.json()
            analysis_text = response_body['content'][0]['text']

            logger.info(f"AI analysis text length: {len(analysis_text)} chars")

            result = self._parse_analysis(analysis_text)
            result['raw_analysis'] = analysis_text
            result['is_spam'] = False
            result['address'] = address
            result['images_count'] = len(images_data)

            return result

        except Exception as e:
            logger.error(f"Error during AI analysis: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "violation_detected": False,
                "is_spam": False
            }

    def _build_analysis_prompt(self, description: Optional[str] = None, address: Optional[str] = None, images_count: int = 1) -> str:
        """Build the analysis prompt for the AI"""
        prompt = f"Проанализируй эти {images_count} изображений на наличие экологических нарушений.\n\n"

        if description:
            prompt += f"Описание от заявителя: {description}\n\n"

        if address:
            prompt += f"Адрес нарушения: {address}\n\n"

        prompt += """Предоставь анализ в следующем формате:

**ОБНАРУЖЕННОЕ НАРУШЕНИЕ:**
[Тип нарушения или "Нарушение не обнаружено"]

**СЕРЬЁЗНОСТЬ:**
[Низкая / Средняя / Высокая]

**ОЦЕНКА ШТРАФА:**
- Минимум: [сумма] сум
- Максимум: [сумма] сум

**ВАШЕ ВОЗНАГРАЖДЕНИЕ (15%):**
- Минимум: [сумма] сум
- Максимум: [сумма] сум

**ОПИСАНИЕ:**
[Краткое описание того, что видно на фото]

**РЕКОМЕНДАЦИИ:**
[Советы по подаче жалобы]

**ВЕРОЯТНОСТЬ ПОДТВЕРЖДЕНИЯ:**
[Процент] - [пояснение]
"""
        return prompt

    def _parse_analysis(self, analysis_text: str) -> dict:
        """Parse the AI analysis to extract structured data"""
        result = {
            "success": True,
            "violation_detected": True
        }

        # Check if no violation detected
        if "не обнаружено" in analysis_text.lower() or "нет нарушения" in analysis_text.lower():
            result["violation_detected"] = False
            result["message"] = "Экологическое нарушение не обнаружено на изображении"
            return result

        # Try to determine violation type
        for key, violation in VIOLATIONS.items():
            if violation["name_ru"].lower() in analysis_text.lower():
                result["violation_type"] = key
                result["violation_name"] = violation["name_ru"]
                result["fine_range"] = {
                    "min": violation["fine_min"],
                    "max": violation["fine_max"]
                }
                result["reward_range"] = {
                    "min": calculate_reward(violation["fine_min"]),
                    "max": calculate_reward(violation["fine_max"])
                }
                break

        # Determine severity
        if "высокая" in analysis_text.lower():
            result["severity"] = "high"
        elif "средняя" in analysis_text.lower():
            result["severity"] = "medium"
        else:
            result["severity"] = "low"

        return result


# Singleton instance
_agent_instance = None

def get_agent() -> ComplaintAnalyzerAgent:
    """Get or create the agent instance"""
    global _agent_instance
    if _agent_instance is None:
        logger.info("Creating new ComplaintAnalyzerAgent instance")
        _agent_instance = ComplaintAnalyzerAgent()
    return _agent_instance
