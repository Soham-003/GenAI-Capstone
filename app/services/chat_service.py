from __future__ import annotations

from time import perf_counter

from openai import OpenAI

from app.agents.actions import trigger_quality_check
from app.config import settings
from app.models import ChatResponse
from app.observability.metrics import LATENCY_SECONDS, QUALITY_ACTION_COUNT, REQUEST_COUNT
from app.rag.retriever import Retriever


class ChatService:
    def __init__(self, retriever: Retriever | None = None) -> None:
        self.retriever = retriever or Retriever()
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def _extract_style(self, message: str) -> tuple[str, str]:
        """Extract response style from message like '[Style] Question'"""
        if message.startswith("[") and "]" in message:
            end_bracket = message.index("]")
            style = message[1:end_bracket].strip()
            question = message[end_bracket + 1:].strip()
            return style, question
        return "Standard Answer", message

    def _build_style_prompt(self, style: str, user_message: str, context_blocks: list[str]) -> str:
        """Build style-specific system prompt and user message"""
        context = "\n\n".join(context_blocks) if context_blocks else "No context found."
        
        style_instructions = {
            "Standard Answer": {
                "system": (
                    "You are a helpful data engineering expert who explains things in simple, easy-to-understand terms. "
                    "Assume the user may not have technical background. Always:\n"
                    "- Use simple, everyday language\n"
                    "- Explain technical terms when you use them\n"
                    "- Break down complex ideas into small steps\n"
                    "- Be direct and to the point\n"
                    "- Use examples when helpful"
                ),
                "temperature": 0.3,
                "instruction": "Answer this question clearly and simply. Explain what it means and why it matters."
            },
            "Executive Summary": {
                "system": (
                    "You are a business-focused consultant who helps non-technical people understand data topics. "
                    "Your goal is to explain the 'what' and 'why', not the technical 'how'. Always:\n"
                    "- Focus on business impact and importance\n"
                    "- Use business terms, not technical jargon\n"
                    "- Highlight what matters to the business\n"
                    "- Keep it brief and actionable\n"
                    "- Start with the key takeaway"
                ),
                "temperature": 0.4,
                "instruction": "Provide a brief, business-focused summary. Start with the key takeaway. Focus on why this matters, not technical details."
            },
            "Root Cause Style": {
                "system": (
                    "You are a problem-solving expert who helps people understand the underlying reasons for issues. "
                    "Explain things step-by-step in simple terms. Always:\n"
                    "- Identify the main issue\n"
                    "- Explain the root cause in simple terms\n"
                    "- Show how problems connect\n"
                    "- Make it understandable for non-technical people\n"
                    "- Be thorough but clear"
                ),
                "temperature": 0.5,
                "instruction": "Analyze what the core issue is. Explain the root causes in simple, step-by-step terms that anyone can understand. Focus on 'why' something happens."
            },
            "Runbook Steps": {
                "system": (
                    "You are a helpful guide who creates clear, step-by-step instructions. "
                    "Make sure anyone can follow your steps, regardless of technical knowledge. Always:\n"
                    "- Number each step clearly\n"
                    "- Use simple language\n"
                    "- Explain what each step does\n"
                    "- Say what to look for to know it worked\n"
                    "- Include what to do if something goes wrong"
                ),
                "temperature": 0.3,
                "instruction": "Create clear, numbered steps that anyone can follow. Explain what each step does and how to know if it worked."
            }
        }
        
        style_config = style_instructions.get(style, style_instructions["Standard Answer"])
        
        system_prompt = (
            f"{style_config['system']}\n\n"
            "Available Context:\n"
            f"{context}"
        )
        
        user_prompt = (
            f"{style_config['instruction']}\n\n"
            f"Question: {user_message}"
        )
        
        return system_prompt, user_prompt, style_config['temperature']

    def _generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.3) -> str:
        """Generate response from OpenAI (non-streaming)."""
        if not self.client:
            return f"[Mock Response]\n{prompt[:500]}"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=temperature,
            max_tokens=1000,
            stream=False,
        )
        
        return response.choices[0].message.content or "No response generated."

    def _generate_stream(self, prompt: str, system_prompt: str = None, temperature: float = 0.3):
        """Generate response from OpenAI with streaming (yields tokens)."""
        if not self.client:
            # Return mock response without streaming
            for word in prompt[:500].split():
                yield word + " "
            return

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=temperature,
            max_tokens=1000,
            stream=True,
        )
        
        # Stream mode: yield tokens as they arrive
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def chat(self, message: str, run_quality_check: bool = False) -> ChatResponse:
        """Main chat orchestrator - returns full ChatResponse."""
        start = perf_counter()
        REQUEST_COUNT.inc()
        
        # Extract style and clean question
        style, clean_question = self._extract_style(message)
        
        # Get relevant context
        citations = self.retriever.search(clean_question, top_k=5)
        
        # Build style-specific prompt
        system_prompt, user_prompt, temperature = self._build_style_prompt(
            style, clean_question, [c.content for c in citations]
        )
        
        # Generate answer with style-specific temperature
        answer = self._generate(user_prompt, system_prompt, temperature)
        
        action_result = None
        if run_quality_check:
            QUALITY_ACTION_COUNT.inc()
            action_result = trigger_quality_check()
            answer = f"{answer}\n\nAgent action result:\n{action_result}"

        LATENCY_SECONDS.observe(perf_counter() - start)
        return ChatResponse(answer=answer, citations=citations, quality_check_result=action_result)

    def chat_stream(self, message: str, run_quality_check: bool = False):
        """Stream response token-by-token like ChatGPT."""
        start = perf_counter()
        REQUEST_COUNT.inc()
        
        # Extract style and clean question
        style, clean_question = self._extract_style(message)
        
        # Get relevant context
        citations = self.retriever.search(clean_question, top_k=5)
        
        # Build style-specific prompt
        system_prompt, user_prompt, temperature = self._build_style_prompt(
            style, clean_question, [c.content for c in citations]
        )
        
        # Stream tokens from the generator
        for token in self._generate_stream(user_prompt, system_prompt, temperature):
            yield token
        
        LATENCY_SECONDS.observe(perf_counter() - start)
