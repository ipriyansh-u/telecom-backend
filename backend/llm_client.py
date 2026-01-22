import requests
import os
from typing import Dict, Optional
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, LLM_MODEL, API_PROVIDER

class LLMClient:
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.base_url = OPENROUTER_BASE_URL
        self.model = LLM_MODEL
        self.provider = API_PROVIDER
        
        # Log initialization status (without exposing the actual key)
        if self.api_key:
            print(f"LLM Client initialized with provider: {self.provider}")
            print(f"LLM Client initialized with model: {self.model}")
            print(f"API Key present: {'Yes' if self.api_key else 'No'} (length: {len(self.api_key) if self.api_key else 0})")
        else:
            print("WARNING: LLM Client initialized without API key!")
    
    def generate_response(self, message: str, intent: str, context: Optional[Dict] = None) -> str:
        """
        Generate response using LLM API.
        
        Args:
            message: User's message
            intent: Classified intent
            context: Additional context if needed
        """
        if not self.api_key:
            return "I apologize, but the AI service is not configured. Please contact support."
        
        # Build system prompt based on intent
        system_prompt = self._build_system_prompt(intent, context)
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        # Add OpenRouter-specific headers only if using OpenRouter
        if self.provider == "openrouter":
            headers["HTTP-Referer"] = "https://telecom-chatbot.local"
            headers["X-Title"] = "Telecom Chatbot"
        
        try:
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            else:
                return "I'm sorry, I couldn't generate a response. Please try again."
        
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {e.response.status_code}"
            if e.response.status_code == 401:
                error_msg += ": Unauthorized - Please check your API key"
            elif e.response.status_code == 429:
                error_msg += ": Rate limit exceeded - Please try again later"
            elif e.response.status_code >= 500:
                error_msg += ": Server error - Please try again later"
            
            try:
                error_detail = e.response.json()
                print(f"LLM API Error: {error_msg}")
                print(f"Error Details: {error_detail}")
                # Log the error response text for debugging
                if hasattr(e.response, 'text'):
                    print(f"Response Text: {e.response.text[:500]}")  # First 500 chars
            except Exception as parse_error:
                print(f"LLM API Error: {error_msg} - {str(e)}")
                print(f"Could not parse error response: {parse_error}")
                if hasattr(e.response, 'text'):
                    print(f"Raw Response: {e.response.text[:500]}")
            
            if e.response.status_code == 401:
                return "I apologize, but there's an authentication issue with the AI service. Please contact support."
            elif e.response.status_code == 429:
                return "I'm currently experiencing high demand. Please try again in a moment."
            else:
                return "I'm experiencing technical difficulties. Please try again later or contact support."
        
        except requests.exceptions.Timeout:
            print("LLM API Error: Request timeout")
            return "The AI service is taking too long to respond. Please try again."
        
        except requests.exceptions.ConnectionError as e:
            print(f"LLM API Error: Connection error - {str(e)}")
            return "I'm unable to connect to the AI service. Please check your internet connection and try again."
        
        except requests.exceptions.RequestException as e:
            print(f"LLM API Error: {type(e).__name__} - {str(e)}")
            return "I'm experiencing technical difficulties. Please try again later or contact support."
    
    def _build_system_prompt(self, intent: str, context: Optional[Dict] = None) -> str:
        """Build system prompt based on intent."""
        base_prompt = """You are a helpful customer support chatbot for a telecom company. 
You are professional, friendly, and knowledgeable about telecom services including internet, mobile, and related technical issues.
Always be concise and helpful. If you don't know something, offer to escalate to a human agent."""
        
        intent_prompts = {
            "Account Information": "Focus on account-related queries. Ask for account number if needed.",
            "Plan Management": "Help with plan upgrades, downgrades, and plan information.",
            "Billing Support": "Assist with billing inquiries, payments, and invoice questions.",
            "Complaint Management": "Be empathetic. Collect complaint details and offer solutions.",
            "Internet Issues": "Provide technical troubleshooting steps for internet connectivity issues.",
            "Router Issues": "Help with router configuration, WiFi setup, and router-related problems.",
            "Call Issues": "Assist with call quality, signal strength, and call-related problems.",
            "Technical Support": "Provide technical assistance and troubleshooting guidance.",
            "Network Information": "Share information about network coverage and signal strength.",
            "Escalation Support": "Acknowledge the request and prepare to transfer to human agent.",
            "Telecom Knowledge": "Explain telecom terms and concepts clearly.",
            "Conversation End": "Politely end the conversation and offer future assistance."
        }
        
        intent_prompt = intent_prompts.get(intent, "")
        
        if context:
            context_str = f"\nAdditional Context: {context}"
        else:
            context_str = ""
        
        return f"{base_prompt}\n\nIntent: {intent}\n{intent_prompt}{context_str}"