import json
import re
from typing import Dict, List, Tuple

class IntentClassifier:
    def __init__(self, intents_file: str = "intents.json"):
        with open(intents_file, 'r', encoding='utf-8') as f:
            self.intents_data = json.load(f)
        self.intents = list(self.intents_data.keys())
    
    def classify_intent(self, message: str) -> Dict[str, any]:
        """
        Classify the intent of a user message.
        Returns intent name and confidence score.
        """
        message_lower = message.lower().strip()
        
        # Check for exact matches first
        intent_scores = {}
        
        for intent, data in self.intents_data.items():
            score = 0
            examples = data.get("examples", [])
            priority = data.get("priority", 1)
            
            # Check for keyword matches
            for example in examples:
                example_lower = example.lower()
                if example_lower in message_lower:
                    score += 2
                # Check for word-level matches
                example_words = example_lower.split()
                message_words = message_lower.split()
                common_words = set(example_words) & set(message_words)
                if len(common_words) > 0:
                    score += len(common_words) * 0.5
            
            # Priority boost
            score *= (1 / priority)
            intent_scores[intent] = score
        
        # Get the intent with highest score
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[best_intent]
            
            # If confidence is too low, default to Telecom Knowledge
            if confidence < 0.5:
                best_intent = "Telecom Knowledge"
                confidence = 0.3
        else:
            best_intent = "Telecom Knowledge"
            confidence = 0.3
        
        return {
            "intent": best_intent,
            "confidence": min(confidence, 1.0),
            "all_scores": intent_scores
        }
    
    def get_intent_payload(self, intent: str) -> Dict:
        """Get the payload structure for a specific intent."""
        return {
            "intent": intent,
            "category": self._get_category(intent),
            "requires_context": self._requires_context(intent)
        }
    
    def _get_category(self, intent: str) -> str:
        """Categorize intent into main categories."""
        if intent in ["Internet Issues", "Router Issues", "Call Issues"]:
            return "Technical Support"
        return intent
    
    def _requires_context(self, intent: str) -> bool:
        """Check if intent requires additional context."""
        context_required = [
            "Account Information",
            "Billing Support",
            "Plan Management",
            "Complaint Management"
        ]
        return intent in context_required
