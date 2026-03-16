"""
LangChain agent with real medical tools
Multi-tool reasoning and action with production APIs
"""

from typing import List, Dict, Optional
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from loguru import logger

from Backend.tools.drug_interaction import RealDrugInteractionChecker
from Backend.tools.clinical_trials import EnhancedClinicalTrialsSearcher
from Backend.tools.medical_codes import RealMedicalCodeLookup


class MedicalAgent:
    """
    Medical agent with specialized real API tools
    
    Capabilities:
    - Drug interaction checking (RxNav API)
    - Clinical trials search (ClinicalTrials.gov API v2)
    - Medical code lookup (NLM API)
    - Multi-step reasoning (ReAct pattern)
    
    All tools use official, free government APIs
    """
    
    def __init__(
        self,
        llm_model: str = "llama3.1:8b",
        max_iterations: int = 5
    ):
        # Initialize LLM
        self.llm = OllamaLLM(
            model=llm_model,
            temperature=0.1  # Low temperature for factual accuracy
        )
        
        # Initialize tools with REAL APIs
        logger.info("Initializing medical tools with real APIs...")
        
        self.drug_checker = RealDrugInteractionChecker()
        self.trials_searcher = EnhancedClinicalTrialsSearcher()
        self.code_lookup = RealMedicalCodeLookup()
        
        # Create LangChain tools
        self.tools = self._create_tools()
        
        # Create agent
        self.agent = self._create_agent(max_iterations)
        
        logger.info(f"Medical agent initialized with {len(self.tools)} real API tools")
    
    def _create_tools(self) -> List[Tool]:
        """
        Create LangChain Tool objects
        
        Tool descriptions are CRITICAL - they guide the agent's decision-making
        """
        
        tools = [
            Tool(
                name="check_drug_interaction",
                description=(
                    "Check for drug-drug interactions using RxNav API (National Library of Medicine). "
                    "Use this when asked about drug safety, interactions, or combining medications. "
                    "Input should be two drug names separated by 'and' or comma. "
                    "Example: 'warfarin and aspirin' or 'metformin, ibuprofen'. "
                    "Returns severity (Major/Moderate/Minor) and clinical recommendations."
                ),
                func=self._check_drug_interaction_wrapper
            ),
            
            Tool(
                name="search_clinical_trials",
                description=(
                    "Search for clinical trials from ClinicalTrials.gov (NIH). "
                    "Use when asked about ongoing trials, trial eligibility, or research studies. "
                    "Input should be the medical condition. "
                    "Example: 'type 2 diabetes' or 'breast cancer'. "
                    "Returns currently recruiting trials with NCT IDs, status, and phase."
                ),
                func=self._search_trials_wrapper
            ),
            
            Tool(
                name="lookup_icd10_code",
                description=(
                    "Look up ICD-10 diagnosis codes using NLM API. "
                    "Use when asked about diagnosis codes, billing codes, or medical coding. "
                    "Input should be the diagnosis or condition name. "
                    "Example: 'diabetes' or 'hypertension'. "
                    "Returns code, description, and billability status."
                ),
                func=self._lookup_icd10_wrapper
            ),
            
            Tool(
                name="lookup_cpt_code",
                description=(
                    "Look up CPT procedure codes (limited public dataset). "
                    "Use when asked about procedure codes or billing for services. "
                    "Input should be the procedure name. "
                    "Example: 'office visit' or 'ECG'. "
                    "Returns code and description from public CPT subset."
                ),
                func=self._lookup_cpt_wrapper
            )
        ]
        
        return tools
    
    def _check_drug_interaction_wrapper(self, input_str: str) -> str:
        """Wrapper for drug interaction tool"""
        
        # Parse input
        drugs = [d.strip() for d in input_str.replace(' and ', ',').split(',')]
        
        if len(drugs) < 2:
            return "Please provide two drug names to check interactions."
        
        drug1, drug2 = drugs[0], drugs[1]
        
        result = self.drug_checker.check_interaction(drug1, drug2)
        
        if result['interaction_found']:
            return (
                f"⚠️ INTERACTION FOUND ({result['severity']} severity)\n"
                f"Drugs: {result['drug1']} + {result['drug2']}\n"
                f"Description: {result['description']}\n"
                f"Recommendation: {result['clinical_recommendation']}\n"
                f"Source: {result['data_source']}"
            )
        else:
            return (
                f"✅ No significant interaction found between {drug1} and {drug2}.\n"
                f"Source: {result.get('data_source', 'N/A')}"
            )
    
    def _search_trials_wrapper(self, condition: str) -> str:
        """Wrapper for clinical trials tool"""
        
        trials = self.trials_searcher.search_trials(
            condition=condition,
            status=["RECRUITING"],
            max_results=3
        )
        
        if not trials:
            return f"No recruiting clinical trials found for {condition}."
        
        return self.trials_searcher.format_trial_results(trials, detailed=False)
    
    def _lookup_icd10_wrapper(self, search_term: str) -> str:
        """Wrapper for ICD-10 lookup"""
        
        codes = self.code_lookup.lookup_icd10(search_term, max_results=3)
        
        if not codes:
            return f"No ICD-10 codes found for '{search_term}'."
        
        return self.code_lookup.format_code_results(codes, "ICD-10")
    
    def _lookup_cpt_wrapper(self, search_term: str) -> str:
        """Wrapper for CPT lookup"""
        
        codes = self.code_lookup.lookup_cpt(search_term, max_results=3)
        
        if not codes:
            return f"No CPT codes found for '{search_term}'."
        
        return self.code_lookup.format_code_results(codes, "CPT")
    
    def _create_agent(self, max_iterations: int) -> AgentExecutor:
        """
        Create ReAct agent
        
        ReAct = Reasoning + Acting
        Agent reasons about which tool to use, then acts
        """
        
        # ReAct prompt template
        template = """You are a medical research assistant with access to real medical databases. Answer the question using the available tools.

Available tools:
{tools}

Tool Names: {tool_names}

Use the following format:

Question: the input question
Thought: think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original question

IMPORTANT GUIDELINES:
- Use tools when needed to get accurate, real-time information
- For drug interactions, ALWAYS check safety using the drug interaction tool
- For clinical trials, search the ClinicalTrials.gov database
- For medical codes, use the official ICD-10/CPT lookup tools
- Provide evidence-based answers with data sources
- Include medical disclaimers when appropriate

Question: {input}
Thought: {agent_scratchpad}"""

        prompt = PromptTemplate.from_template(template)
        
        # Create agent
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=max_iterations,
            handle_parsing_errors=True
        )
        
        return agent_executor
    
    def query(self, question: str) -> Dict:
        """
        Query the agent
        
        Args:
            question: User's medical question
            
        Returns:
            {
                'answer': str,
                'intermediate_steps': List,
                'tools_used': List[str]
            }
        """
        
        logger.info(f"Agent query: {question}")
        
        try:
            result = self.agent.invoke({
                'input': question
            })
            
            # Extract tools used
            tools_used = []
            if 'intermediate_steps' in result:
                for step in result['intermediate_steps']:
                    if len(step) > 0:
                        action = step[0]
                        if hasattr(action, 'tool'):
                            tools_used.append(action.tool)
            
            return {
                'answer': result.get('output', 'No answer generated'),
                'intermediate_steps': result.get('intermediate_steps', []),
                'tools_used': list(set(tools_used))
            }
        
        except Exception as e:
            logger.error(f"Agent error: {e}")
            return {
                'answer': f"I encountered an error: {str(e)}",
                'intermediate_steps': [],
                'tools_used': []
            }


if __name__ == "__main__":
    """Test medical agent"""
    
    print("="*70)
    print("MEDICAL AGENT TEST")
    print("Real APIs: RxNav, ClinicalTrials.gov, NLM")
    print("="*70)
    
    agent = MedicalAgent()
    
    # Test queries
    test_queries = [
        "Is it safe to take warfarin and aspirin together?",
        "What clinical trials are recruiting for type 2 diabetes?",
        "What is the ICD-10 code for hypertension?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}")
        print(f"{'='*70}")
        print(f"Query: {query}\n")
        
        result = agent.query(query)
        
        print(f"\nANSWER:")
        print("-"*70)
        print(result['answer'])
        print("-"*70)
        
        if result['tools_used']:
            print(f"\nTools used: {', '.join(result['tools_used'])}")