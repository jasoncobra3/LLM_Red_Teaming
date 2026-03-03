"""
LLM Factory – creates LangChain chat model instances and wraps them as
DeepEvalBaseLLM so they can be plugged into DeepTeam as attacker / target.
"""

from __future__ import annotations

import asyncio
from typing import Any, Optional

from deepeval.models import DeepEvalBaseLLM
from config.settings import settings


# -----------------------------------------------------------------------
# LangChain → DeepEvalBaseLLM adapter
# -----------------------------------------------------------------------

class LangChainAdapter(DeepEvalBaseLLM):
    """
    Wraps any LangChain BaseChatModel into the DeepEvalBaseLLM interface
    so DeepTeam can use it as a simulator or evaluation model.
    """

    def __init__(self, chat_model: Any, model_name: str):
        self._chat_model = chat_model
        self._model_name = model_name
        self._supports_json_mode = self._check_json_mode_support()
        # Do NOT call super().__init__ with model= because we
        # override load_model / get_model_name ourselves.
        super().__init__(model=model_name)
    
    def _check_json_mode_support(self) -> bool:
        """Check if the underlying model supports JSON mode."""
        model_class_name = type(self._chat_model).__name__
        # OpenAI and Azure OpenAI models support JSON mode
        return model_class_name in ['ChatOpenAI', 'AzureChatOpenAI']

    def load_model(self) -> Any:
        return self._chat_model

    def generate(self, prompt: str, schema: Any = None, **kwargs) -> str:
        from langchain_core.messages import HumanMessage
        import json

        # For schema-based generation, try to use JSON mode if available
        if schema is not None:
            # Check if the model supports JSON mode (OpenAI models)
            if self._supports_json_mode and hasattr(self._chat_model, 'model_kwargs'):
                original_kwargs = self._chat_model.model_kwargs.copy() if self._chat_model.model_kwargs else {}
                self._chat_model.model_kwargs = self._chat_model.model_kwargs or {}
                self._chat_model.model_kwargs['response_format'] = {"type": "json_object"}
                
                # Ensure prompt asks for JSON
                json_prompt = f"{prompt}\n\nYou must respond with valid JSON only."
                try:
                    response = self._chat_model.invoke([HumanMessage(content=json_prompt)])
                    # Restore original kwargs
                    self._chat_model.model_kwargs = original_kwargs
                    return response.content
                except Exception as e:
                    # Restore and fallback
                    self._chat_model.model_kwargs = original_kwargs
                    raise TypeError(f"JSON mode failed: {e}. Using fallback.")
            else:
                # For other models, raise TypeError to trigger DeepTeam's JSON fallback
                raise TypeError("Schema-based generation not supported, use JSON fallback")
        
        response = self._chat_model.invoke([HumanMessage(content=prompt)])
        return response.content

    async def a_generate(self, prompt: str, schema: Any = None, **kwargs) -> str:
        from langchain_core.messages import HumanMessage
        import json

        # For schema-based generation, try to use JSON mode if available
        if schema is not None:
            # Check if the model supports JSON mode (OpenAI models)
            if self._supports_json_mode and hasattr(self._chat_model, 'model_kwargs'):
                original_kwargs = self._chat_model.model_kwargs.copy() if self._chat_model.model_kwargs else {}
                self._chat_model.model_kwargs = self._chat_model.model_kwargs or {}
                self._chat_model.model_kwargs['response_format'] = {"type": "json_object"}
                
                # Ensure prompt asks for JSON
                json_prompt = f"{prompt}\n\nYou must respond with valid JSON only."
                try:
                    response = await self._chat_model.ainvoke([HumanMessage(content=json_prompt)])
                    # Restore original kwargs
                    self._chat_model.model_kwargs = original_kwargs
                    return response.content
                except Exception as e:
                    # Restore and fallback
                    self._chat_model.model_kwargs = original_kwargs
                    raise TypeError(f"JSON mode failed: {e}. Using fallback.")
            else:
                # For other models, raise TypeError to trigger DeepTeam's JSON fallback
                raise TypeError("Schema-based generation not supported, use JSON fallback")

        response = await self._chat_model.ainvoke([HumanMessage(content=prompt)])
        return response.content

    def get_model_name(self) -> str:
        return self._model_name


# -----------------------------------------------------------------------
# Factory functions – one per provider
# -----------------------------------------------------------------------

def _build_openai(model: str, **kw) -> Any:
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=model,
        api_key=kw.get("api_key") or settings.OPENAI_API_KEY,
        temperature=kw.get("temperature", 0.0),
    )


def _build_anthropic(model: str, **kw) -> Any:
    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(
        model=model,
        api_key=kw.get("api_key") or settings.ANTHROPIC_API_KEY,
        temperature=kw.get("temperature", 0.0),
    )


