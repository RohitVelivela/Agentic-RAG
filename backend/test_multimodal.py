"""
Test script for Multi-Modal RAG features
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.multimodal_service import MultiModalService
from app.models.schemas import DocumentImage, DocumentChunk
from PIL import Image, ImageDraw
import io
import numpy as np

async def test_multimodal_service():
    """Test the multi-modal service functionality"""
    print("🧪 Testing Multi-Modal RAG Service")
    print("=" * 50)

    # Initialize service
    service = MultiModalService()
    print("✅ Service initialized")

    # Test 1: Chart Analysis (with mock chart)
    print("\n📊 Test 1: Chart Analysis")
    try:
        # Create a simple mock chart image
        chart_image = create_mock_chart()

        analysis = await service.analyze_chart_to_text(
            image=chart_image,
            context="Sales data for Q1-Q4 2023"
        )

        print(f"Chart Type: {analysis.chart_type}")
        print(f"Confidence: {analysis.confidence:.2f}")
        print(f"Facts Count: {len(analysis.queryable_facts)}")
        print(f"Description Preview: {analysis.text_content[:100]}...")
        print("✅ Chart analysis completed")

    except Exception as e:
        print(f"❌ Chart analysis failed: {e}")

    # Test 2: Smart Image Captioning
    print("\n🖼️ Test 2: Smart Image Captioning")
    try:
        # Create a simple mock technical diagram
        diagram_image = create_mock_diagram()

        captions = await service.generate_smart_image_captions(
            image=diagram_image,
            context="System architecture diagram"
        )

        print("Generated Captions:")
        for caption_type, caption in captions.items():
            print(f"  {caption_type}: {caption[:80]}...")
        print("✅ Image captioning completed")

    except Exception as e:
        print(f"❌ Image captioning failed: {e}")

    # Test 3: Visual-Text Linking
    print("\n🔗 Test 3: Visual-Text Linking")
    try:
        # Create mock images and text chunks
        mock_images = create_mock_document_images()
        mock_text_chunks = create_mock_text_chunks()

        links = await service.create_visual_text_links(
            images=mock_images,
            text_chunks=mock_text_chunks
        )

        print(f"Created {len(links)} visual-text links")
        for i, link in enumerate(links[:3]):  # Show first 3
            print(f"  Link {i+1}: {link.relationship} (confidence: {link.confidence:.2f})")
        print("✅ Visual-text linking completed")

    except Exception as e:
        print(f"❌ Visual-text linking failed: {e}")

    # Test 4: Multi-Modal Search
    print("\n🔍 Test 4: Multi-Modal Search")
    try:
        # Mock search results
        from app.models.schemas import SearchResult, SourceType

        mock_text_results = [
            SearchResult(
                id="text_1",
                title="Sample Document",
                content="This document contains sales analysis for 2023",
                source_type=SourceType.DOCUMENT,
                confidence_score=0.8,
                metadata={"document_id": "doc_1", "page_number": 1}
            )
        ]

        enhanced_results = await service.multi_modal_search(
            query="What are the sales trends?",
            text_results=mock_text_results,
            image_results=mock_images
        )

        print(f"Enhanced search returned {len(enhanced_results)} results")
        for result in enhanced_results[:2]:  # Show first 2
            print(f"  Result: {result.title} (confidence: {result.confidence_score:.2f})")
        print("✅ Multi-modal search completed")

    except Exception as e:
        print(f"❌ Multi-modal search failed: {e}")

    print("\n✨ Multi-Modal RAG Testing Complete!")
    print("=" * 50)

def create_mock_chart():
    """Create a simple mock chart image"""
    # Create a 400x300 image with a simple bar chart
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)

    # Draw simple bars
    bars = [(50, 250, 90, 200), (110, 250, 150, 150), (170, 250, 210, 100), (230, 250, 270, 180)]
    colors = ['blue', 'red', 'green', 'orange']

    for bar, color in zip(bars, colors):
        draw.rectangle(bar, fill=color)

    # Add title
    draw.text((150, 20), "Sales by Quarter", fill='black')

    return img

def create_mock_diagram():
    """Create a simple mock technical diagram"""
    img = Image.new('RGB', (300, 200), color='white')
    draw = ImageDraw.Draw(img)

    # Draw simple boxes and arrows
    draw.rectangle((20, 50, 80, 90), outline='black', width=2)
    draw.text((30, 65), "User", fill='black')

    draw.rectangle((150, 50, 210, 90), outline='black', width=2)
    draw.text((160, 65), "API", fill='black')

    draw.rectangle((220, 50, 280, 90), outline='black', width=2)
    draw.text((235, 65), "DB", fill='black')

    # Draw arrows
    draw.line((80, 70, 150, 70), fill='black', width=2)
    draw.line((210, 70, 220, 70), fill='black', width=2)

    return img

def create_mock_document_images():
    """Create mock DocumentImage objects"""
    return [
        DocumentImage(
            id="img_1",
            document_id="doc_1",
            page_number=1,
            image_type="chart",
            description="Sales chart showing quarterly performance",
            bbox=[100, 100, 400, 300],
            image_url="/images/chart1.png",
            metadata={"extracted_from": "sales_report.pdf"}
        ),
        DocumentImage(
            id="img_2",
            document_id="doc_1",
            page_number=2,
            image_type="diagram",
            description="System architecture diagram",
            bbox=[50, 150, 350, 400],
            image_url="/images/diagram1.png",
            metadata={"extracted_from": "tech_spec.pdf"}
        )
    ]

def create_mock_text_chunks():
    """Create mock DocumentChunk objects"""
    return [
        DocumentChunk(
            id="chunk_1",
            document_id="doc_1",
            content="The sales data shows a significant increase in Q3 2023, with revenue reaching $2.5M. This represents a 25% growth compared to Q2.",
            chunk_index=0,
            page_number=1,
            metadata={"content_type": "text"}
        ),
        DocumentChunk(
            id="chunk_2",
            document_id="doc_1",
            content="Our system architecture follows a microservices pattern with API gateway routing requests to various services including user management and database layers.",
            chunk_index=1,
            page_number=2,
            metadata={"content_type": "text"}
        ),
        DocumentChunk(
            id="chunk_3",
            document_id="doc_1",
            content="The chart above illustrates the quarterly performance metrics, highlighting the upward trend in customer acquisition and retention rates.",
            chunk_index=2,
            page_number=1,
            metadata={"content_type": "text"}
        )
    ]

if __name__ == "__main__":
    # Set up basic configuration for testing
    os.environ['AI_PROVIDER'] = 'claude'  # or 'gemini'
    os.environ['CLAUDE_API_KEY'] = 'test-key'  # Replace with actual key for real testing

    print("🚀 Starting Multi-Modal RAG Tests")
    print("Note: This test will use mock data and may not call actual AI services without proper API keys.")
    print()

    asyncio.run(test_multimodal_service())