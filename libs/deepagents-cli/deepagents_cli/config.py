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
  ;                                                                                                                     
  ED.                                                                                                                   
  E#Wi         :                                                                              ,;L.                      
  E###G.       Ef                         .                                       .Gt       f#i EW:        ,ft          
  E#fD#W;      E#t             ..       : Ef.                          ..        j#W:     .E#t  E##;       t#E GEEEEEEEL
  E#t t##L     E#t            ,W,     .Et E#Wi                        ;W,      ;K#f      i#W,   E###t      t#E ,;;L#K;;.
  E#t  .E#K,   E#t           t##,    ,W#t E#K#D:                     j##,    .G#D.      L#D.    E#fE#f     t#E    t#E   
  E#t    j##f  E#t fi       L###,   j###t E#t,E#f.  .......         G###,   j#K;      :K#Wfff;  E#t D#G    t#E    t#E   
  E#t    :E#K: E#t L#j    .E#j##,  G#fE#t E#WEE##Wt .AS-FUCK.     :E####, ,K#f   ,GD; i##WLLLLt E#t  f#E.  t#E    t#E   
  E#t   t##L   E#t L#L   ;WW; ##,:K#i E#t E##Ei;;;;.             ;W#DG##,  j#Wi   E#t  .E#L     E#t   t#K: t#E    t#E   
  E#t .D#W;    E#tf#E:  j#E.  ##f#W,  E#t E#DWWt                j###DW##,   .G#D: E#t    f#E:   E#t    ;#W,t#E    t#E   
  E#tiW#G.     E###f  .D#L    ###K:   E#t E#t f#K;             G##i,,G##,     ,K#fK#t     ,WW;  E#t     :K#D#E    t#E   
  E#K##i       E#K,  :K#t     ##D.    E#t E#Dfff##E,         :K#K:   L##,       j###t      .D#; E#t      .E##E    t#E   
  E##D.        EL    ...      #G      ..  jLLLLLLLLL;       ;##D.    L##,        .G#t        tt ..         G#E     fE   
  E#t          :              j                             ,,,      .,,           ;;                       fE      :   
  L:                                                                                                         ,          
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
            api_key="NA"
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
