#!/usr/bin/env python3

from app.models.schemas import ProcessedDocument, DocumentChunk
import time

try:
    # Test ProcessedDocument creation
    doc = ProcessedDocument(
        document_id='test123',
        filename='test.txt',
        file_type='txt', 
        file_size=100,
        pages_processed=1,
        text_chunks=[],
        images=[],
        metadata={'test': 'value'},
        processing_time_ms=150
    )
    print('ProcessedDocument created successfully!')
    print(f'Processing time: {doc.processing_time_ms}')
    
    # Test with dictionary (this should fail)
    test_dict = {
        'document_id': 'test123',
        'chunks_created': 1
    }
    print('\nTrying to create ProcessedDocument from dict...')
    doc2 = ProcessedDocument(**test_dict)
    
except Exception as e:
    print(f'Error: {e}')
    print(f'Error type: {type(e)}') 