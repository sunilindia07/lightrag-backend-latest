from collections.abc import Iterable
import os
import pipmaster as pm  # Pipmaster for dynamic library install

# install specific modules
if not pm.is_installed("openai"):
    pm.install("openai")

from openai import (
    AsyncAzureOpenAI,
    APIConnectionError,
    RateLimitError,
    APITimeoutError,
)
from openai.types.chat import ChatCompletionMessageParam

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from lightrag.utils import (
    wrap_embedding_func_with_attrs,
    safe_unicode_decode,
    logger,
)

import numpy as np


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(
        (RateLimitError, APIConnectionError, APIConnectionError)
    ),
)
async def azure_openai_complete_if_cache(
    model,
    prompt,
    system_prompt: str | None = None,
    history_messages: Iterable[ChatCompletionMessageParam] | None = None,
    enable_cot: bool = False,
    base_url: str | None = None,
    api_key: str | None = None,
    api_version: str | None = None,
    **kwargs,
):
    if enable_cot:
        logger.debug(
            "enable_cot=True is not supported for the Azure OpenAI API and will be ignored."
        )
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT") or model or os.getenv("LLM_MODEL")
    base_url = (
        base_url or os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("LLM_BINDING_HOST")
    )
    api_key = (
        api_key or os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("LLM_BINDING_API_KEY")
    )
    api_version = (
        api_version
        or os.getenv("AZURE_OPENAI_API_VERSION")
        or os.getenv("OPENAI_API_VERSION")
    )

    # Validate required configuration
    if not base_url:
        raise ValueError(
            "Azure OpenAI LLM endpoint is not configured. "
            "Please set AZURE_OPENAI_ENDPOINT or LLM_BINDING_HOST in your .env file. "
            "Example: AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/"
        )
    
    if not api_key:
        raise ValueError(
            "Azure OpenAI LLM API key is not configured. "
            "Please set AZURE_OPENAI_API_KEY or LLM_BINDING_API_KEY in your .env file."
        )
    
    if not api_version:
        raise ValueError(
            "Azure OpenAI API version is not configured. "
            "Please set AZURE_OPENAI_API_VERSION or OPENAI_API_VERSION in your .env file. "
            "Example: AZURE_OPENAI_API_VERSION=2024-02-15-preview"
        )
    
    # Validate endpoint format
    if not base_url.startswith(("http://", "https://")):
        raise ValueError(
            f"Invalid Azure OpenAI endpoint format: {base_url}. "
            "Endpoint must start with http:// or https://"
        )

    kwargs.pop("hashing_kv", None)
    kwargs.pop("keyword_extraction", None)
    timeout = kwargs.pop("timeout", None)

    openai_async_client = AsyncAzureOpenAI(
        azure_endpoint=base_url,
        azure_deployment=deployment,
        api_key=api_key,
        api_version=api_version,
        timeout=timeout,
    )
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if history_messages:
        messages.extend(history_messages)
    if prompt is not None:
        messages.append({"role": "user", "content": prompt})

    if "response_format" in kwargs:
        response = await openai_async_client.beta.chat.completions.parse(
            model=model, messages=messages, **kwargs
        )
    else:
        response = await openai_async_client.chat.completions.create(
            model=model, messages=messages, **kwargs
        )

    if hasattr(response, "__aiter__"):

        async def inner():
            async for chunk in response:
                if len(chunk.choices) == 0:
                    continue
                content = chunk.choices[0].delta.content
                if content is None:
                    continue
                if r"\u" in content:
                    content = safe_unicode_decode(content.encode("utf-8"))
                yield content

        return inner()
    else:
        content = response.choices[0].message.content
        if r"\u" in content:
            content = safe_unicode_decode(content.encode("utf-8"))
        return content


async def azure_openai_complete(
    prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
) -> str:
    kwargs.pop("keyword_extraction", None)
    result = await azure_openai_complete_if_cache(
        os.getenv("LLM_MODEL", "gpt-4o-mini"),
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        **kwargs,
    )
    return result


@wrap_embedding_func_with_attrs(embedding_dim=1536)
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(
        (RateLimitError, APIConnectionError, APITimeoutError)
    ),
)
async def azure_openai_embed(
    texts: list[str],
    model: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    api_version: str | None = None,
) -> np.ndarray:
    deployment = (
        os.getenv("AZURE_EMBEDDING_DEPLOYMENT")
        or model
        or os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    )
    base_url = (
        base_url
        or os.getenv("AZURE_EMBEDDING_ENDPOINT")
        or os.getenv("EMBEDDING_BINDING_HOST")
    )
    api_key = (
        api_key
        or os.getenv("AZURE_EMBEDDING_API_KEY")
        or os.getenv("EMBEDDING_BINDING_API_KEY")
    )
    api_version = (
        api_version
        or os.getenv("AZURE_EMBEDDING_API_VERSION")
        or os.getenv("OPENAI_API_VERSION")
    )

    # Validate required configuration
    if not base_url:
        raise ValueError(
            "Azure OpenAI embedding endpoint is not configured. "
            "Please set AZURE_EMBEDDING_ENDPOINT or EMBEDDING_BINDING_HOST in your .env file. "
            "Example: AZURE_EMBEDDING_ENDPOINT=https://your-resource-name.openai.azure.com/"
        )
    
    if not api_key:
        raise ValueError(
            "Azure OpenAI embedding API key is not configured. "
            "Please set AZURE_EMBEDDING_API_KEY or EMBEDDING_BINDING_API_KEY in your .env file."
        )
    
    if not api_version:
        raise ValueError(
            "Azure OpenAI API version is not configured. "
            "Please set AZURE_EMBEDDING_API_VERSION or OPENAI_API_VERSION in your .env file. "
            "Example: AZURE_EMBEDDING_API_VERSION=2024-02-15-preview"
        )
    
    # Validate endpoint format
    if not base_url.startswith(("http://", "https://")):
        raise ValueError(
            f"Invalid Azure OpenAI endpoint format: {base_url}. "
            "Endpoint must start with http:// or https://"
        )

    try:
        openai_async_client = AsyncAzureOpenAI(
            azure_endpoint=base_url,
            azure_deployment=deployment,
            api_key=api_key,
            api_version=api_version,
        )

        response = await openai_async_client.embeddings.create(
            model=model, input=texts, encoding_format="float"
        )
        return np.array([dp.embedding for dp in response.data])
    except APIConnectionError as e:
        logger.error(
            f"Failed to connect to Azure OpenAI endpoint: {base_url}. "
            f"Please verify your AZURE_EMBEDDING_ENDPOINT configuration. Error: {e}"
        )
        raise
