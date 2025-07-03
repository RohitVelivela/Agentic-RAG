#!/usr/bin/env python3

import asyncio
import time
from app.services.document_processor import DocumentProcessor
from app.models.schemas import ProcessedDocument
from app.config import settings

class MockFile:
    def __init__(self, content: str, filename: str):
        self.content = content.encode('utf-8')
        self.filename = filename
    
    async def read(self):
        return self.content

async def test_document_processing():
    try:
        # Create document processor
        processor = DocumentProcessor()
        
        # Create mock text file
        mock_file = MockFile("This is a test document for upload.", "test.txt")
        
        print("Starting document processing...")
        
        # Process the document
        result = await processor.process_document(mock_file)
        
        print(f"Document processed successfully!")
        print(f"Document ID: {result.document_id}")
        print(f"Processing time: {result.processing_time_ms}ms")
        print(f"Text chunks: {len(result.text_chunks)}")
        print(f"Images: {len(result.images)}")
        
        return result
        
    except Exception as e:
        print(f"Error during processing: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_document_processing()) 