from typing import List, Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import FormattedText
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from mantacoder.session.history import ConversationHistory

# Color definitions using standard color codes
CYAN = "#00FFFF"  # Standard cyan color
DIMMED_CYAN = "#009999"  # Darker/dimmed cyan for labels
BLUE = "#0000FF"
YELLOW = "#FFFF00"
RED = "#FF0000"
GREEN = "#00FF00"
MAGENTA = "#FF00FF"

custom_theme = Theme(
    {
        "info": CYAN,
        "warning": YELLOW,
        "error": RED,
        "success": GREEN,
        "system": MAGENTA,
        "user": BLUE,
        "assistant": GREEN,
        "tool": YELLOW,
        "separator": f"dim {CYAN}",  # Using standard Rich color name with dim modifier
        "stat_label": DIMMED_CYAN,
        "stat_value": f"{CYAN} bold",
    }
)


class IO:
    def __init__(
        self, session: PromptSession, conversation_history: ConversationHistory
    ):
        self.session = session
        self.conversation_history = conversation_history
        self.console = Console(theme=custom_theme)

    def _print_conversation_status(self):
        """Print current conversation status in a single line"""
        total_messages = len(self.conversation_history.messages)
        total_tokens = self.conversation_history.get_total_tokens()

        # Create horizontal line with consistent width
        width = self.console.width if self.console.width else 80
        self.console.print("─" * width, style="separator")

        # Create status text with properly styled components
        status = Text()
        status.append("Messages: ", style="stat_label")
        status.append(str(total_messages), style="stat_value")
        status.append(" | ", style="separator")
        status.append("Tokens: ", style="stat_label")
        status.append(str(total_tokens), style="stat_value")

        # Print status line
        self.console.print(status)

    def prompt(self, message: str) -> str:
        """Handle input prompts with rich formatting and status display"""
        # Print status and separator line above prompt
        self._print_conversation_status()

        # Create properly formatted text using HTML-style formatting
        formatted_message = FormattedText([("class:prompt", message)])

        # Use prompt_toolkit's prompt with formatted message
        return self.session.prompt(formatted_message)

    def print_welcome(self, agent_name: str):
        """Print welcome message in a decorated panel"""
        welcome_msg = f"Hello, I am {agent_name}, your enhanced agent."
        self.console.print(
            Panel(welcome_msg, title="Welcome", border_style="cyan", box=box.ROUNDED)
        )

    def print_goodbye(self):
        """Print goodbye message in a decorated panel"""
        self.console.print(
            Panel(
                "Goodbye! Thank you for using the agent.",
                title="Goodbye",
                border_style="cyan",
                box=box.ROUNDED,
            )
        )

    def print_message(self, message: str, style: str = "info"):
        """Print regular messages with optional style"""
        text = Text(message)
        self.console.print(text, style=style)

    def print_tool_execution(self, tool_name: str, tool_params: dict, messsage: str):
        self.print_message(messsage)

        """Print tool execution details in a structured format"""
        tool_table = Table(show_header=False, box=box.SIMPLE)
        tool_table.add_column("Property", style="tool")
        tool_table.add_column("Value")

        tool_table.add_row("Tool", tool_name)
        for param, value in tool_params.items():
            tool_table.add_row("Parameter", f"{param}: {value}")

        self.console.print(
            Panel(
                tool_table,
                title="Tool Execution",
                border_style="yellow",
                box=box.ROUNDED,
            )
        )

    def print_file_attachment(self, file_path: str):
        """Print file attachment confirmation with style"""
        self.console.print(f"✓ File attached: [success]{file_path}[/success]")

    def print_conversation_history(
        self, history: List[dict], total_messages: int, total_tokens: int
    ):
        """Print conversation history in a structured format"""
        history_table = Table(
            title="Conversation History",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold",
        )
        history_table.add_column("Role", style="cyan")
        history_table.add_column("Content")

        for message in history:
            # Handle different message types with appropriate styling
            role = message["role"]
            content = message["content"]

            # If content is code, format it with syntax highlighting
            if "```" in content:
                parts = content.split("```")
                for i, part in enumerate(parts):
                    if i % 2 == 1:  # Code block
                        try:
                            lang, code = part.split("\n", 1)
                        except ValueError:
                            lang, code = "text", part
                        content = str(
                            Syntax(code.strip(), lang.strip(), theme="monokai")
                        )

            history_table.add_row(role, content)

        self.console.print(history_table)
        self.console.print(
            f"Total messages: [info]{total_messages}[/info], Tokens: [info]{total_tokens}[/info]"
        )

    def print_error(self, error_message: str):
        """Print error messages in a distinctive style"""
        self.console.print(
            Panel(
                f"[error]{error_message}[/error]",
                title="Error",
                border_style="red",
                box=box.ROUNDED,
            )
        )

    def print_code(self, code: str, language: str = "python"):
        """Print code with syntax highlighting"""
        syntax = Syntax(code, language, theme="monokai")
        self.console.print(syntax)

    def print_markdown(self, markdown_text: str):
        """Print markdown-formatted text"""
        markdown = Markdown(markdown_text)
        self.console.print(markdown)

    def print_status(self, status: str, style: str = "info"):
        """Print status messages with appropriate styling"""
        self.console.print(f"[{style}]>>> {status}[/{style}]")

    def print_divider(self):
        """Print a divider line"""
        self.console.rule()
