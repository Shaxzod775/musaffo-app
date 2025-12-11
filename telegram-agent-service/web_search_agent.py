"""
Web Search Agent for Air Quality News
Uses AWS Bedrock via Bearer Token (same as air_quality_agent.py)
Uses external search APIs for web search (Tavily, SerpAPI, or Google)
"""

import os
import json
import asyncio
import logging
import time
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class WebSearchNewsAgent:
    """AI Agent that searches the web for air quality news in Uzbekistan"""

    def __init__(self):
        self.bearer_token = os.getenv('AWS_BEARER_TOKEN_BEDROCK', '')
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        # Use Claude Sonnet for better quality
        self.model_id = 'us.anthropic.claude-sonnet-4-20250514-v1:0'
        self.endpoint = f"https://bedrock-runtime.{self.region}.amazonaws.com/model/{self.model_id}/invoke"

        # Search API keys
        self.tavily_api_key = os.getenv('TAVILY_API_KEY', '')
        self.serp_api_key = os.getenv('SERP_API_KEY', '')
        self.google_api_key = os.getenv('GOOGLE_API_KEY', '')
        self.google_cx = os.getenv('GOOGLE_CX', '')  # Custom Search Engine ID

        if not self.bearer_token:
            raise ValueError("AWS_BEARER_TOKEN_BEDROCK not set in environment")

        logger.info(f"WebSearchNewsAgent initialized with {self.model_id}")

    def _call_claude(self, prompt: str, system_prompt: str = None, max_tokens: int = 2048) -> Optional[str]:
        """Call Claude via AWS Bedrock HTTP API with Bearer token"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "messages": [{"role": "user", "content": prompt}],
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
                    timeout=90
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
                time.sleep(1)
                return response_data['content'][0]['text']

            except Exception as e:
                logger.error(f"Bedrock API error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(3)
                continue

        logger.error("Max retries exceeded")
        return None

    def _search_tavily(self, query: str) -> List[Dict[str, Any]]:
        """Search using Tavily API"""
        if not self.tavily_api_key:
            return []

        try:
            response = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self.tavily_api_key,
                    "query": query,
                    "search_depth": "advanced",
                    "include_images": True,
                    "max_results": 5
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                results = []
                for r in data.get('results', []):
                    results.append({
                        'title': r.get('title', ''),
                        'content': r.get('content', ''),
                        'url': r.get('url', ''),
                        'image': r.get('image', '')
                    })
                # Add images from separate field if available
                images = data.get('images', [])
                return results, images
            else:
                logger.error(f"Tavily API error: {response.status_code}")
        except Exception as e:
            logger.error(f"Tavily search error: {e}")

        return [], []

    def _search_serp(self, query: str) -> List[Dict[str, Any]]:
        """Search using SerpAPI"""
        if not self.serp_api_key:
            return [], []

        try:
            response = requests.get(
                "https://serpapi.com/search",
                params={
                    "api_key": self.serp_api_key,
                    "q": query,
                    "engine": "google",
                    "num": 5,
                    "hl": "ru"
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                results = []
                for r in data.get('organic_results', []):
                    results.append({
                        'title': r.get('title', ''),
                        'content': r.get('snippet', ''),
                        'url': r.get('link', ''),
                        'image': ''
                    })
                # Get images
                images = [img.get('original', '') for img in data.get('images_results', [])[:3]]
                return results, images
            else:
                logger.error(f"SerpAPI error: {response.status_code}")
        except Exception as e:
            logger.error(f"SerpAPI search error: {e}")

        return [], []

    def _search_google(self, query: str) -> List[Dict[str, Any]]:
        """Search using Google Custom Search API"""
        if not self.google_api_key or not self.google_cx:
            return [], []

        try:
            response = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "key": self.google_api_key,
                    "cx": self.google_cx,
                    "q": query,
                    "num": 5,
                    "lr": "lang_ru"
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                results = []
                images = []
                for r in data.get('items', []):
                    results.append({
                        'title': r.get('title', ''),
                        'content': r.get('snippet', ''),
                        'url': r.get('link', ''),
                        'image': ''
                    })
                    # Try to get image from pagemap
                    pagemap = r.get('pagemap', {})
                    if 'cse_image' in pagemap:
                        images.append(pagemap['cse_image'][0].get('src', ''))
                return results, images
            else:
                logger.error(f"Google API error: {response.status_code}")
        except Exception as e:
            logger.error(f"Google search error: {e}")

        return [], []

    def web_search(self, query: str) -> tuple:
        """
        Perform web search using available API
        Returns (results, images)
        """
        # Try Tavily first (best for news)
        results, images = self._search_tavily(query)
        if results:
            logger.info(f"Found {len(results)} results via Tavily")
            return results, images

        # Try SerpAPI
        results, images = self._search_serp(query)
        if results:
            logger.info(f"Found {len(results)} results via SerpAPI")
            return results, images

        # Try Google Custom Search
        results, images = self._search_google(query)
        if results:
            logger.info(f"Found {len(results)} results via Google")
            return results, images

        logger.warning("No search API available or no results found")
        return [], []

    def search_air_quality_news(self) -> List[Dict[str, Any]]:
        """
        Search web for latest air quality news in Uzbekistan
        Returns list of news items
        """

        # Search queries
        queries = [
            "качество воздуха Ташкент AQI сегодня",
            "загрязнение воздуха Узбекистан смог PM2.5",
            "air quality Tashkent Uzbekistan"
        ]

        all_results = []
        all_images = []

        for query in queries:
            results, images = self.web_search(query)
            all_results.extend(results)
            all_images.extend(images)
            if results:
                break  # Got results, no need for more queries
            time.sleep(1)

        if not all_results:
            # No search results - use fallback
            logger.warning("No search results, using fallback generation")
            return self._generate_fallback_news()

        # Use Claude to process search results into news format
        return self._process_search_results(all_results, all_images)

    def _process_search_results(self, results: List[Dict], images: List[str]) -> List[Dict[str, Any]]:
        """Use Claude to process search results into news format"""

        # Format results for Claude
        results_text = ""
        for i, r in enumerate(results[:5], 1):
            results_text += f"\n{i}. {r['title']}\n   URL: {r['url']}\n   Содержание: {r['content']}\n"

        system_prompt = """Ты профессиональный новостной редактор, специализирующийся на экологии и качестве воздуха.
