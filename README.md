# Two Provider Cost Tracker

Sends the same prompt to Google Gemini and Groq and shows each reply,
the token counts, the time and the cost side by side.

## Setup

1. Install [uv](https://docs.astral.sh/uv/)
2. Copy `.env.example` to `.env` and put in your own API keys
3. Install packages: `uv sync`

## Run

```
uv run tracker.py "what is machine learning"
```

Results are also saved in `results.json`.

## Sample output

```
provider       input    output   seconds     cost (USD)
----------------------------------------------------------------------
gemini             5       737      9.25       0.001107
groq              75       494      1.53       0.000154
```

Models: gemini-3.1-flash-lite and openai/gpt-oss-20b.
Prices (USD per 1M tokens) are in `.env` and were taken from the
providers' pricing pages in November 2026.

## What I learned

The same prompt gave 5 input tokens on Gemini and 75 on Groq, because each
provider tokenizes text differently. Output tokens cost more than input
tokens, so long replies are what make a call expensive. Cost is
tokens x price per million / 1,000,000, with input and output priced separately.