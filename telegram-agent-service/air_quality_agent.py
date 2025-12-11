"""
Air Quality News Agent
Uses AWS Bedrock via Bearer Token
Model: Claude Haiku 4.5
"""

import os
import json
import logging
import time
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class AirQualityAgent:
    """AI Agent for detecting and rephrasing air quality news using AWS Bedrock"""

    def __init__(self):
        self.bearer_token = os.getenv('AWS_BEARER_TOKEN_BEDROCK', '')
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        # Use cross-region inference profile for Claude 4.5 Haiku
        self.model_id = 'us.anthropic.claude-haiku-4-5-20251001-v1:0'

        # Bedrock endpoint
        self.endpoint = f"https://bedrock-runtime.{self.region}.amazonaws.com/model/{self.model_id}/invoke"

        if not self.bearer_token:
            raise ValueError("AWS_BEARER_TOKEN_BEDROCK not set in environment")

        logger.info(f"Air Quality Agent initialized with {self.model_id}")

    def _call_claude(self, prompt: str, system_prompt: str = None, max_tokens: int = 1024) -> Optional[str]:
        """Call Claude via AWS Bedrock HTTP API with Bearer token"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7
                }

                if system_prompt:
                    body["system"] = system_prompt

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.bearer_token}",
                    "Accept": "application/json"
                }

                response = requests.post(
                    self.endpoint,
                    headers=headers,
                    json=body,
                    timeout=60
                )

                if response.status_code == 429:
                    wait_time = 5 * (attempt + 1)
                    logger.warning(f"Rate limited. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue

                if response.status_code != 200:
                    logger.error(f"Bedrock API error: {response.status_code} - {response.text}")
                    return None

                response_data = response.json()

                # Add delay between requests to avoid rate limiting
                time.sleep(1)

                return response_data['content'][0]['text']

            except Exception as e:
                logger.error(f"Claude API error: {e}")
                return None

        logger.error("Max retries exceeded")
        return None

    def is_air_quality_news(self, text: str) -> Dict[str, Any]:
        """
        Determine if the text is about air quality
        """

        system_prompt = """Ты эксперт по качеству воздуха и экологии.
Твоя задача - определить, является ли текст новостью или информацией о качестве воздуха."""

        prompt = f"""Проанализируй следующий текст и определи, является ли он новостью о качестве воздуха.

Текст считается новостью о качестве воздуха, если содержит информацию о:
- Индексе качества воздуха (AQI, ИКВ)
- Загрязнении воздуха, смоге
- Измерениях PM2.5, PM10, озона и других загрязнителей
- Рекомендациях по защите от загрязнения воздуха
- Экологической обстановке связанной с воздухом
- Метеорологических условиях, влияющих на качество воздуха

ТЕКСТ:
{text}

Ответь СТРОГО в JSON формате:
{{
    "is_air_quality_news": true/false,
    "confidence": 0.0-1.0,
    "reason": "краткое объяснение"
}}"""

        response = self._call_claude(prompt, system_prompt, max_tokens=512)

        if not response:
            return {
                'is_air_quality_news': False,
                'confidence': 0.0,
                'reason': 'API error'
            }

        try:
            # Strip markdown code blocks if present
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()

            result = json.loads(cleaned_response)
            return result
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON response: {response}")
            keywords = ['aqi', 'воздух', 'havo', 'смог', 'загрязнение',
                       'ifloslanish', 'air quality', 'pm2.5', 'pm10']
            has_keywords = any(kw.lower() in text.lower() for kw in keywords)

            return {
                'is_air_quality_news': has_keywords,
                'confidence': 0.6 if has_keywords else 0.3,
                'reason': 'Fallback keyword detection'
            }

    def rephrase_news(self, original_text: str, language: str = 'auto') -> Optional[str]:
        """
        Rephrase air quality news while preserving facts
        """

        system_prompt = """Ты профессиональный новостной редактор.
Твоя задача - переписать новость своими словами, сохранив все факты и цифры."""

        prompt = f"""Перефразируй эту новость про качество воздуха.

ВАЖНЫЕ ТРЕБОВАНИЯ:
1. Сохрани ВСЕ числовые данные (AQI, PM2.5, температура и т.д.)
2. Сохрани названия районов и локаций
3. Сохрани рекомендации для населения
4. Пиши на том же языке, что и оригинал
5. Сделай текст уникальным, но информативным
6. Текст должен быть 3-5 предложений
7. Не добавляй хэштеги или эмодзи
8. Не добавляй источники или ссылки

ОРИГИНАЛЬНЫЙ ТЕКСТ:
{original_text}

ПЕРЕФОРМУЛИРОВАННАЯ ВЕРСИЯ:"""

        response = self._call_claude(prompt, system_prompt, max_tokens=1024)

        if response:
            response = response.strip()
            unwanted_prefixes = [
                'Переформулированная версия:',
                'Перефразированная версия:',
                'Вот переформулированная версия:',
                'Here is the rephrased version:'
            ]
            for prefix in unwanted_prefixes:
                if response.startswith(prefix):
                    response = response[len(prefix):].strip()

        return response

    def translate_text(self, text: str, target_language: str) -> Optional[str]:
        """
        Translate text to target language (uz or en)
        """
        lang_names = {
            'uz': "O'zbek tilida (lotin alifbosida)",
            'en': 'English'
        }

        system_prompt = f"""You are a professional translator specializing in environmental and air quality news.
Translate the text accurately to {lang_names.get(target_language, target_language)}."""

        prompt = f"""Translate the following air quality news text to {lang_names.get(target_language, target_language)}.

IMPORTANT REQUIREMENTS:
1. Keep ALL numerical data (AQI, PM2.5, temperature, etc.) exactly as is
2. Keep location names accurate
3. Preserve the meaning and tone
4. Output ONLY the translation, nothing else

TEXT TO TRANSLATE:
{text}

TRANSLATION:"""

        response = self._call_claude(prompt, system_prompt, max_tokens=1024)

        if response:
            response = response.strip()
            # Remove any prefixes the model might add
            prefixes = ['Translation:', 'TRANSLATION:', 'Tarjima:', "Tarjima:"]
            for prefix in prefixes:
                if response.startswith(prefix):
                    response = response[len(prefix):].strip()

        return response

    def analyze_and_rephrase(self, text: str, min_confidence: float = 0.6) -> Optional[str]:
        """
        Complete pipeline: check if air quality news, then rephrase
        """

        analysis = self.is_air_quality_news(text)

        logger.info(f"Analysis: is_air_quality_news={analysis['is_air_quality_news']}, "
                   f"confidence={analysis['confidence']}, reason={analysis['reason']}")

        if not analysis['is_air_quality_news'] or analysis['confidence'] < min_confidence:
            logger.info(f"Text rejected: confidence {analysis['confidence']} < {min_confidence}")
            return None

        rephrased = self.rephrase_news(text)

        if not rephrased:
            logger.warning("Rephrasing failed")
            return None

        logger.info(f"Successfully rephrased air quality news (confidence: {analysis['confidence']})")
        return rephrased


# Singleton instance
_agent_instance = None

def get_agent() -> AirQualityAgent:
    """Get or create singleton agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = AirQualityAgent()
    return _agent_instance
