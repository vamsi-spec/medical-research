from socket import timeout
from typing import List, Dict, Optional
from urllib import request
from loguru import logger
import requests
from datetime import datetime, timedelta
import json
from functools import lru_cache


class RealDrugInteractionChecker:
    def __init__(self):
        self.rxnav_url = "https://rxnav.nlm.nih.gov/REST"
        self.openfda_base_url = "https://api.fda.gov/drug"

        self.cache = {}
        self.cache_expiry = timedelta(hours=24)

        self.curated_interactions = self._build_curated_database()

        logger.info("Real drug interaction checker initialized(RxNav + OpenFDA)")

    def check_interaction(self,drug1: str,drug2: str,use_cache:bool = True) -> Dict:
        """
        Check interaction using RxNav API with fallback
        
        Args:
            drug1: First drug name
            drug2: Second drug name
            use_cache: Use cached results (faster)
            
        Returns:
            {
                'interaction_found': bool,
                'severity': str,
                'description': str,
                'clinical_recommendation': str,
                'source': str,
                'data_source': str
            }
        """

        logger.info(f"Checking interaction between {drug1} and {drug2}")

        cache_key = f"{drug1.lower()}_{drug2.lower()}"
        if use_cache and cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_expiry:
                logger.debug(f"Returning cached result for {drug1} and {drug2}")
                return cached_data
        try:
            rxcui1 = self._get_rxcui(drug1)
            rxcui2 = self._get_rxcui(drug2)

            if not rxcui1 or not rxcui2:
                logger.warning(f"RxCUI not found, trying curated database")
                return self._check_curated_database(drug1,drug2)

            interactions = self._get_interactions_from_rxnav(rxcui1,rxcui2)

            if interactions:
                result = self._format_interaction_result(
                    drug1,drug2,interactions
                )

                self.cache[cache_key] = (result,datetime.now())

                return result

            else:
                curated_result = self._check_curated_database(drug1,drug2)
                if curated_result['interaction_found']:
                    return curated_result
                
                result = {
                    'interaction_found' : False,
                    'drug1' : drug1,
                    'drug2' : drug2,
                    'severity' : None,
                    'description': f"No known interaction found between {drug1} and {drug2} in RxNav database.",
                    'clinical_recommendation': "No interaction documented. However, always consult your healthcare provider when combining medications.",
                    'source': 'RxNav API',
                    'data_source': 'NLM'
                }

                self.cache[cache_key] = (result,datetime.now())

                return result
        except Exception as e:
            logger.error(f"Error checking interaction between {drug1} and {drug2}: {e}")
            logger.info("Falling back to curated database")
            return self._check_curated_database(drug1,drug2)

    @lru_cache(maxsize=1000)
    def _get_rxcui(self, drug_name: str) -> Optional[str]:

        try:
            url = f"{self.rxnav_url}/rxcui.json"
            params = {'name' : drug_name}
            headers = {'User-Agent': 'MedicalResearchAssistant/1.0'}
            response = requests.get(url, params=params, headers=headers, timeout=10)

            response.raise_for_status()

            data = response.json()

            if 'idGroup' in data and 'rxnormId' in data['idGroup']:
                rxcuis =  data['idGroup']['rxnormId']
                if rxcuis:
                    rxcui = rxcuis[0]
                    logger.debug(f"Found RxCUI: {rxcui} for {drug_name}")
                    return rxcui
            logger.warning(f"No RxCUI found for {drug_name}")
            return None

        except Exception as e:
            logger.error(f"Error getting Rxcuii for {drug_name}: {e}")
            return None

    def _get_interactions_from_rxnav(self, rxcui1: str, rxcui2: str) -> List[Dict]:
        try:
            url = f"{self.rxnav_url}/interaction/list.json?rxcuis={rxcui1}+{rxcui2}"
            headers = {'User-Agent': 'MedicalResearchAssistant/1.0'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            interactions = []

            if 'fullInteractionTypeGroup' in data:
                for type_group in data['fullInteractionTypeGroup']:
                    for interaction_type in type_group.get('fullInteractionType', []):
                        for pair in interaction_type.get('interactionPair', []):
                            interactions.append({
                                'description': pair.get('description', 'No description'),
                                'severity': pair.get('severity', 'Unknown')
                            })

            return interactions
        except Exception as e:
            logger.error(f"Error getting interactions from RxNav: {e}")
            return []

    def _pair_involves_drug(self, pair: Dict, rxcui: str) -> bool:
        """Check if interaction pair involves the specified drug"""
        
        # Check both interaction concepts
        for concept in pair.get('interactionConcept', []):
            if concept.get('minConceptItem', {}).get('rxcui') == rxcui:
                return True
        
        return False
    

    def _format_interaction_result(
        self,
        drug1: str,
        drug2: str,
        interactions: List[Dict]
    ) -> Dict:
        primary_interaction = interactions[0]

        description = primary_interaction.get('description', 'Interaction documented')
        severity = primary_interaction.get('severity', 'Unknown')

        severity_mapping = {
            'high': 'Major',
            'moderate': 'Moderate',
            'low': 'Minor',
            'unknown': 'Unknown'
        }

        severity_normalized = severity_mapping.get(
            severity.lower(),
            'Moderate'
        )
        if severity_normalized == 'Major':
            recommendation = (
                "⚠️ MAJOR INTERACTION: Avoid this combination if possible. "
                "If unavoidable, close monitoring is essential. Consult your "
                "physician or pharmacist immediately."
            )
        elif severity_normalized == 'Moderate':
            recommendation = (
                "⚠️ MODERATE INTERACTION: Use with caution. Monitor for side effects. "
                "Dose adjustment may be needed. Inform your healthcare provider."
            )
        else:
            recommendation = (
                "ℹ️ MINOR INTERACTION: Generally safe but monitor for effects. "
                "Inform your healthcare provider about all medications you're taking."
            )
        return {
            'interaction_found': True,
            'drug1': drug1,
            'drug2': drug2,
            'severity': severity_normalized,
            'description': description,
            'clinical_recommendation': recommendation,
            'source': 'RxNav API',
            'data_source': 'National Library of Medicine (NLM)',
            'total_interactions': len(interactions),
            'all_interactions': interactions if len(interactions) > 1 else None
        }
        
    def _check_curated_database(self,drug1: str,drug2: str) -> Dict:
        drug1_norm = self._normalize_drug_name(drug1)
        drug2_norm = self._normalize_drug_name(drug2)

        key = f"{drug1_norm}_{drug2_norm}"
        reverse_key = f"{drug2_norm}_{drug1_norm}"
        interaction = (
            self.curated_interactions.get(key) or 
            self.curated_interactions.get(reverse_key)
        )

        if interaction:
            return {
                'interaction_found': True,
                'drug1': drug1,
                'drug2': drug2,
                'severity': interaction['severity'],
                'description': interaction['description'],
                'clinical_recommendation': interaction['recommendation'],
                'source': 'Curated Database (Fallback)',
                'data_source': 'Internal Critical Interactions'
            }
        else:
            return {
                'interaction_found': False,
                'drug1': drug1,
                'drug2': drug2,
                'severity': None,
                'description': f"No interaction found between {drug1} and {drug2}.",
                'clinical_recommendation': "No documented interaction. Consult healthcare provider when combining medications.",
                'source': 'No Data Available',
                'data_source': 'N/A'
            }

    def _normalize_drug_name(self,drug: str) -> str:


        import re
        
        # Lowercase
        drug_lower = drug.lower().strip()
        
        # Remove dosage info
        drug_clean = re.sub(r'\d+\s*mg', '', drug_lower)
        drug_clean = re.sub(r'tablet[s]?|capsule[s]?|pill[s]?', '', drug_clean)
        drug_clean = drug_clean.strip()
        
        # Common aliases
        aliases = {
            'acetylsalicylic acid': 'aspirin',
            'asa': 'aspirin',
            'glucophage': 'metformin',
            'coumadin': 'warfarin',
            'advil': 'ibuprofen',
            'motrin': 'ibuprofen'
        }
        
        return aliases.get(drug_clean, drug_clean)

    def _build_curated_database(self) -> Dict:

        return {
            'warfarin_aspirin': {
                'severity': 'Major',
                'description': 'Increased risk of bleeding. Warfarin is an anticoagulant and aspirin inhibits platelet aggregation, leading to additive bleeding risk.',
                'recommendation': 'Avoid combination if possible. If necessary, use lowest effective aspirin dose and monitor INR closely. Consider alternatives like acetaminophen for pain.'
            },
            'warfarin_ibuprofen': {
                'severity': 'Major',
                'description': 'Significantly increased bleeding risk. NSAIDs like ibuprofen can increase warfarin levels and independently affect platelet function.',
                'recommendation': 'Avoid concurrent use. Consider acetaminophen as alternative. If unavoidable, monitor INR frequently and watch for bleeding signs.'
            },
            
            # ACE inhibitors + NSAIDs
            'lisinopril_ibuprofen': {
                'severity': 'Moderate',
                'description': 'Reduced antihypertensive effect and increased risk of kidney injury. NSAIDs can blunt ACE inhibitor efficacy.',
                'recommendation': 'Monitor blood pressure and kidney function. Use lowest effective NSAID dose for shortest duration. Consider alternative pain management.'
            },
            
            # Metformin + Contrast
            'metformin_iohexol': {
                'severity': 'Moderate',
                'description': 'Risk of lactic acidosis. Contrast dye may cause acute kidney injury, reducing metformin clearance.',
                'recommendation': 'Hold metformin 48 hours before and after contrast administration. Check kidney function before resuming.'
            }
        }


    def check_multiple_drugs(
        self,
        drugs: List[str],
    ) -> List[Dict]:

        interactions_found = []

        logger.info(f"Checking {len(drugs)} drugs for interactions (real API)")

        for i in range(len(drugs)):
            for j in range(i+1,len(drugs)):
                interaction = self.check_interaction(drugs[i], drugs[j])

                if interaction['interaction_found']:
                    interactions_found.append(interaction)

        logger.info(f"Found {len(interactions_found)} real interactions")

        return interactions_found

    def format_interaction_report(
        self,
        interactions: List[Dict]
    ) -> str:
        if not interactions:
            return "No significant drug interactions detected"
        

        major = [i for i in interactions if i['severity'] == 'Major']
        moderate = [i for i in interactions if i['severity'] == 'Moderate']
        minor = [i for i in interactions if i['severity'] == 'Minor']


        report_parts = []

        report_parts.append("⚠️ DRUG INTERACTION REPORT")
        report_parts.append("=" * 70)
        report_parts.append(f"Total interactions found: {len(interactions)}")
        report_parts.append("")

        if major:
            report_parts.append("🔴 MAJOR INTERACTIONS (Contraindicated/Serious):")
            report_parts.append("-" * 70)
            for i, interaction in enumerate(major, 1):
                report_parts.append(f"\n{i}. {interaction['drug1']} + {interaction['drug2']}")
                report_parts.append(f"   {interaction['description']}")
                report_parts.append(f"   ⚕️ Recommendation: {interaction['clinical_recommendation']}")
                report_parts.append(f"   📊 Source: {interaction['data_source']}")
        
        # Moderate interactions
        if moderate:
            report_parts.append("\n🟡 MODERATE INTERACTIONS (Requires monitoring):")
            report_parts.append("-" * 70)
            for i, interaction in enumerate(moderate, 1):
                report_parts.append(f"\n{i}. {interaction['drug1']} + {interaction['drug2']}")
                report_parts.append(f"   {interaction['description']}")
                report_parts.append(f"   ⚕️ Recommendation: {interaction['clinical_recommendation']}")
        
        # Minor interactions
        if minor:
            report_parts.append("\n🟢 MINOR INTERACTIONS (Usually not clinically significant):")
            report_parts.append("-" * 70)
            for i, interaction in enumerate(minor, 1):
                report_parts.append(f"\n{i}. {interaction['drug1']} + {interaction['drug2']}")
                report_parts.append(f"   {interaction['description']}")
        
        return "\n".join(report_parts)

DrugInteractionChecker = RealDrugInteractionChecker()


if __name__ == "__main__":
    """Test drug interaction checker with real API"""
    
    checker = RealDrugInteractionChecker()
    
    print("="*70)
    print("REAL DRUG INTERACTION CHECKER TEST")
    print("Using: RxNav API (National Library of Medicine)")
    print("="*70)
    
    # Test 1: Known interaction
    print("\n1. Testing KNOWN interaction: Warfarin + Aspirin")
    print("-"*70)
    result = checker.check_interaction("warfarin", "aspirin")
    
    print(f"Interaction Found: {result['interaction_found']}")
    if result['interaction_found']:
        print(f"Severity: {result['severity']}")
        print(f"Description: {result['description'][:150]}...")
        print(f"Recommendation: {result['clinical_recommendation'][:150]}...")
        print(f"Data Source: {result['data_source']}")
    
    # Test 2: Multiple drugs
    print("\n\n2. Testing Multiple Drugs:")
    print("-"*70)
    drugs = ["warfarin", "aspirin", "ibuprofen"]
    print(f"Medications: {', '.join(drugs)}")
    
    interactions = checker.check_multiple_drugs(drugs)
    
    print(f"\nFound {len(interactions)} interactions")
    print("\n" + checker.format_interaction_report(interactions))
