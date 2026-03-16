from typing import Dict, Optional
import json
import re
from loguru import logger

class StructuredOutputParser:
    def __init__(self):
        pass

    def parse_json_response(self,response:str) -> Optional[Dict]:
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        json_match = re.search(r'\{.*\}',response,re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        logger.warning("Could not parse JSON from response")

        return None

    def validate_medical_answer(self,answer_dict: Dict) -> bool:
        required_fields = ['answer']
        for field in required_fields:
            if field not in answer_dict:
                logger.warning(f"Missing required field:{field}")
                return False
        return True

    def extract_citations_from_text(self,text:str) -> list:
        citations = re.findall(r'\[(\d+)]',text)

        return [int(c) for c in citations]

if __name__ == "__main__":
    parser = StructuredOutputParser()

    test_cases = [
        # Case 1: Plain JSON
        '{"answer": "Metformin is first-line", "confidence": 0.9}',
        
        # Case 2: Markdown wrapped
        '''```json
        {
            "answer": "Based on research [1][2]...",
            "confidence": 0.85
        }
```''',
        
        # Case 3: Mixed text
        'Here is the answer: {"answer": "Test", "confidence": 0.8} Hope this helps!',
    ]

    print("="*70)
    print("OUTPUT PARSER TEST")
    print("="*70)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"Input: {test_case[:50]}...")
        
        result = parser.parse_json_response(test_case)
        
        if result:
            print(f"✅ Parsed successfully: {result}")
        else:
            print("❌ Parse failed")
    
    # Test citation extraction
    text = "Metformin is effective [1][2]. Studies show [3] that..."
    citations = parser.extract_citations_from_text(text)
    print(f"\nCitation extraction: {citations}")