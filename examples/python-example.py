"""OpenAI-compatible HTTP examples using Python's standard library only."""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = os.environ["OPENAI_BASE_URL"].rstrip("/")
SYSTEM_PROMPT = "You help analyse short survey responses. Be concise, follow the requested format, and do not invent details."


def request(path, payload=None):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("Set OPENAI_API_KEY first.")
    req = urllib.request.Request(
        BASE_URL + path,
        data=None if payload is None else json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    return urllib.request.urlopen(req, timeout=120)


def list_models():
    with request("/models") as response:
        return [model["id"] for model in json.load(response)["data"]]


def chat(prompt, stream=False):
    model = os.getenv("OPENAI_MODEL")
    if not model:
        raise ValueError("Set OPENAI_MODEL to an ID returned by --models.")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "stream": stream,
    }
    with request("/chat/completions", payload) as response:
        if not stream:
            return json.load(response)["choices"][0]["message"]["content"]
        fragments = []
        for raw_line in response:
            line = raw_line.decode("utf-8").strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            event = json.loads(data)
            if "error" in event:
                raise RuntimeError("The server reported a streaming error.")
            for choice in event.get("choices", []):
                text = choice.get("delta", {}).get("content") or ""
                print(text, end="", flush=True)
                fragments.append(text)
        print()
        return "".join(fragments)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", action="store_true")
    parser.add_argument("--stream", action="store_true")
    parser.add_argument("--prompt", default="Summarise in one sentence: The course was useful, but I wanted more time for exercises.")
    args = parser.parse_args()
    try:
        if args.models:
            print("\n".join(list_models()))
        else:
            answer = chat(args.prompt, stream=args.stream)
            if not args.stream:
                print(answer)
    except urllib.error.HTTPError as exc:
        sys.exit(f"HTTP {exc.code}: check your API base, key and model ID.")
    except (ValueError, RuntimeError, urllib.error.URLError, TimeoutError) as exc:
        sys.exit(str(exc))
