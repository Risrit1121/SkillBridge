from backend.config import settings

async def call_ai(prompt: str) -> str:
    key = settings.active_openrouter_key
    if key:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=key, base_url="https://openrouter.ai/api/v1")
        resp = await client.chat.completions.create(
            model=settings.model_name or "openai/gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content

    if settings.gemini_api_key:
        from google import genai
        client = genai.Client(api_key=settings.gemini_api_key)
        resp = client.models.generate_content(
            model=settings.model_name or "gemini-2.0-flash", contents=prompt)
        return resp.text

    if settings.anthropic_api_key:
        import anthropic
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        msg = client.messages.create(
            model="claude-3-haiku-20240307", max_tokens=1024,
            messages=[{"role": "user", "content": prompt}])
        return msg.content[0].text

    raise ValueError("No AI provider configured")
