class AgentError(Exception):
    """Base exception for all agent errors."""

    pass


class ConfigError(AgentError):
    """Configuration related errors."""

    pass


class LLMError(AgentError):
    """LLM service related errors."""

    pass


class ToolError(AgentError):
    """Tool related errors."""

    pass


class ToolExecutionError(ToolError):
    """Error during tool execution."""

    pass


class ToolValidationError(ToolError):
    """Error during tool validation."""

    pass


class SessionError(AgentError):
    """Session related errors."""

    pass


class InputError(AgentError):
    """Input handling related errors."""

    pass
