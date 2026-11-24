import json
import os
import sys
import time

from dotenv import load_dotenv
from google import genai
from groq import Groq

load_dotenv()


def get_setting(name):
    value = os.getenv(name)
    if not value:
        print(f"Error: {name} is missing. Add it to your .env file (see .env.example).")
        sys.exit(1)
    return value


def calculate_cost(input_tokens, output_tokens, input_price_per_m, output_price_per_m):
    return (input_tokens * input_price_per_m / 1_000_000) + (
        output_tokens * output_price_per_m / 1_000_000
    )


def call_gemini(prompt):
    client = genai.Client(
    api_key=get_setting("GEMINI_API_KEY"),
    http_options={"timeout": 30000},
)
    model = get_setting("GEMINI_MODEL")
    in_price = float(get_setting("GEMINI_INPUT_PRICE_PER_M"))
    out_price = float(get_setting("GEMINI_OUTPUT_PRICE_PER_M"))

    start = time.time()
    response = client.models.generate_content(model=model, contents=prompt)
    seconds = time.time() - start

    usage = response.usage_metadata
    input_tokens = usage.prompt_token_count or 0
    output_tokens = (usage.candidates_token_count or 0) + (usage.thoughts_token_count or 0)

    return {
        "provider": "gemini",
        "model": model,
        "reply": response.text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_price_per_m": in_price,
        "output_price_per_m": out_price,
        "cost_usd": calculate_cost(input_tokens, output_tokens, in_price, out_price),
        "seconds": round(seconds, 2),
    }


def call_groq(prompt):
    client = Groq(api_key=get_setting("GROQ_API_KEY"), timeout=30)
    model = get_setting("GROQ_MODEL")
    in_price = float(get_setting("GROQ_INPUT_PRICE_PER_M"))
    out_price = float(get_setting("GROQ_OUTPUT_PRICE_PER_M"))

    start = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    seconds = time.time() - start

    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens

    return {
        "provider": "groq",
        "model": model,
        "reply": response.choices[0].message.content,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_price_per_m": in_price,
        "output_price_per_m": out_price,
        "cost_usd": calculate_cost(input_tokens, output_tokens, in_price, out_price),
        "seconds": round(seconds, 2),
    }


def print_results(results):
    for r in results:
        print(f"\n=== {r['provider'].upper()} ({r['model']}) ===")
        print(r["reply"])

    print("\n" + "-" * 70)
    print(f"{'provider':<10}{'input':>10}{'output':>10}{'seconds':>10}{'cost (USD)':>15}")
    print("-" * 70)
    for r in results:
        print(
            f"{r['provider']:<10}{r['input_tokens']:>10}{r['output_tokens']:>10}"
            f"{r['seconds']:>10}{r['cost_usd']:>15.6f}"
        )


def main():
    if len(sys.argv) < 2:
        print('Usage: uv run tracker.py "your prompt"')
        sys.exit(1)

    prompt = sys.argv[1]
    results = [call_gemini(prompt), call_groq(prompt)]

    print_results(results)

    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("\nSaved to results.json")


if __name__ == "__main__":
    main()