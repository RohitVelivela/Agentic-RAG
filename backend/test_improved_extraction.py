#!/usr/bin/env python3
"""
Test improved PDF text extraction with AI vision fallback
"""

import requests
import time

def test_improved_extraction():
    """Test if improved text extraction is getting more complete content"""
    print("🧪 Testing Improved PDF Text Extraction")
    print("=" * 50)
    
    # Wait for server
    time.sleep(2)
    
    # Test query on existing documents
    queries = [
        "What specific projects are mentioned?",
        "What details are in the motivation letter?",
        "What information is in the ticket document?"
    ]
    
    for query in queries:
        print(f"\n📝 Query: {query}")
        
        try:
            response = requests.post(
                "http://localhost:8000/query",
                json={"query": query, "num_results": 5},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data['answer']
                
                print(f"✅ Answer length: {len(answer)} characters")
                print(f"📝 Answer preview: {answer[:200]}...")
                
                # Check if we're getting better content
                if "Projects" == answer.strip() or len(answer) < 20:
                    print("⚠️  Still getting minimal content")
                else:
                    print("✅ Getting detailed content!")
                    
                # Show sources
                sources_used = data.get('sources_used', {})
                doc_count = sources_used.get('DOCUMENT', 0)
                print(f"📚 Document sources: {doc_count}")
                
                # Show citations
                citations = data.get('citations', [])
                print(f"📄 Citations: {len(citations)}")
                for i, citation in enumerate(citations[:2]):
                    title = citation.get('title', 'Unknown')
                    confidence = citation.get('confidence_score', 0)
                    print(f"   {i+1}. {title} (confidence: {confidence:.3f})")
                    
            else:
                print(f"❌ Query failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n" + "=" * 50)
    print("🎉 Test completed!")

if __name__ == "__main__":
    test_improved_extraction() 