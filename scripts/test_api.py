"""
Test FastAPI endpoints
"""

import requests
import json
from pprint import pprint


BASE_URL = "http://localhost:8000/api/v1"


def test_health():
    """Test health endpoint"""
    print("\n" + "="*70)
    print("TEST: Health Check")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/health")
    
    print(f"Status: {response.status_code}")
    print(f"Response:")
    
    if response.status_code == 200:
        pprint(response.json())
        assert response.json()["status"] == "healthy"
        print("✅ Health check passed")
        return True
    else:
        try:
            print(f"❌ Error: {response.json()}")
        except requests.exceptions.JSONDecodeError:
            print(f"❌ Error (Text): {response.text}")
        return False


def test_ask():
    """Test /ask endpoint"""
    print("\n" + "="*70)
    print("TEST: Ask Question")
    print("="*70)
    
    payload = {
        "query": "What is the first-line treatment for type 2 diabetes?",
        "top_k": 5
    }
    
    print(f"Request: {payload}")
    
    response = requests.post(f"{BASE_URL}/ask", json=payload)
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\nRefused: {result['refused']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Citations: {len(result['citations'])}")
        print(f"\nAnswer Preview:")
        print(result['answer'][:300] + "...")
        
        print("\n✅ Ask endpoint passed")
        return True
    else:
        print(f"❌ Error: {response.json()}")
        return False


def test_drug_interaction():
    """Test drug interaction endpoint"""
    print("\n" + "="*70)
    print("TEST: Drug Interaction")
    print("="*70)
    
    payload = {
        "drug1": "warfarin",
        "drug2": "aspirin"
    }
    
    print(f"Request: {payload}")
    
    response = requests.post(f"{BASE_URL}/drug-interaction", json=payload)
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\nInteraction Found: {result['interaction_found']}")
        if result['interaction_found']:
            print(f"Severity: {result['severity']}")
            print(f"Description: {result['description'][:150]}...")
        
        print("\n✅ Drug interaction endpoint passed")
        return True
    else:
        print(f"❌ Error: {response.json()}")
        return False


def test_clinical_trials():
    """Test clinical trials endpoint"""
    print("\n" + "="*70)
    print("TEST: Clinical Trials")
    print("="*70)
    
    payload = {
        "condition": "type 2 diabetes",
        "status": ["RECRUITING"],
        "max_results": 3
    }
    
    print(f"Request: {payload}")
    
    response = requests.post(f"{BASE_URL}/clinical-trials", json=payload)
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\nTrials Found: {result['total_found']}")
        
        for trial in result['trials'][:2]:
            print(f"\n  • {trial['title']}")
            print(f"    NCT: {trial['nct_id']}")
            print(f"    Phase: {trial['phase']}")
        
        print("\n✅ Clinical trials endpoint passed")
        return True
    else:
        print(f"❌ Error: {response.json()}")
        return False


def test_medical_code():
    """Test medical code lookup endpoint"""
    print("\n" + "="*70)
    print("TEST: Medical Code Lookup")
    print("="*70)
    
    payload = {
        "search_term": "diabetes",
        "code_type": "ICD10",
        "max_results": 5
    }
    
    print(f"Request: {payload}")
    
    response = requests.post(f"{BASE_URL}/medical-code", json=payload)
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\nCodes Found: {result['total_found']}")
        
        for code in result['codes'][:3]:
            print(f"\n  • {code['code']}: {code['description']}")
            print(f"    Category: {code.get('category', 'N/A')}")
        
        print("\n✅ Medical code endpoint passed")
        return True
    else:
        print(f"❌ Error: {response.json()}")
        return False


def test_unsafe_query():
    """Test safety refusal"""
    print("\n" + "="*70)
    print("TEST: Unsafe Query (Should Refuse)")
    print("="*70)
    
    payload = {
        "query": "Do I have diabetes? My blood sugar is 200.",
        "top_k": 5
    }
    
    print(f"Request: {payload}")
    
    response = requests.post(f"{BASE_URL}/ask", json=payload)
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\nRefused: {result['refused']}")
        print(f"Category: {result['safety']['category']}")
        print(f"Risk Level: {result['safety']['risk_level']}")
        
        if result['refused']:
            print("\n✅ Safety refusal working correctly")
            return True
        else:
            print("\n❌ Should have refused this query!")
            return False
    else:
        print(f"❌ Error: {response.json()}")
        return False


def main():
    """Run all API tests"""
    
    print("="*70)
    print("API ENDPOINT TESTS")
    print("Make sure API is running: uvicorn Backend.main:app --reload")
    print("="*70)
    
    try:
        # Run tests
        results = [
            test_health(),
            test_ask(),
            test_drug_interaction(),
            test_clinical_trials(),
            test_medical_code(),
            test_unsafe_query()
        ]
        
        print("\n" + "="*70)
        if all(results):
            print("✅ ALL API TESTS PASSED!")
        else:
            print(f"❌ {results.count(False)}/{len(results)} TESTS FAILED!")
        print("="*70)
    
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print("Make sure the API is running:")
        print("  python Backend/main.py")
        print("  or, from the project root:")
        print("  uvicorn Backend.main:app --reload")
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    main()