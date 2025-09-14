"""
Advanced Multi-Modal Reasoning Service
Provides chart-to-text intelligence, visual-text cross-referencing, and multi-modal search
"""

import asyncio
import logging
import time
import uuid
import json
import base64
import io
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import cv2
import google.generativeai as genai
# import anthropic  # Using Gemini instead

from app.config import settings
from app.models.schemas import (
    SearchResult,
    Citation,
    DocumentImage,
    DocumentChunk,
    SourceType,
    CitationType
)

logger = logging.getLogger(__name__)

class ChartAnalysis:
    """Analysis result for charts and graphs"""
    def __init__(self, chart_type: str, data_insights: Dict, text_content: str, confidence: float):
        self.chart_type = chart_type
        self.data_insights = data_insights
        self.text_content = text_content
        self.confidence = confidence
        self.queryable_facts = []

class VisualTextLink:
    """Link between visual elements and text explanations"""
    def __init__(self, visual_id: str, text_chunks: List[str], relationship: str, confidence: float):
        self.visual_id = visual_id
        self.text_chunks = text_chunks
        self.relationship = relationship
        self.confidence = confidence

class MultiModalService:
    """Advanced multi-modal reasoning and analysis service"""

    def __init__(self):
        self.genai_client = None
        self.claude_client = None
        self.chart_cache = {}  # Cache for chart analysis
        self.visual_text_links = {}  # Visual-text relationships
        self._initialize_ai_clients()

    def _initialize_ai_clients(self):
        """Initialize AI clients for multi-modal analysis"""
        try:
            if settings.ai_provider == "gemini" and settings.gemini_api_key:
                genai.configure(api_key=settings.gemini_api_key)
                self.genai_client = genai.GenerativeModel("gemini-1.5-pro-vision-latest")
                logger.info("Gemini Vision client initialized for multi-modal service")
            elif settings.ai_provider == "claude" and settings.claude_api_key:
                self.claude_client = anthropic.AsyncAnthropic(api_key=settings.claude_api_key)
                logger.info("Claude Vision client initialized for multi-modal service")
        except Exception as e:
            logger.error(f"Failed to initialize AI clients: {e}")

    async def analyze_chart_to_text(self, image: Image.Image, context: str = "") -> ChartAnalysis:
        """
        Convert charts/graphs into comprehensive queryable insights

        Args:
            image: PIL Image of the chart
            context: Additional context about the document

        Returns:
            ChartAnalysis with extracted data and insights
        """
        try:
            # Step 1: Identify chart type and structure
            chart_metadata = await self._identify_chart_structure(image)

            # Step 2: Extract data points and values
            data_insights = await self._extract_chart_data(image, chart_metadata)

            # Step 3: Generate queryable text representation
            text_content = await self._generate_chart_text_description(
                image, chart_metadata, data_insights, context
            )

            # Step 4: Create searchable facts
            queryable_facts = await self._extract_queryable_facts(
                chart_metadata, data_insights, text_content
            )

            analysis = ChartAnalysis(
                chart_type=chart_metadata.get("type", "unknown"),
                data_insights=data_insights,
                text_content=text_content,
                confidence=chart_metadata.get("confidence", 0.5)
            )
            analysis.queryable_facts = queryable_facts

            # Cache the analysis
            chart_id = str(uuid.uuid4())
            self.chart_cache[chart_id] = analysis

            logger.info(f"Chart analysis completed: {chart_metadata.get('type')} with {len(queryable_facts)} facts")
            return analysis

        except Exception as e:
            logger.error(f"Chart analysis failed: {e}")
            return ChartAnalysis("unknown", {}, "Chart analysis failed", 0.0)

    async def _identify_chart_structure(self, image: Image.Image) -> Dict[str, Any]:
        """Identify chart type and structural elements"""
        try:
            prompt = """Analyze this chart/graph image and identify:

1. Chart Type: (bar_chart, line_chart, pie_chart, scatter_plot, histogram, box_plot, area_chart, etc.)
2. Title: Extract the main title
3. Axes: Identify X and Y axis labels and units
4. Legend: Extract legend items and colors
5. Data Series: Identify different data series or categories
6. Scale: Determine the scale/range of data
7. Annotations: Any text annotations or callouts

Return your analysis in this JSON format:
{
    "type": "chart_type",
    "title": "chart title",
    "x_axis": {"label": "x label", "unit": "unit", "range": [min, max]},
    "y_axis": {"label": "y label", "unit": "unit", "range": [min, max]},
    "legend": ["item1", "item2"],
    "data_series": ["series1", "series2"],
    "annotations": ["text1", "text2"],
    "confidence": 0.9
}"""

            if settings.ai_provider == "gemini" and self.genai_client:
                response = await self._analyze_with_gemini(image, prompt)
            elif settings.ai_provider == "claude" and self.claude_client:
                response = await self._analyze_with_claude(image, prompt)
            else:
                return {"type": "unknown", "confidence": 0.0}

            # Try to parse JSON response
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Fallback to basic analysis
                return {
                    "type": "chart",
                    "title": "Unknown Chart",
                    "confidence": 0.3,
                    "raw_response": response
                }

        except Exception as e:
            logger.error(f"Chart structure identification failed: {e}")
            return {"type": "unknown", "confidence": 0.0}

    async def _extract_chart_data(self, image: Image.Image, metadata: Dict) -> Dict[str, Any]:
        """Extract specific data points and values from the chart"""
        try:
            chart_type = metadata.get("type", "unknown")

            prompt = f"""Extract specific data values from this {chart_type}:

1. Data Points: Extract all visible data points with their values
2. Trends: Identify increasing/decreasing trends
3. Comparisons: Note highest/lowest values and comparisons
4. Key Statistics: Calculate or identify key metrics (averages, totals, etc.)
5. Relationships: Identify correlations or patterns

Format your response as JSON:
{{
    "data_points": [
        {{"category": "name", "value": number, "series": "series_name"}},
        ...
    ],
    "trends": ["trend1", "trend2"],
    "key_statistics": {{
        "highest": {{"category": "name", "value": number}},
        "lowest": {{"category": "name", "value": number}},
        "average": number,
        "total": number
    }},
    "insights": ["insight1", "insight2"]
}}

Be precise with numbers and specific with categories."""

            if settings.ai_provider == "gemini" and self.genai_client:
                response = await self._analyze_with_gemini(image, prompt)
            elif settings.ai_provider == "claude" and self.claude_client:
                response = await self._analyze_with_claude(image, prompt)
            else:
                return {}

            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Extract key insights from raw text
                return {"raw_analysis": response, "data_points": []}

        except Exception as e:
            logger.error(f"Chart data extraction failed: {e}")
            return {}

    async def _generate_chart_text_description(self, image: Image.Image, metadata: Dict,
                                             data_insights: Dict, context: str) -> str:
        """Generate comprehensive text description of the chart"""
        try:
            chart_type = metadata.get("type", "chart")
            title = metadata.get("title", "Untitled Chart")

            prompt = f"""Create a comprehensive text description of this {chart_type} titled "{title}".

Context: {context}

Include:
1. Chart overview and purpose
2. All visible data with specific values
3. Key trends and patterns
4. Important comparisons and insights
5. Business implications (if applicable)

Make the description searchable and informative. Someone should be able to understand the chart completely from your description alone. Use specific numbers and be detailed about what the chart shows.

Description:"""

            if settings.ai_provider == "gemini" and self.genai_client:
                description = await self._analyze_with_gemini(image, prompt)
            elif settings.ai_provider == "claude" and self.claude_client:
                description = await self._analyze_with_claude(image, prompt)
            else:
                description = f"Chart of type {chart_type} with title {title}"

            # Enhance with extracted data
            if data_insights.get("key_statistics"):
                stats = data_insights["key_statistics"]
                description += f"\n\nKey Statistics: "
                if "highest" in stats:
                    description += f"Highest value: {stats['highest'].get('value')} "
                if "lowest" in stats:
                    description += f"Lowest value: {stats['lowest'].get('value')} "
                if "average" in stats:
                    description += f"Average: {stats['average']} "

            return description

        except Exception as e:
            logger.error(f"Chart text generation failed: {e}")
            return "Chart description generation failed"

    async def _extract_queryable_facts(self, metadata: Dict, data_insights: Dict,
                                     text_content: str) -> List[str]:
        """Extract specific queryable facts from chart analysis"""
        facts = []

        try:
            # Add chart type fact
            if metadata.get("type"):
                facts.append(f"This is a {metadata['type']}")

            # Add title fact
            if metadata.get("title"):
                facts.append(f"Chart title: {metadata['title']}")

            # Add data point facts
            if data_insights.get("data_points"):
                for point in data_insights["data_points"][:10]:  # Limit to avoid too many facts
                    if "category" in point and "value" in point:
                        facts.append(f"{point['category']}: {point['value']}")

            # Add trend facts
            if data_insights.get("trends"):
                for trend in data_insights["trends"]:
                    facts.append(f"Trend: {trend}")

            # Add statistical facts
            stats = data_insights.get("key_statistics", {})
            if "highest" in stats and stats["highest"]:
                facts.append(f"Highest value: {stats['highest'].get('value')} ({stats['highest'].get('category')})")
            if "lowest" in stats and stats["lowest"]:
                facts.append(f"Lowest value: {stats['lowest'].get('value')} ({stats['lowest'].get('category')})")
            if "average" in stats:
                facts.append(f"Average value: {stats['average']}")

            # Add insight facts
            if data_insights.get("insights"):
                facts.extend(data_insights["insights"])

        except Exception as e:
            logger.error(f"Fact extraction failed: {e}")

        return facts

    async def create_visual_text_links(self, images: List[DocumentImage],
                                     text_chunks: List[DocumentChunk]) -> List[VisualTextLink]:
        """
        Create cross-references between visual elements and text explanations
        """
        links = []

        try:
            for image in images:
                # Find related text chunks (same page or nearby pages)
                related_chunks = [
                    chunk for chunk in text_chunks
                    if abs(chunk.page_number - image.page_number) <= 1
                ]

                if not related_chunks:
                    continue

                # Analyze relationships using AI
                relationships = await self._analyze_visual_text_relationships(
                    image, related_chunks
                )

                for relationship in relationships:
                    link = VisualTextLink(
                        visual_id=image.id,
                        text_chunks=relationship["text_chunks"],
                        relationship=relationship["relationship"],
                        confidence=relationship["confidence"]
                    )
                    links.append(link)

                    # Cache the link
                    self.visual_text_links[image.id] = link

            logger.info(f"Created {len(links)} visual-text links")
            return links

        except Exception as e:
            logger.error(f"Visual-text linking failed: {e}")
            return []

    async def _analyze_visual_text_relationships(self, image: DocumentImage,
                                               text_chunks: List[DocumentChunk]) -> List[Dict]:
        """Analyze relationships between an image and surrounding text"""
        try:
            # Combine text content
            text_content = "\n".join([chunk.content for chunk in text_chunks])

            prompt = f"""Analyze the relationship between this image and the surrounding text:

Text Content:
{text_content}

Image Description: {image.description or 'No description available'}
Image Type: {image.image_type}

Identify:
1. How the image relates to the text (illustration, example, data_visualization, etc.)
2. Which specific text passages explain or reference the image
3. What insights the image provides that complement the text
4. Confidence level of the relationship

Return JSON format:
[
    {{
        "relationship": "relationship_type",
        "text_chunks": ["relevant_text_snippet1", "relevant_text_snippet2"],
        "confidence": 0.8,
        "explanation": "why this relationship exists"
    }}
]"""

            if settings.ai_provider == "gemini" and self.genai_client:
                response = await self._analyze_with_gemini_text_only(prompt)
            elif settings.ai_provider == "claude" and self.claude_client:
                response = await self._analyze_with_claude_text_only(prompt)
            else:
                return []

            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return [{
                    "relationship": "general",
                    "text_chunks": [chunk.content[:100] for chunk in text_chunks[:2]],
                    "confidence": 0.3,
                    "explanation": "Basic proximity relationship"
                }]

        except Exception as e:
            logger.error(f"Visual-text relationship analysis failed: {e}")
            return []

    async def generate_smart_image_captions(self, image: Image.Image,
                                          context: str = "") -> Dict[str, str]:
        """
        Generate detailed, searchable descriptions of technical diagrams
        """
        try:
            # Generate multiple types of captions
            captions = {}

            # 1. Technical description
            technical_prompt = f"""Provide a detailed technical description of this image.

Context: {context}

Focus on:
- Technical elements and components
- Relationships and connections
- Measurements, labels, and specifications
- Functional aspects
- Any technical terminology visible

Technical Description:"""

            captions["technical"] = await self._generate_caption(image, technical_prompt)

            # 2. Searchable keywords
            keyword_prompt = f"""Extract searchable keywords and phrases from this image.

List important terms that someone might search for:
- Technical terms
- Component names
- Process names
- Industry-specific terminology
- Visible text and labels

Keywords (comma-separated):"""

            captions["keywords"] = await self._generate_caption(image, keyword_prompt)

            # 3. Functional description
            functional_prompt = f"""Describe what this image shows in terms of function and purpose.

Focus on:
- What the image demonstrates or illustrates
- The purpose or function being shown
- How components work together
- Process flows or sequences

Functional Description:"""

            captions["functional"] = await self._generate_caption(image, functional_prompt)

            return captions

        except Exception as e:
            logger.error(f"Smart captioning failed: {e}")
            return {"error": "Caption generation failed"}

    async def multi_modal_search(self, query: str, text_results: List[SearchResult],
                                image_results: List[DocumentImage]) -> List[SearchResult]:
        """
        Enhanced search across text, images, tables, and charts simultaneously
        """
        try:
            enhanced_results = []

            # 1. Enhance text results with visual context
            for result in text_results:
                enhanced_result = await self._enhance_text_with_visual_context(result, image_results)
                enhanced_results.append(enhanced_result)

            # 2. Search through cached chart analyses
            chart_results = await self._search_chart_analyses(query)
            enhanced_results.extend(chart_results)

            # 3. Search through visual-text links
            link_results = await self._search_visual_text_links(query)
            enhanced_results.extend(link_results)

            # 4. Rank results by multi-modal relevance
            ranked_results = await self._rank_multimodal_results(query, enhanced_results)

            logger.info(f"Multi-modal search returned {len(ranked_results)} enhanced results")
            return ranked_results

        except Exception as e:
            logger.error(f"Multi-modal search failed: {e}")
            return text_results  # Fallback to original results

    async def _enhance_text_with_visual_context(self, text_result: SearchResult,
                                              image_results: List[DocumentImage]) -> SearchResult:
        """Enhance text search results with related visual context"""
        try:
            # Find images from the same document/page
            related_images = [
                img for img in image_results
                if img.document_id == text_result.metadata.get("document_id") and
                abs(img.page_number - text_result.metadata.get("page_number", 0)) <= 1
            ]

            if related_images:
                # Add visual context to the result
                visual_context = []
                for img in related_images[:3]:  # Limit to 3 images
                    if img.description:
                        visual_context.append(f"Related image: {img.description}")
                    if img.image_type in ["chart", "graph", "diagram"]:
                        # Check if we have chart analysis for this image
                        chart_analysis = self._get_chart_analysis_by_image_id(img.id)
                        if chart_analysis:
                            visual_context.append(f"Chart data: {chart_analysis.text_content[:200]}")

                if visual_context:
                    text_result.content += "\n\nVisual Context: " + " ".join(visual_context)
                    text_result.metadata["visual_enhancements"] = len(visual_context)

            return text_result

        except Exception as e:
            logger.error(f"Visual context enhancement failed: {e}")
            return text_result

    async def _search_chart_analyses(self, query: str) -> List[SearchResult]:
        """Search through cached chart analyses"""
        results = []

        try:
            for chart_id, analysis in self.chart_cache.items():
                # Check if query matches chart content
                relevance = await self._calculate_text_relevance(
                    query, analysis.text_content
                )

                if relevance > 0.3:  # Threshold for relevance
                    result = SearchResult(
                        id=f"chart_{chart_id}",
                        title=f"{analysis.chart_type.title()} Chart",
                        content=analysis.text_content,
                        source_type=SourceType.IMAGE,
                        url=None,
                        confidence_score=relevance * analysis.confidence,
                        metadata={
                            "chart_type": analysis.chart_type,
                            "data_insights": analysis.data_insights,
                            "queryable_facts": analysis.queryable_facts
                        }
                    )
                    results.append(result)

        except Exception as e:
            logger.error(f"Chart search failed: {e}")

        return results

    async def _search_visual_text_links(self, query: str) -> List[SearchResult]:
        """Search through visual-text relationship links"""
        results = []

        try:
            for visual_id, link in self.visual_text_links.items():
                # Check relevance to query
                combined_text = " ".join(link.text_chunks)
                relevance = await self._calculate_text_relevance(query, combined_text)

                if relevance > 0.3:
                    result = SearchResult(
                        id=f"link_{visual_id}",
                        title=f"Visual-Text Link ({link.relationship})",
                        content=f"Relationship: {link.relationship}. " + combined_text[:300],
                        source_type=SourceType.IMAGE,
                        url=None,
                        confidence_score=relevance * link.confidence,
                        metadata={
                            "visual_id": visual_id,
                            "relationship": link.relationship,
                            "link_confidence": link.confidence
                        }
                    )
                    results.append(result)

        except Exception as e:
            logger.error(f"Visual link search failed: {e}")

        return results

    async def _rank_multimodal_results(self, query: str,
                                     results: List[SearchResult]) -> List[SearchResult]:
        """Rank results considering multi-modal relevance"""
        try:
            # Enhanced ranking considering:
            # 1. Text relevance
            # 2. Visual context bonus
            # 3. Multi-modal completeness

            for result in results:
                base_score = result.confidence_score

                # Bonus for visual enhancements
                if "visual_enhancements" in result.metadata:
                    base_score *= 1.2

                # Bonus for chart data
                if "chart_type" in result.metadata:
                    base_score *= 1.3

                # Bonus for visual-text links
                if "relationship" in result.metadata:
                    base_score *= 1.1

                result.confidence_score = min(base_score, 1.0)

            # Sort by enhanced confidence score
            results.sort(key=lambda x: x.confidence_score, reverse=True)
            return results

        except Exception as e:
            logger.error(f"Multi-modal ranking failed: {e}")
            return results

    # Helper methods for AI analysis
    async def _analyze_with_gemini(self, image: Image.Image, prompt: str) -> str:
        """Analyze image with Gemini Vision"""
        try:
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.genai_client.generate_content([
                    prompt,
                    {"mime_type": "image/png", "data": img_byte_arr}
                ])
            )

            return response.text if response.text else "No response generated"

        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            return "Analysis failed"

    async def _analyze_with_claude(self, image: Image.Image, prompt: str) -> str:
        """Analyze image with Claude Vision"""
        try:
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            img_base64 = base64.b64encode(img_byte_arr).decode()

            message = await self.claude_client.messages.create(
                model=settings.claude_vision_model,
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": [{
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": img_base64
                        }
                    }, {
                        "type": "text",
                        "text": prompt
                    }]
                }]
            )

            return message.content[0].text if message.content else "No response generated"

        except Exception as e:
            logger.error(f"Claude analysis failed: {e}")
            return "Analysis failed"

    async def _analyze_with_gemini_text_only(self, prompt: str) -> str:
        """Analyze text with Gemini"""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: genai.GenerativeModel("gemini-1.5-pro").generate_content(prompt)
            )
            return response.text if response.text else "No response"
        except Exception as e:
            logger.error(f"Gemini text analysis failed: {e}")
            return "Analysis failed"

    async def _analyze_with_claude_text_only(self, prompt: str) -> str:
        """Analyze text with Claude"""
        try:
            message = await self.claude_client.messages.create(
                model=settings.claude_chat_model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text if message.content else "No response"
        except Exception as e:
            logger.error(f"Claude text analysis failed: {e}")
            return "Analysis failed"

    async def _generate_caption(self, image: Image.Image, prompt: str) -> str:
        """Generate caption for image"""
        if settings.ai_provider == "gemini" and self.genai_client:
            return await self._analyze_with_gemini(image, prompt)
        elif settings.ai_provider == "claude" and self.claude_client:
            return await self._analyze_with_claude(image, prompt)
        else:
            return "Caption generation not available"

    async def _calculate_text_relevance(self, query: str, text: str) -> float:
        """Calculate relevance between query and text (simple implementation)"""
        try:
            query_words = set(query.lower().split())
            text_words = set(text.lower().split())
            overlap = len(query_words.intersection(text_words))
            return overlap / max(len(query_words), 1)
        except Exception:
            return 0.0

    def _get_chart_analysis_by_image_id(self, image_id: str) -> Optional[ChartAnalysis]:
        """Get chart analysis by image ID"""
        for analysis in self.chart_cache.values():
            if hasattr(analysis, 'image_id') and analysis.image_id == image_id:
                return analysis
        return None

    async def process_uploaded_images_for_multimodal(self, images: List[DocumentImage],
                                                   text_chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """
        Process uploaded images for multi-modal analysis

        Returns analysis results that can be indexed for search
        """
        try:
            results = {
                "chart_analyses": [],
                "visual_text_links": [],
                "enhanced_captions": [],
                "searchable_content": []
            }

            for image in images:
                # Load image for analysis
                if image.image_url:
                    # In production, load from storage URL
                    # For now, skip if we can't load the image
                    continue

                # Analyze charts if detected
                if image.image_type in ["chart", "graph", "diagram"]:
                    # Would need actual image data here
                    # chart_analysis = await self.analyze_chart_to_text(pil_image, context)
                    # results["chart_analyses"].append(chart_analysis)
                    pass

                # Generate enhanced captions
                # enhanced_captions = await self.generate_smart_image_captions(pil_image, context)
                # results["enhanced_captions"].append(enhanced_captions)

            # Create visual-text links
            visual_links = await self.create_visual_text_links(images, text_chunks)
            results["visual_text_links"] = visual_links

            return results

        except Exception as e:
            logger.error(f"Multi-modal processing failed: {e}")
            return {}