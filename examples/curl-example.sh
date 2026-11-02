#!/usr/bin/env bash
set -euo pipefail
: "${OPENAI_BASE_URL:?Set OPENAI_BASE_URL}"
: "${OPENAI_API_KEY:?Set OPENAI_API_KEY}"
: "${OPENAI_MODEL:?Set OPENAI_MODEL}"
# Requires curl and jq. jq safely encodes the model and prompt as JSON.
curl --fail-with-body "${OPENAI_BASE_URL%/}/models" \
  -H "Authorization: Bearer $OPENAI_API_KEY"
printf '\n'
jq -n --arg model "$OPENAI_MODEL" \
  '{model: $model, messages: [{role: "user", content: "Explain sentiment classification in two sentences."}]}' |
  curl --fail-with-body "${OPENAI_BASE_URL%/}/chat/completions" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H 'Content-Type: application/json' --data-binary @-
printf '\n'