def _build_azure_openai(model: str, **kw) -> Any:
    from langchain_openai import AzureChatOpenAI

    return AzureChatOpenAI(
        azure_deployment=kw.get("deployment") or settings.AZURE_OPENAI_DEPLOYMENT_NAME or model,
        api_key=kw.get("api_key") or settings.AZURE_OPENAI_API_KEY,
        azure_endpoint=kw.get("endpoint") or settings.AZURE_OPENAI_ENDPOINT,
        api_version=kw.get("api_version") or settings.AZURE_OPENAI_API_VERSION,
        temperature=kw.get("temperature", 0.0),
    )


def _build_google_gemini(model: str, **kw) -> Any:
    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=kw.get("api_key") or settings.GOOGLE_API_KEY,
        temperature=kw.get("temperature", 0.0),
    )


def _build_aws_bedrock(model: str, **kw) -> Any:
    from langchain_aws import ChatBedrockConverse

    return ChatBedrockConverse(
        model=model,
        region_name=kw.get("region") or settings.AWS_DEFAULT_REGION,
        temperature=kw.get("temperature", 0.0),
    )


def _build_huggingface(model: str, **kw) -> Any:
    from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

    endpoint = HuggingFaceEndpoint(
        repo_id=model,
        huggingfacehub_api_token=kw.get("api_key") or settings.HUGGINGFACEHUB_API_TOKEN,
        temperature=kw.get("temperature", 0.01),
    )
    return ChatHuggingFace(llm=endpoint)


def _build_groq(model: str, **kw) -> Any:
    from langchain_groq import ChatGroq

    return ChatGroq(
        model=model,
        api_key=kw.get("api_key") or settings.GROQ_API_KEY,
        temperature=kw.get("temperature", 0.0),
    )


def _build_deepseek(model: str, **kw) -> Any:
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=model,
        api_key=kw.get("api_key") or settings.DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com/v1",
        temperature=kw.get("temperature", 0.0),
    )


# -----------------------------------------------------------------------
# Provider dispatch map
# -----------------------------------------------------------------------

_BUILDERS = {
    "openai": _build_openai,
    "anthropic": _build_anthropic,
    "azure_openai": _build_azure_openai,
    "google_gemini": _build_google_gemini,
    "aws_bedrock": _build_aws_bedrock,
    "huggingface": _build_huggingface,
    "groq": _build_groq,
    "deepseek": _build_deepseek,
}


# -----------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------

def create_chat_model(provider: str, model: str, **kwargs) -> Any:
    """
    Create a raw LangChain chat model for the given provider + model name.
    Extra kwargs (api_key, temperature, …) are forwarded to the builder.
    """
    builder = _BUILDERS.get(provider)
    if builder is None:
        raise ValueError(f"Unsupported provider: {provider}")
    return builder(model, **kwargs)


def create_deepeval_model(provider: str, model: str, **kwargs) -> LangChainAdapter:
    """
    Create a DeepEvalBaseLLM-compatible wrapper around a LangChain model.
    This is what you pass to DeepTeam's RedTeamer as simulator_model or target.
    """
    chat_model = create_chat_model(provider, model, **kwargs)
    return LangChainAdapter(chat_model, model_name=f"{provider}/{model}")


def create_target_callback(provider: str, model: str, **kwargs):
    """
    Returns a simple callable(prompt) -> response string,
    suitable for passing as `model_callback` to RedTeamer.red_team().
    """
    chat_model = create_chat_model(provider, model, **kwargs)

    def _callback(prompt: str, conversation_history=None) -> str:
        from langchain_core.messages import HumanMessage, AIMessage

        messages = []
        if conversation_history:
            for turn in conversation_history:
                messages.append(HumanMessage(content=turn.input))
                if turn.response:
                    messages.append(AIMessage(content=turn.response))
        messages.append(HumanMessage(content=prompt))
        response = chat_model.invoke(messages)
        return response.content

    return _callback


def create_async_target_callback(provider: str, model: str, **kwargs):
    """
    Returns an async callable(prompt) -> response string,
    required when RedTeamer uses async_mode=True.
    """
    from utils.logger import get_logger
    logger = get_logger(__name__)
    
    chat_model = create_chat_model(provider, model, **kwargs)
    call_count = {"count": 0}

    async def _async_callback(prompt: str, conversation_history=None) -> str:
        from langchain_core.messages import HumanMessage, AIMessage

        call_count["count"] += 1
        if call_count["count"] % 50 == 1:  # Log every 50th call
            logger.info(f"Target callback called {call_count['count']} times")
        
        try:
            messages = []
            if conversation_history:
                for turn in conversation_history:
                    messages.append(HumanMessage(content=turn.input))
                    if turn.response:
                        messages.append(AIMessage(content=turn.response))
            messages.append(HumanMessage(content=prompt))
            response = await chat_model.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error in target callback: {e}")
            # Return a safe error message instead of raising
            return f"Error: {str(e)}"

    return _async_callback
