from typing import Dict, List
from loguru import logger
from datetime import datetime
import json
from pathlib import Path


class SafetyMonitor:
    def __init__(
        self,
        log_dir: str = "logs/safety"
    ):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True,exist_ok=True)

        self.refusal_log = self.log_dir / "refusals.jsonl"
        self.low_confidence_log = self.log_dir / "low_confidence.jsonl"
        self.hallucination_log = self.log_dir / "hallucinations.jsonl"

        logger.info(f"Safety monitor initialized (log dir: {log_dir})")

    def log_refusal(
            self,
            query: str,
            safety_result: Dict,
            timestamp: datetime = None
        ):
            event = {
                'timestamp': (timestamp or datetime.now()).isoformat(),
                'event_type': 'refusal',
                'query': query,
                'category': safety_result['category'],
                'risk_level': safety_result['risk_level'],
                'reason': safety_result['refusal_reason']
            }

            self._append_log(self.refusal_log, event)
            logger.warning(f"Query refused: {safety_result['category']}")

    def log_low_confidence(
            self,
            query: str,
            confidence: float,
            confidence_breakdown: Dict,
            timestamp: datetime = None
        ):
            event = {
                'timestamp': (timestamp or datetime.now()).isoformat(),
                'event_type': 'low_confidence',
                'query': query,
                'confidence': confidence,
                'breakdown': confidence_breakdown
            }
            
            self._append_log(self.low_confidence_log, event)
            logger.warning(f"Low confidence answer: {confidence:.2%}")

    def log_hallucination(
        self,
        query: str,
        answer: str,
        hallucination_result: Dict,
        timestamp: datetime = None
    ):
        event = {
            'timestamp': (timestamp or datetime.now()).isoformat(),
            'event_type': 'hallucination',
            'query': query,
            'answer_preview': answer[:200],
            'risk': hallucination_result['hallucination_risk'],
            'issues': hallucination_result['issues']
        }
        
        self._append_log(self.hallucination_log, event)
        logger.warning(f"Hallucination detected: {hallucination_result['hallucination_risk']} risk")

    def _append_log(self, log_file: Path, event: Dict):
        """Append event to JSONL log file"""
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')

    def get_safety_stats(self, days: int = 7) -> Dict:
        """Get safety statistics for last N days"""
        
        # Count refusals by category
        refusal_stats = self._count_events(self.refusal_log, days)
        
        # Count low confidence
        low_conf_stats = self._count_events(self.low_confidence_log, days)
        
        # Count hallucinations
        halluc_stats = self._count_events(self.hallucination_log, days)
        
        return {
            'period_days': days,
            'refusals': refusal_stats,
            'low_confidence': low_conf_stats,
            'hallucinations': halluc_stats
        }

    def _count_events(self, log_file: Path, days: int) -> int:
        """Count events in log file from last N days"""
        
        if not log_file.exists():
            return 0
        
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        
        count = 0
        with open(log_file, 'r') as f:
            for line in f:
                event = json.loads(line)
                event_time = datetime.fromisoformat(event['timestamp'])
                if event_time >= cutoff:
                    count += 1
        
        return count

if __name__ == "__main__":
    """Test safety monitor"""
    
    monitor = SafetyMonitor()
    
    # Test logging
    monitor.log_refusal(
        query="Do I have diabetes?",
        safety_result={
            'category': 'diagnosis_request',
            'risk_level': 'high',
            'refusal_reason': 'Cannot provide medical diagnosis'
        }
    )
    
    monitor.log_low_confidence(
        query="What is X?",
        confidence=0.45,
        confidence_breakdown={'retrieval': 0.5, 'evidence': 0.4}
    )
    
    # Get stats
    stats = monitor.get_safety_stats(days=7)
    print("Safety Stats (last 7 days):")
    print(json.dumps(stats, indent=2))

        