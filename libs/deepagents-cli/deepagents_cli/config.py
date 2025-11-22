"""Configuration, constants, and model creation for the CLI."""

import os
import sys
from pathlib import Path

import dotenv
from rich.console import Console

dotenv.load_dotenv()

# Color scheme
COLORS = {
    "primary": "#10b981",
    "dim": "#6b7280",
    "user": "#ffffff",
    "agent": "#10b981",
    "thinking": "#34d399",
    "tool": "#fbbf24",
}

# ASCII art banner

DEEP_AGENTS_ASCII = """
 ,gggggggggggg,                                               
dP ""88nosockY8b,             ,dPYb,     ,dPYb,               
Yb,  88       `8b,            IP'`Yb     IP'`Yb               
 `"  88        `8b            I8  8I     I8  8I               
     88         Y8            I8  8'     I8  8'               
     88         d8  ,ggggg,   I8 dP      I8 dP      gg     gg 
     88        ,8P dP"  "Y8gggI8dP   88ggI8dP   88ggI8     8I 
     88       ,8P'i8'    ,8I  I8P    8I  I8P    8I  I8,   ,8I 
     88______,dP',d8,   ,d8' ,d8b,  ,8I ,d8b,  ,8I ,d8b, ,d8I 
    888888888P"  P"Y8888P"   8P'"Y88P"' 8P'"Y88P"' P""Y88P"888
                                                         ,d8I'
                                                       ,dP'8I 
                                                      ,8"  8I 
    🪄 P E R S O N A L - A I - E L F 🪄                I8   8I 
                                                      `8, ,8I 
                                                       `Y8P"  
"""


# Interactive commands
COMMANDS = {
    "clear": "Clear screen and reset conversation",
    "help": "Show help information",
    "tokens": "Show token usage for current session",
    "quit": "Exit the CLI",
    "exit": "Exit the CLI",
}


# Maximum argument length for display
MAX_ARG_LENGTH = 150

# Agent configuration
config = {"recursion_limit": 1000}

# Rich console instance
console = Console(highlight=False)


class SessionState:
    """Holds mutable session state (auto-approve mode, etc)."""

    def __init__(self, auto_approve: bool = False):
        self.auto_approve = auto_approve
        self.exit_hint_until: float | None = None
        self.exit_hint_handle = None

    def toggle_auto_approve(self) -> bool:
        """Toggle auto-approve and return new state."""
        self.auto_approve = not self.auto_approve
        return self.auto_approve


def get_default_coding_instructions() -> str:
    """Get the default coding agent instructions.

    These are the immutable base instructions that cannot be modified by the agent.
    Long-term memory (agent.md) is handled separately by the middleware.
    """
    default_prompt_path = Path(__file__).parent / "default_agent_prompt.md"
    return default_prompt_path.read_text()


def create_model():
    """Create the appropriate model based on available API keys.

    Returns:
        ChatModel instance (OpenAI or Anthropic)

    Raises:
        SystemExit if no API key is configured
    """
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    llama_host = os.environ.get("LLAMA_CPP_ENV_HOST")
    

    if llama_host:
        from .local.local_chat import ChatOpenAILocal
        host_url = llama_host
        model = os.environ.get("LLAMA_CPP_ENV_MODEL")
        temp=0.9
        return ChatOpenAILocal(
            model=model,
            base_url=host_url,
            temperature=temp,
            api_key="NA",
            extra_body={"strict": True}  # enforce JSON tool calls
        )

    if openai_key:
        from langchain_openai import ChatOpenAI

        model_name = os.environ.get("OPENAI_MODEL", "gpt-5-mini")
        console.print(f"[dim]Using OpenAI model: {model_name}[/dim]")
        return ChatOpenAI(
            model=model_name,
            temperature=0.7,
        )
    if anthropic_key:
        from langchain_anthropic import ChatAnthropic

        model_name = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
        console.print(f"[dim]Using Anthropic model: {model_name}[/dim]")
        return ChatAnthropic(
            model_name=model_name,
            max_tokens=20000,
        )
    console.print("[bold red]Error:[/bold red] No API key configured.")
    console.print("\nPlease set one of the following environment variables:")
    console.print("  - OPENAI_API_KEY     (for OpenAI models like gpt-5-mini)")
    console.print("  - ANTHROPIC_API_KEY  (for Claude models)")
    console.print("\nExample:")
    console.print("  export OPENAI_API_KEY=your_api_key_here")
    console.print("\nOr add it to your .env file.")
    sys.exit(1)
