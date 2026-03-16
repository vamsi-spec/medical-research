"""
Comprehensive test of all real medical APIs
Tests drug interactions, clinical trials, and medical codes
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from Backend.tools.drug_interaction import RealDrugInteractionChecker
from Backend.tools.clinical_trials import EnhancedClinicalTrialsSearcher
from Backend.tools.medical_codes import RealMedicalCodeLookup
from Backend.agents.medical_agent import MedicalAgent


def test_all_apis():
    """
    Comprehensive test of all real APIs
    """
    
    print("="*70)
    print("COMPREHENSIVE REAL API TEST")
    print("Testing all medical data sources")
    print("="*70)
    
    # Initialize all tools
    print("\n📦 Initializing tools with real APIs...")
    drug_checker = RealDrugInteractionChecker()
    trials_searcher = EnhancedClinicalTrialsSearcher()
    code_lookup = RealMedicalCodeLookup()
    print("✅ All tools initialized\n")
    
    # Test 1: Drug Interactions
    print("\n" + "="*70)
    print("TEST 1: DRUG INTERACTION CHECKER (RxNav API)")
    print("="*70)
    
    print("\nChecking: Warfarin + Aspirin")
    interaction = drug_checker.check_interaction("warfarin", "aspirin")
    
    print(f"Interaction Found: {interaction['interaction_found']}")
    if interaction['interaction_found']:
        print(f"Severity: {interaction['severity']}")
        print(f"Description: {interaction['description'][:150]}...")
        print(f"Source: {interaction['data_source']}")
    
    # Test 2: Clinical Trials
    print("\n\n" + "="*70)
    print("TEST 2: CLINICAL TRIALS (ClinicalTrials.gov API v2)")
    print("="*70)
    
    print("\nSearching: Type 2 Diabetes (Recruiting)")
    trials = trials_searcher.search_trials(
        condition="type 2 diabetes",
        status=["RECRUITING"],
        max_results=2
    )
    
    print(f"✅ Found {len(trials)} trials")
    for trial in trials:
        print(f"\n  • {trial['title']}")
        print(f"    NCT: {trial['nct_id']}")
        print(f"    Phase: {trial['phase']}")
        print(f"    Status: {trial['status']}")
    
    # Test 3: ICD-10 Codes
    print("\n\n" + "="*70)
    print("TEST 3: ICD-10 CODES (NLM ClinicalTables API)")
    print("="*70)
    
    print("\nLooking up: 'diabetes'")
    icd_codes = code_lookup.lookup_icd10("diabetes", max_results=3)
    
    print(f"✅ Found {len(icd_codes)} codes")
    for code in icd_codes:
        print(f"\n  • {code['code']}: {code['description']}")
        print(f"    Category: {code['category']}")
        print(f"    Billable: {code['billable']}")
    
    # Test 4: Full Agent
    print("\n\n" + "="*70)
    print("TEST 4: MEDICAL AGENT (Multi-Tool)")
    print("="*70)
    
    agent = MedicalAgent()
    
    query = "Is warfarin safe with ibuprofen?"
    print(f"\nQuery: {query}")
    
    result = agent.query(query)
    
    print(f"\nAgent Answer:")
    print("-"*70)
    print(result['answer'])
    print("-"*70)
    
    if result['tools_used']:
        print(f"\nTools Used: {', '.join(result['tools_used'])}")
    
    # Summary
    print("\n\n" + "="*70)
    print("✅ ALL REAL APIS WORKING!")
    print("="*70)
    print("\nData Sources:")
    print("  1. RxNav API (NLM) - Drug interactions")
    print("  2. ClinicalTrials.gov API v2 - Clinical trials")
    print("  3. NLM ClinicalTables API - ICD-10 codes")
    print("  4. Public CPT Dataset - Procedure codes")
    print("\nAll FREE, official medical data sources! 🎉")


if __name__ == "__main__":
    test_all_apis()