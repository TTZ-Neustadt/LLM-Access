# LLM Access

Code snippets for OpenAI-compatible chat APIs using cURL, Python, JavaScript, LangChain and R/ellmer. No API keys or API base URLs are included.

## Configuration

Obtain your connection details privately from your provider or course organiser and set these environment variables:

| Variable | Value to supply privately |
| --- | --- |
| `OPENAI_BASE_URL` | Your provider's API base, including its API version path when required |
| `OPENAI_API_KEY` | Your personal access key |
| `OPENAI_MODEL` | An exact model ID supported by your provider |

The examples require explicit configuration and do not choose a default service. `.env.example` contains empty fields only; the scripts do not automatically load `.env` files. For R, put your values in your user `~/.Renviron` and restart R. For notebooks, set environment variables within the kernel; use `getpass.getpass()` for hidden key input.

Never commit filled credential files, private key CSVs or notebook output containing credentials. The supplied `.gitignore` excludes common local credential files.

## 1. cURL

Requires cURL and jq. List available models:

```bash
curl --fail-with-body "${OPENAI_BASE_URL%/}/models" \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

Send a chat request:

```bash
jq -n --arg model "$OPENAI_MODEL" \
  '{model: $model, messages: [{role: "user", content: "Explain sentiment classification in two sentences."}]}' |
  curl --fail-with-body "${OPENAI_BASE_URL%/}/chat/completions" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H 'Content-Type: application/json' --data-binary @-
```

For streaming, add `stream: true` to the JSON object and `--no-buffer` to cURL. The response consists of server-sent events.

Full example: [examples/curl-example.sh](examples/curl-example.sh).

## 2. Python

Python 3, standard library only:

```python
import json
import os
import urllib.request

request = urllib.request.Request(
    os.environ["OPENAI_BASE_URL"].rstrip("/") + "/chat/completions",
    headers={
        "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"],
        "Content-Type": "application/json",
    },
    data=json.dumps({
        "model": os.environ["OPENAI_MODEL"],
        "messages": [{"role": "user", "content": "Explain sentiment classification."}],
    }).encode(),
)
with urllib.request.urlopen(request, timeout=120) as response:
    print(json.load(response)["choices"][0]["message"]["content"])
```

[The full Python example](examples/python-example.py) also supports model discovery and streaming:

```bash
python3 examples/python-example.py --models
python3 examples/python-example.py
python3 examples/python-example.py --stream --prompt 'Explain sentiment classification.'
```

In a notebook, load the functions after setting your environment variables:

```python
import runpy
api = runpy.run_path("examples/python-example.py")
print(api["list_models"]())
answer = api["chat"]("Summarise: Useful course, but too little practice.")
print(answer)
```

## 3. JavaScript

Node.js 22+, using built-in `fetch`. Run on the server or in Node; putting credentials in browser code exposes them to visitors.

```javascript
const response = await fetch(
  `${process.env.OPENAI_BASE_URL.replace(/\/+$/, "")}/chat/completions`,
  {
    method: "POST",
    headers: {
      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: process.env.OPENAI_MODEL,
      messages: [{ role: "user", content: "Explain sentiment classification." }],
    }),
    signal: AbortSignal.timeout(120000),
  },
);
if (!response.ok) throw new Error(`HTTP ${response.status}`);
console.log((await response.json()).choices[0].message.content);
```

Run [the full JavaScript example](examples/javascript-example.mjs):

```bash
node examples/javascript-example.mjs
```

## 4. LangChain (Python)

Install the integration:

```bash
python3 -m pip install langchain-openai
```

```python
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

model = ChatOpenAI(
    base_url=os.environ["OPENAI_BASE_URL"],
    api_key=os.environ["OPENAI_API_KEY"],
    model=os.environ["OPENAI_MODEL"],
    use_responses_api=False,
)
prompt = ChatPromptTemplate.from_messages([
    ("system", "Classify sentiment as positive, negative, mixed or neutral. Return only the label."),
    ("human", "{response}"),
])
chain = prompt | model
print(chain.invoke({"response": "Useful course, but too little practice."}).content)
```

[Full LangChain example](examples/langchain-example.py), including a streaming alternative. This uses basic chat completions; provider-specific features may need a dedicated integration. See the [LangChain integration reference](https://reference.langchain.com/python/langchain-openai/langchain_openai).

## 5. R with ellmer

Install ellmer (and httr2 for model discovery in the full example):

```r
install.packages(c("ellmer", "httr2"))
```

After setting configuration in your user `.Renviron` and restarting R:

```r
library(ellmer)
stopifnot(all(nzchar(Sys.getenv(c("OPENAI_BASE_URL", "OPENAI_API_KEY", "OPENAI_MODEL")))))
chat <- chat_openai_compatible(
  base_url = Sys.getenv("OPENAI_BASE_URL"),
  credentials = function() Sys.getenv("OPENAI_API_KEY"),
  model = Sys.getenv("OPENAI_MODEL"),
  system_prompt = "Be concise and do not invent details.",
  echo = "output"
)
chat$chat("Summarise: The course was useful, but I wanted more exercises.")
```

Use `chat_openai_compatible()` for compatible chat-completions services, as documented in the [official ellmer reference](https://ellmer.tidyverse.org/reference/chat_openai_compatible.html). Update ellmer if your version does not export this function. `echo = "output"` displays the answer as it streams.

[The full R example](examples/ellmer-example.R) discovers models and demonstrates summarisation and classification. Reuse a chat object for follow-up questions; create a new one for each independent survey response to avoid carrying over conversation history.

```r
source("examples/ellmer-example.R")
```

## Troubleshooting

- **401:** check that your key is active and valid for the configured service.
- **Unknown model:** query `/models` and use an exact returned ID.
- **404:** check your base path; avoid adding the API version twice.
- **429 or temporary errors:** retry after a short delay and limit concurrency.
- Compatible APIs differ in supported features; these examples focus on model listing and chat completions.

Examples are templates. Syntax checks do not establish compatibility with every provider, and no live API credentials are included or used for verification.
