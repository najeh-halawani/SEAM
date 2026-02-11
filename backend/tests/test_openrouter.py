"""Smoke test: verify OpenRouter free GPT-oss-120b actually responds.

Run with:  python -m backend.tests.test_openrouter
"""

import asyncio
from openai import AsyncOpenAI
from backend.config import settings


async def main():
    print(f"Base URL : {settings.openrouter_base_url}")
    print(f"Model    : {settings.llm_model}")
    print(f"API Key  : {settings.openai_api_key[:12]}...{settings.openai_api_key[-4:]}")
    print("-" * 50)
    print("Sending test prompt...")

    client = AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openrouter_base_url,
    )

    try:
        response = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "user", "content": "Say 'Hello SEAM!' and nothing else."},
            ],
            max_tokens=20,
        )
        reply = response.choices[0].message.content.strip()
        print(f"\n✅ Response: {reply}")
        print(f"   Model:   {response.model}")
        print(f"   Tokens:  prompt={response.usage.prompt_tokens}, "
              f"completion={response.usage.completion_tokens}")
        print("\n🎉 OpenRouter free tier is working!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPossible causes:")
        print("  - Invalid API key")
        print("  - Model not available / rate limited")
        print("  - Network issue")


if __name__ == "__main__":
    asyncio.run(main())
