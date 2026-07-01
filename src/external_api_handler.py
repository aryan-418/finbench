import requests
import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


def call_external_api(prompt, endpoint_url, api_key, api_type="openai"):
    """
    Send a prompt to any external banking AI API and get a response.
    Supports OpenAI-compatible APIs, Groq, and generic REST endpoints.
    """

    # ── OpenAI-compatible (most common — works for OpenAI, Azure, local LLMs) ──
    if api_type in ["openai", "openai_compatible"]:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.3
        }
        try:
            response = requests.post(
                endpoint_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            return f"API_ERROR: {str(e)}"
        except (KeyError, json.JSONDecodeError) as e:
            return f"PARSE_ERROR: {str(e)} | Raw: {response.text[:200]}"

    # ── Groq API ──────────────────────────────────────────────────────────────
    elif api_type == "groq":
        try:
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"API_ERROR: {str(e)}"

    # ── Generic REST endpoint ─────────────────────────────────────────────────
    elif api_type == "generic_rest":
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {"message": prompt, "query": prompt, "input": prompt}
        try:
            response = requests.post(
                endpoint_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            # Try common response field names
            for field in ["response", "message", "output", "text", "content", "answer", "reply"]:
                if field in data:
                    return str(data[field])
            return str(data)
        except requests.exceptions.RequestException as e:
            return f"API_ERROR: {str(e)}"

    else:
        return f"UNSUPPORTED_API_TYPE: {api_type}"


def validate_external_api(endpoint_url, api_key, api_type="openai"):
    """
    Test if an external API is reachable and responding before running full benchmark.
    Returns (success: bool, message: str, sample_response: str)
    """
    test_prompt = "Hello. What banking services can you help me with today?"

    print(f"Validating external API at: {endpoint_url}")
    response = call_external_api(test_prompt, endpoint_url, api_key, api_type)

    if response.startswith("API_ERROR") or response.startswith("PARSE_ERROR"):
        return False, f"Connection failed: {response}", ""

    if len(response) < 5:
        return False, "API responded but with empty or very short response", response

    return True, "API connection successful", response


def call_single_prompt(prompt, target_type, endpoint_url=None, api_key=None,
                       api_type=None, customer_id="CUST001"):
    """
    Route a single prompt to either internal simulator or external API.
    Used for both benchmark runs and live single-prompt testing.
    """
    if target_type == "internal":
        from bank_simulator import chat_with_bank_ai
        return chat_with_bank_ai(prompt, customer_id)
    elif target_type == "external":
        if not endpoint_url or not api_key:
            return "ERROR: External API requires endpoint URL and API key"
        return call_external_api(prompt, endpoint_url, api_key, api_type or "openai")
    else:
        return "ERROR: Invalid target type. Use 'internal' or 'external'"


if __name__ == "__main__":
    # Test internal routing
    print("Testing internal routing...")
    response = call_single_prompt(
        "What is my account balance?",
        target_type="internal"
    )
    print(f"Internal response: {response[:100]}")
    print("\n✓ External API handler ready")
    print("✓ Supports: OpenAI-compatible, Groq, Generic REST")
    print("✓ Single prompt routing working")