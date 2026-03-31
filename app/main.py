import os
import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from groq import Groq
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="AI Test Generator",
    description="Generates pytest test cases for Python functions using Groq API",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

request_count = 0
error_count = 0


def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is not set")
    return Groq(api_key=api_key)


class FunctionInput(BaseModel):
    code: str

    @field_validator("code")
    @classmethod
    def validate_code(cls, v):
        if not v or not v.strip():
            raise ValueError("code must not be empty")
        if len(v) > 2000:
            raise ValueError("code must not exceed 2000 characters")
        return v


@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": time.time()}


@app.get("/metrics")
def metrics():
    return {
        "request_count": request_count,
        "error_count": error_count
    }


@app.post("/generate")
@limiter.limit("5/minute")
async def generate_tests(request: Request, payload: FunctionInput):
    global request_count, error_count
    request_count += 1

    prompt = f"""You are an expert Python test engineer.
Given the following Python function, generate a complete pytest test file.
Include at least 3 meaningful test cases covering normal behavior, edge cases, and error cases.
Return only valid Python code with no explanation or markdown.

Function:
{payload.code}
"""

    try:
        groq_client = get_groq_client()
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.1-8b-instant",
        )
        test_code = chat_completion.choices[0].message.content
        return {"tests": test_code}

    except HTTPException:
        error_count += 1
        raise

    except Exception as e:
        error_count += 1
        raise HTTPException(status_code=500, detail=f"Groq API error: {str(e)}")