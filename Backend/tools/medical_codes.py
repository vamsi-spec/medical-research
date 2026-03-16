from typing import List, Dict, Optional
from loguru import logger
import requests
from functools import lru_cache

class RealMedicalCodeLookup:
    def __init__(self):
        self.icd10_api_url = "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"

        self.cpt_codes = self._load_public_cpt_codes()
        self.icd10_fallback = self._load_fallback_icd10_codes()

        logger.info("Real Medical Code Lookup initialized (NLM API + Public CPT + Fallback)")

    @lru_cache(maxsize=500)

    def lookup_icd10(
        self,
        search_term: str,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Look up ICD-10 codes using NLM API
        
        Args:
            search_term: Diagnosis or code to search
            max_results: Maximum results to return
            
        Returns:
            List of ICD-10 codes with descriptions
        """

        logger.info(f"ICD-10 lookup: {search_term}(NLM API)")

        try:
            params = {
                'sf': 'code,name',
                'terms': search_term,
                'maxList': max_results
            }

            response = requests.get(
                self.icd10_api_url,
                params = params,
                timeout=10
            )

            response.raise_for_status()

            data = response.json()

            if len(data) >= 4:
                results = data[3]

                codes = []
                for result in results:
                    if len(result) >= 2:
                        code = result[0]
                        description = result[1]

                        codes.append({
                            'code': code,
                            'description': description,
                            'code_system': 'ICD-10-CM',
                            'source': 'National Library of Medicine',
                            'billable': self._is_billable_icd10(code),
                            'category': self._get_icd10_category(code)
                        })

                    logger.info(f"Found {len(codes)} ICD-10 codes")

                    return codes
                return []

        except Exception as e:
            logger.error(f"Error looking up ICD-10 code: {e}")
            logger.info("Using local fallback database due to API error")
            return self._lookup_local_icd10(search_term, max_results)

    def _lookup_local_icd10(self, search_term: str, max_results: int) -> List[Dict]:
        """Local fallback search when API is down"""
        search_lower = search_term.lower()
        matches = []
        
        # Check for exact code match first
        if search_term.upper() in self.icd10_fallback:
            matches.append({
                'code': search_term.upper(),
                'description': self.icd10_fallback[search_term.upper()],
                'code_system': 'ICD-10-CM',
                'source': 'Local Fallback',
                'billable': self._is_billable_icd10(search_term.upper()),
                'category': self._get_icd10_category(search_term.upper())
            })
        
        # Search descriptions
        for code, description in self.icd10_fallback.items():
            if code == search_term.upper():
                continue # Already added
                
            if search_lower in description.lower() or search_lower in code.lower():
                matches.append({
                    'code': code,
                    'description': description,
                    'code_system': 'ICD-10-CM',
                    'source': 'Local Fallback',
                    'billable': self._is_billable_icd10(code),
                    'category': self._get_icd10_category(code)
                })
        
        return matches[:max_results]

    def validate_icd10(self,code: str) -> Dict:
        try:
            results = self.lookup_icd10(code, max_results=1)
            
            if results and results[0]['code'].upper() == code.upper():
                return {
                    'valid': True,
                    **results[0]
                }
            else:
                return {
                    'valid': False,
                    'code': code,
                    'message': 'Code not found in ICD-10-CM database'
                }
        
        except Exception as e:
            logger.error(f"Error validating ICD-10 code: {e}")
            return {
                'valid': False,
                'code': code,
                'message': f'Validation error: {str(e)}'
            }

    def _is_billable_icd10(self, code: str) -> bool:
        """Determine if ICD-10 code is billable"""
        
        # Codes with decimal points and sufficient specificity are billable
        parts = code.split('.')
        
        if len(parts) > 1 and len(parts[1]) >= 1:
            return True
        
        return False

    def _get_icd10_category(self, code: str) -> str:
        """Get ICD-10 category from code prefix"""
        
        if not code:
            return "Unknown"
        
        first_letter = code[0].upper()
        
        categories = {
            'A': 'Infectious and parasitic diseases',
            'B': 'Infectious and parasitic diseases',
            'C': 'Neoplasms',
            'D': 'Diseases of blood and immune system',
            'E': 'Endocrine, nutritional and metabolic diseases',
            'F': 'Mental and behavioral disorders',
            'G': 'Diseases of the nervous system',
            'H': 'Diseases of eye/ear',
            'I': 'Diseases of the circulatory system',
            'J': 'Diseases of the respiratory system',
            'K': 'Diseases of the digestive system',
            'L': 'Diseases of the skin',
            'M': 'Diseases of the musculoskeletal system',
            'N': 'Diseases of the genitourinary system',
            'O': 'Pregnancy, childbirth',
            'P': 'Perinatal conditions',
            'Q': 'Congenital malformations',
            'R': 'Symptoms and abnormal findings',
            'S': 'Injury, poisoning',
            'T': 'Injury, poisoning',
            'Z': 'Factors influencing health status'
        }
        
        return categories.get(first_letter, 'Unknown category')

    def lookup_cpt(
        self,
        search_term: str,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Look up CPT codes from public dataset
        """
        
        search_lower = search_term.lower()
        matches = []
        
        for code, details in self.cpt_codes.items():
            if search_term.upper() == code:
                return [{
                    'code': code,
                    **details,
                    'source': 'Public CPT Dataset'
                }]
            
            if search_lower in details['description'].lower():
                matches.append({
                    'code': code,
                    **details,
                    'source': 'Public CPT Dataset'
                })
        
        logger.info(f"Found {len(matches)} CPT codes")
        
        return matches[:max_results]


    def _load_fallback_icd10_codes(self) -> Dict:
        """Load common ICD-10 codes for fallback"""
        return {
            'E11.9': 'Type 2 diabetes mellitus without complications',
            'E11': 'Type 2 diabetes mellitus',
            'E10.9': 'Type 1 diabetes mellitus without complications',
            'I10': 'Essential (primary) hypertension',
            'J00': 'Acute nasopharyngitis [common cold]',
            'J18.9': 'Pneumonia, unspecified organism',
            'M54.5': 'Low back pain',
            'R05': 'Cough',
            'R50.9': 'Fever, unspecified',
            'Z00.00': 'Encounter for general adult medical exam without abnormal findings'
        }

    def _load_public_cpt_codes(self) -> Dict:
        """Load public CPT codes (limited subset)"""
        
        return {
            # Evaluation and Management
            '99202': {
                'description': 'Office visit, new patient, straightforward',
                'category': 'Evaluation and Management'
            },
            '99203': {
                'description': 'Office visit, new patient, low complexity',
                'category': 'Evaluation and Management'
            },
            '99204': {
                'description': 'Office visit, new patient, moderate complexity',
                'category': 'Evaluation and Management'
            },
            '99213': {
                'description': 'Office visit, established patient, low complexity',
                'category': 'Evaluation and Management'
            },
            '99214': {
                'description': 'Office visit, established patient, moderate complexity',
                'category': 'Evaluation and Management'
            },
            
            # Common lab tests
            '80053': {
                'description': 'Comprehensive metabolic panel',
                'category': 'Pathology and Laboratory'
            },
            '83036': {
                'description': 'Hemoglobin A1c level',
                'category': 'Pathology and Laboratory'
            },
            '85025': {
                'description': 'Complete blood count with differential',
                'category': 'Pathology and Laboratory'
            },
            
            # Common procedures
            '93000': {
                'description': 'Electrocardiogram (ECG), complete',
                'category': 'Medicine'
            }
        }

    def format_code_results(
        self,
        codes: List[Dict],
        code_type: str = "ICD-10"
    ) -> str:
        """Format code lookup results for display"""
        
        if not codes:
            return f"No {code_type} codes found matching the criteria."
        
        report_parts = []
        
        report_parts.append(f"📋 {code_type} CODE LOOKUP RESULTS: {len(codes)}")
        report_parts.append("=" * 70)
        
        for i, code_data in enumerate(codes, 1):
            report_parts.append(f"\n{i}. {code_data['code']}: {code_data['description']}")
            
            if 'category' in code_data:
                report_parts.append(f"   Category: {code_data['category']}")
            
            if 'billable' in code_data:
                billable_str = "✅ Yes" if code_data['billable'] else "❌ No"
                report_parts.append(f"   Billable: {billable_str}")
            
            if 'source' in code_data:
                report_parts.append(f"   Source: {code_data['source']}")
        
        return "\n".join(report_parts)


# For backward compatibility
MedicalCodeLookup = RealMedicalCodeLookup


if __name__ == "__main__":
    """Test medical code lookup"""
    
    lookup = RealMedicalCodeLookup()
    
    print("="*70)
    print("REAL MEDICAL CODE LOOKUP TEST")
    print("ICD-10: National Library of Medicine API")
    print("="*70)
    
    # Test ICD-10 lookup
    print("\n1. ICD-10 Lookup: 'diabetes'")
    print("-"*70)
    icd_results = lookup.lookup_icd10("diabetes", max_results=5)
    print(lookup.format_code_results(icd_results, "ICD-10"))
    
    # Test validation
    print("\n\n2. ICD-10 Code Validation: 'E11.9'")
    print("-"*70)
    validation = lookup.validate_icd10("E11.9")
    
    if validation['valid']:
        print(f"✅ Valid Code: {validation['code']}")
        print(f"Description: {validation['description']}")
        print(f"Category: {validation['category']}")
    else:
        print(f"❌ Invalid: {validation['message']}")