Твоя задача - создать информативные новости на основе результатов поиска."""

        prompt = f"""На основе следующих результатов поиска создай 1-2 новости о качестве воздуха в Узбекистане.

РЕЗУЛЬТАТЫ ПОИСКА:
{results_text}

Создай новости в формате JSON:
{{
    "news": [
        {{
            "title": "Заголовок новости на русском (краткий, информативный)",
            "summary": "Содержание новости на русском (3-5 предложений). ОБЯЗАТЕЛЬНО сохрани все числовые данные: AQI, PM2.5, PM10, температуру и т.д. Добавь рекомендации для населения если есть.",
            "source": "Название источника",
            "source_url": "URL источника",
            "image_query": "Поисковый запрос для изображения на английском (например: 'Tashkent city smog air pollution')"
        }}
    ]
}}

ВАЖНО:
- Минимум 1 новость ОБЯЗАТЕЛЬНА
- Сохраняй ВСЕ числовые данные из источников
- Пиши на русском языке
- Если данных мало, добавь общие рекомендации по защите от загрязнения воздуха
- Не выдумывай цифры, используй только те что есть в источниках"""

        response = self._call_claude(prompt, system_prompt)

        if not response:
            return self._generate_fallback_news()

        news_list = self._parse_news_response(response)

        # Add found images to news
        if images and news_list:
            for i, news in enumerate(news_list):
                if i < len(images) and images[i]:
                    news['found_image_url'] = images[i]

        return news_list

    def _generate_fallback_news(self) -> List[Dict[str, Any]]:
        """Generate a fallback news item when no search results available"""

        system_prompt = """Ты эксперт по качеству воздуха в Узбекистане и Центральной Азии."""

        prompt = """Создай информативную новость о качестве воздуха в Ташкенте.

Используй типичные данные для зимнего периода в Ташкенте:
- AQI обычно от 100 до 200+ в зимние месяцы
- PM2.5 часто превышает норму ВОЗ
- Основные источники: отопление, транспорт, промышленность

Верни в формате JSON:
{
    "news": [
        {
            "title": "Заголовок на русском",
            "summary": "Содержание 3-5 предложений с типичными показателями и рекомендациями",
            "source": "Мониторинг качества воздуха",
            "source_url": "https://aqicn.org/city/tashkent/",
            "image_query": "Tashkent winter smog air pollution cityscape"
        }
    ]
}

