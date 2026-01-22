from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
from intent_classifier import IntentClassifier
from llm_client import LLMClient
from config import CORS_ORIGINS, BACKEND_PORT
import uvicorn

app = FastAPI(title="Telecom Chatbot API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
intent_classifier = IntentClassifier()
llm_client = LLMClient()

# Request/Response Models
class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict] = None

class ChatResponse(BaseModel):
    intent: str
    confidence: float
    response: str
    session_id: Optional[str] = None
    requires_escalation: bool = False

class HealthResponse(BaseModel):
    status: str
    service: str

@app.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(status="healthy", service="Telecom Chatbot API")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", service="Telecom Chatbot API")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint that processes user messages.
    """
    try:
        # Classify intent
        intent_result = intent_classifier.classify_intent(request.message)
        intent = intent_result["intent"]
        confidence = intent_result["confidence"]
        
        # Get intent payload
        intent_payload = intent_classifier.get_intent_payload(intent)
        
        # Check if escalation is needed
        requires_escalation = intent == "Escalation Support" or confidence < 0.3
        
        # Generate LLM response
        response_text = llm_client.generate_response(
            message=request.message,
            intent=intent,
            context=request.context
        )
        
        return ChatResponse(
            intent=intent,
            confidence=confidence,
            response=response_text,
            session_id=request.session_id,
            requires_escalation=requires_escalation
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/intents")
async def get_intents():
    """Get all available intents."""
    return {
        "intents": list(intent_classifier.intents_data.keys()),
        "total": len(intent_classifier.intents_data)
    }

@app.get("/api-status")
async def api_status():
    """Check API key configuration status (without exposing the key)."""
    from config import OPENROUTER_API_KEY
    import requests
    
    api_key_present = OPENROUTER_API_KEY is not None and OPENROUTER_API_KEY.strip() != ""
    api_key_prefix = OPENROUTER_API_KEY[:10] if OPENROUTER_API_KEY and len(OPENROUTER_API_KEY) >= 10 else "N/A"
    
    # Test the API key with a simple request
    test_result = {"status": "not_tested"}
    if api_key_present:
        try:
            test_payload = {
                "model": llm_client.model,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 5
            }
            test_headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            test_response = requests.post(
                llm_client.base_url,
                json=test_payload,
                headers=test_headers,
                timeout=10
            )
            test_result = {
                "status": "success" if test_response.status_code == 200 else "failed",
                "status_code": test_response.status_code,
                "error": test_response.text[:200] if test_response.status_code != 200 else None
            }
        except Exception as e:
            test_result = {
                "status": "error",
                "error": str(e)[:200]
            }
    
    return {
        "api_key_configured": api_key_present,
        "api_key_length": len(OPENROUTER_API_KEY) if OPENROUTER_API_KEY else 0,
        "api_key_prefix": api_key_prefix,
        "api_key_format": "OpenRouter (sk-or-v1-...)" if api_key_prefix.startswith("sk-or-v1") else "Other format",
        "model": llm_client.model,
        "base_url": llm_client.base_url,
        "test_result": test_result
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=BACKEND_PORT)
