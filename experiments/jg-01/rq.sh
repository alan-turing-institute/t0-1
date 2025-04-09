#!/bin/zsh
## Attempt a request to the Azure OpenAI API
curl -X POST "https://ai-aifoundrygpt4o065309524447.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2025-01-01-preview" \
    -H "Content-Type: application/json" \
    -H "api-key: $AZURE_API_KEY" \
    -d '{"messages": [{"role": "user", "content": "What have I got in my pocket?"}], "max_tokens": 4096, "temperature": 1, "top_p": 1, "model": "gpt-4o"}'