ВАЖНО: Укажи что данные являются типичными для сезона и рекомендуй проверить актуальные показатели."""

        response = self._call_claude(prompt, system_prompt)

        if response:
            return self._parse_news_response(response)

        # Ultimate fallback
        return [{
            "title": "Качество воздуха в Ташкенте",
            "summary": "Рекомендуем следить за показателями качества воздуха в вашем районе. В зимний период уровень загрязнения часто повышается из-за отопительного сезона. При высоком уровне AQI рекомендуется ограничить время на улице и использовать маски.",
            "source": "Мониторинг качества воздуха",
            "source_url": "https://aqicn.org/city/tashkent/",
            "image_query": "Tashkent air pollution smog"
        }]

    def _parse_news_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse news from Claude response"""
        if not response:
            return []

        try:
            cleaned = response.strip()

            # Extract JSON from response
            if '```json' in cleaned:
                start = cleaned.find('```json') + 7
                end = cleaned.find('```', start)
                cleaned = cleaned[start:end].strip()
            elif '```' in cleaned:
                start = cleaned.find('```') + 3
                end = cleaned.find('```', start)
                cleaned = cleaned[start:end].strip()
            elif '{' in cleaned:
                start = cleaned.find('{')
                end = cleaned.rfind('}') + 1
                cleaned = cleaned[start:end]

            data = json.loads(cleaned)

            if 'news' in data:
                return data['news']
            elif isinstance(data, list):
                return data
            else:
                return [data]

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON: {e}")
            return []

    def search_and_download_image(self, query: str, output_path: str, found_url: str = None) -> Optional[str]:
        """
        Search for an image and download it
        """
        # If we already have a URL from search results, try it first
        if found_url:
            downloaded = self._download_image(found_url, output_path)
            if downloaded:
                return downloaded

        # Try image search APIs
        try:
            # Unsplash (free)
            unsplash_key = os.getenv('UNSPLASH_ACCESS_KEY', '')
            if unsplash_key:
                response = requests.get(
                    "https://api.unsplash.com/search/photos",
                    params={"query": query, "per_page": 1},
                    headers={"Authorization": f"Client-ID {unsplash_key}"},
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get('results'):
                        image_url = data['results'][0]['urls']['regular']
                        return self._download_image(image_url, output_path)

            # Pexels (free)
            pexels_key = os.getenv('PEXELS_API_KEY', '')
            if pexels_key:
                response = requests.get(
                    "https://api.pexels.com/v1/search",
                    params={"query": query, "per_page": 1},
                    headers={"Authorization": pexels_key},
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get('photos'):
                        image_url = data['photos'][0]['src']['large']
                        return self._download_image(image_url, output_path)

            logger.warning("No image API configured or no images found")
            return None

        except Exception as e:
            logger.error(f"Image search error: {e}")
            return None

    def _download_image(self, url: str, output_path: str) -> Optional[str]:
        """Download image from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=30, stream=True, headers=headers)

            if response.status_code == 200:
                os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                logger.info(f"Downloaded image: {output_path}")
                return output_path

        except Exception as e:
            logger.error(f"Failed to download image from {url}: {e}")

        return None

    def get_news_with_images(self) -> List[Dict[str, Any]]:
        """
        Complete pipeline: search news, find images, download them
        Returns list of news with local image paths
        """
        os.makedirs('./media', exist_ok=True)

        # Search for news
        news_list = self.search_air_quality_news()

        if not news_list:
            logger.warning("No news found")
            return []

        logger.info(f"Found {len(news_list)} news items")

        # Process each news item
        processed_news = []

        for i, news in enumerate(news_list):
            try:
                timestamp = int(datetime.now().timestamp())
                news_item = {
                    'id': f"web_search_{timestamp}_{i}",
                    'channel': 'web_search',
                    'title': news.get('title', ''),
                    'text': news.get('summary', ''),
                    'source': news.get('source', 'Web'),
                    'source_url': news.get('source_url', ''),
                    'date': datetime.now().isoformat(),
                    'photo_path': None
                }

                # Try to download image
                image_query = news.get('image_query', 'Tashkent air pollution')
                found_image = news.get('found_image_url', '')
                photo_path = f"./media/web_search_{timestamp}_{i}.jpg"

                downloaded = self.search_and_download_image(image_query, photo_path, found_image)
                if downloaded:
                    news_item['photo_path'] = downloaded

                processed_news.append(news_item)
                time.sleep(1)

            except Exception as e:
                logger.error(f"Error processing news item: {e}")
                continue

        return processed_news


# Singleton instance
_web_search_agent = None


def get_web_search_agent() -> WebSearchNewsAgent:
    """Get or create singleton agent instance"""
    global _web_search_agent
    if _web_search_agent is None:
        _web_search_agent = WebSearchNewsAgent()
    return _web_search_agent


async def search_web_for_news() -> List[Dict[str, Any]]:
    """
    Convenience async function to search web for air quality news
    Returns list of news items ready for posting
    """
    agent = get_web_search_agent()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, agent.get_news_with_images)
