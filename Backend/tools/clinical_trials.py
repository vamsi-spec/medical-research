from typing import List, Dict, Optional
from loguru import logger
import requests
from datetime import datetime
import time


class EnhancedClinicalTrialsSearcher:
    """
    Production clinical trials searcher
    
    API: ClinicalTrials.gov API v2 (latest version)
    Documentation: https://clinicaltrials.gov/data-api/api
    
    Features:
    - Advanced search with filters
    - Study details retrieval
    - Eligibility criteria
    - Contact information
    - Study locations
    
    """

    def __init__(self):
        self.base_url = "https://clinicaltrials.gov/api/v2"

        self.last_request_time = 0
        self.min_request_interval = 0.5

        logger.info("Enhanced clinical trials searcher initialized")

    def search_trials(
        self,
        condition: str,
        status: Optional[List[str]] = None,
        phase: Optional[List[str]] = None,
        country: str = "United States",
        max_results: int = 10
    )-> List[Dict]:
        """
        Advanced trial search
        
        Args:
            condition: Medical condition (e.g., "diabetes", "breast cancer")
            status: List of statuses ["RECRUITING", "ACTIVE_NOT_RECRUITING", "COMPLETED"]
            phase: List of phases ["PHASE1", "PHASE2", "PHASE3", "PHASE4"]
            country: Country name
            max_results: Maximum results to return
            
        Returns:
            List of trial dictionaries with detailed information
        """

        if status is None:
            status = ["RECRUITING"]

        logger.info(f"Searching trails:{condition} (status:{status})")

        try:
            self._rate_limit()

            url = f"{self.base_url}/studies"
            params = {
                'query.term': condition,
                'filter.overallStatus': ','.join(status) if status else None,
                'pageSize': min(max_results, 100),  # Max 100 per page
                'format': 'json'
            }

            params = {k: v for k, v in params.items() if v is not None}

            response = requests.get(url,params=params,timeout=15)

            response.raise_for_status()

            data = response.json()

            trails = self._parse_trails_v2(data)

            logger.info(f"Found {len(trails)} trails")

            return trails[:max_results]

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Error searching trials: {e}")
            return []

    def get_trail_details(self,nct_id: str) -> Optional[Dict]:
        """
        Get detailed information for specific trial
        
        Args:
            nct_id: NCT identifier (e.g., "NCT05234567")
            
        Returns:
            Comprehensive trial details
        """

        try:
            self._rate_limit()

            url = f"{self.base_url}/studies/{nct_id}"
            params = {'format': 'json'}

            response = requests.get(url,params=params,timeout=15)
            response.raise_for_status()

            data = response.json()

            if 'studies' in data and len(data['studies']) > 0:
                study = data['studies'][0]
                return self._parse_trails_v2({'studies':[study]})[0]

            return None

        except Exception as e:
            logger.error(f"Error getting trial details: {e}")
            return None

    def _rate_limit(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

    def _parse_trails_v2(self,api_response: Dict) -> List[Dict]:
        trials = []

        if 'studies' not in api_response:
            return trials

        for study in api_response['studies']:
            try:
                protocol = study.get('protocolSection', {})
                identification = protocol.get('identificationModule', {})
                status = protocol.get('statusModule', {})
                design = protocol.get('designModule', {})
                eligibility = protocol.get('eligibilityModule', {})
                contacts = protocol.get('contactsLocationsModule', {})
                description = protocol.get('descriptionModule', {})
                conditions = protocol.get('conditionsModule', {})
                
                # Extract basic info
                trial = {
                    'nct_id': identification.get('nctId', 'Unknown'),
                    'title': identification.get('briefTitle', 'Unknown'),
                    'official_title': identification.get('officialTitle', ''),
                    
                    # Status
                    'status': status.get('overallStatus', 'Unknown'),
                    'start_date': status.get('startDateStruct', {}).get('date', 'Unknown'),
                    'completion_date': status.get('completionDateStruct', {}).get('date', 'Unknown'),
                    
                    # Study details
                    'phase': ', '.join(design.get('phases', [])) if design.get('phases') else 'N/A',
                    'study_type': design.get('studyType', 'Unknown'),
                    'enrollment': status.get('enrollmentStruct', {}).get('count', 'Unknown'),
                    
                    # Conditions
                    'conditions': conditions.get('conditions', []),
                    
                    # Interventions
                    'interventions': self._extract_interventions(protocol),
                    
                    # Eligibility
                    'min_age': eligibility.get('minimumAge', 'N/A'),
                    'max_age': eligibility.get('maximumAge', 'N/A'),
                    'sex': eligibility.get('sex', 'ALL'),
                    
                    # Description
                    'brief_summary': description.get('briefSummary', ''),
                    
                    # Locations
                    'locations': self._extract_locations(contacts),
                    
                    # URL
                    'url': f"https://clinicaltrials.gov/study/{identification.get('nctId', '')}"
                }
                
                trials.append(trial)
            
            except Exception as e:
                logger.warning(f"Error parsing trial: {e}")
                continue
        
        return trials

    def _extract_interventions(self,protocol: Dict) -> List[Dict]:
        interventions_module = protocol.get('armsInterventionsModule', {})
        interventions = interventions_module.get('interventions', [])


        return [
            f"{i.get('type','Unknown')}: {i.get('name','Unknown')}" for i in interventions[:3]
        ]

    def _extract_locations(self,contacts_module: Dict) -> List[Dict]:
        locations = contacts_module.get('locations', [])
        return [
            {
                'facility': loc.get('facility', 'Unknown'),
                'city': loc.get('city', ''),
                'state': loc.get('state', ''),
                'country': loc.get('country', ''),
            }
            for loc in locations[:3]  # Limit to 3 locations
        ]

    def format_trial_results(
        self,
        trials: List[Dict],
        detailed: bool = False
    ) -> str:
        if not trials:
            return "No trials found"

        report_parts = []

        report_parts.append(f"🔬 CLINICAL TRIALS FOUND: {len(trials)}")
        report_parts.append("=" * 70)
        
        for i, trial in enumerate(trials, 1):
            report_parts.append(f"\n{i}. {trial['title']}")
            report_parts.append(f"   📋 NCT ID: {trial['nct_id']}")
            report_parts.append(f"   📊 Status: {trial['status']}")
            report_parts.append(f"   🔬 Phase: {trial['phase']}")
            
            if detailed:
                report_parts.append(f"   👥 Enrollment: {trial['enrollment']}")
                
                # Conditions
                if trial.get('conditions'):
                    conditions_str = ', '.join(trial['conditions'][:2])
                    report_parts.append(f"   🏥 Conditions: {conditions_str}")
                
                # Interventions
                if trial.get('interventions'):
                    interventions_str = ', '.join(trial['interventions'][:2])
                    report_parts.append(f"   💊 Interventions: {interventions_str}")
                
                # Location
                if trial.get('locations'):
                    location = trial['locations'][0]
                    report_parts.append(
                        f"   📍 Location: {location.get('city', '')}, {location.get('state', '')}"
                    )
            
            report_parts.append(f"   🔗 {trial['url']}")
        
        return "\n".join(report_parts)

ClinicalTrialsSearcher = EnhancedClinicalTrialsSearcher


if __name__ == "__main__":
    """Test clinical trials API"""
    
    searcher = EnhancedClinicalTrialsSearcher()
    
    print("="*70)
    print("ENHANCED CLINICAL TRIALS API TEST")
    print("Using: ClinicalTrials.gov API v2 (Latest)")
    print("="*70)
    
    # Test search
    print("\nSearching: Type 2 Diabetes (Recruiting)")
    print("-"*70)
    trials = searcher.search_trials(
        condition="type 2 diabetes",
        status=["RECRUITING"],
        max_results=3
    )
    
    print(searcher.format_trial_results(trials, detailed=True))

    
