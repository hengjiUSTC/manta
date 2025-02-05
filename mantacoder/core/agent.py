import logging
import os
from typing import List, Optional

from mantacoder.core.command_classifier import CommandClassifier, CommandType
from mantacoder.core.config import Config
from mantacoder.core.reply_handler import ReplyHandler, ResponseType
from mantacoder.llm.client import LLMClient
from mantacoder.prompts.system_prompt import system_prompt as prompt_template
from mantacoder.session.history import ConversationHistory
from mantacoder.session.manager import IOSessionManager


class CodeAgent:
    def __init__(self, config: Config):
        self.name = config.name
        self.config = config
        self.client = LLMClient(config)

        # Initialize conversation history
        self.conversation_history = ConversationHistory()
        self.reply_handler = ReplyHandler(self.config, self.conversation_history)

        self.session_manager = IOSessionManager(self.conversation_history)

        # Initialize system prompt
        system_prompt = self._create_system_prompt()
        self.conversation_history.add_system_message(system_prompt=system_prompt)
        logging.debug(system_prompt)

    def _get_files_tree(self) -> List[str]:
        """Get the current directory file tree."""
        working_dir = os.getcwd()
        logging.debug(f"Working directory: {working_dir}")
        files_tree = []

        try:
            for item in os.listdir(working_dir):
                logging.debug(f"Item: {item}")
                full_path = os.path.join(working_dir, item)
                if os.path.isdir(full_path):
                    files_tree.append(f"[DIR] {item}/")
                else:
                    files_tree.append(f"[FILE] {item}")
        except OSError as e:
            logging.debug(f"Warning: Error reading directory structure: {e}")

        return files_tree

    def _create_system_prompt(self) -> str:
        """Create the system prompt with current directory information."""
        working_directory = os.getcwd()
        files_tree = self._get_files_tree()

        tools_description = self.reply_handler.get_tools_description()

        return (
            prompt_template.replace("{working_directory}", working_directory)
            .replace("{files_tree}", "\n".join(files_tree))
            .replace("{tools_description}", tools_description)
        )

    def _parse_and_attach_files(self, command: str) -> Optional[str]:
        return self.session_manager.attach_files(command)

    def _handle_response_loop(self, initial_response: str):
        """Handle the response loop including multiple tool calls."""
        current_response = initial_response

        while True:
            processed = self.reply_handler.process_response(current_response)

            if processed.type == ResponseType.FINAL_RESPONSE:
                self.session_manager.io.print_message(processed.content)
                break
            elif (
                processed.tool_name
                and processed.tool_params
                and processed.type == ResponseType.TOOL_CALL
            ):
                self.session_manager.io.print_tool_execution(
                    processed.tool_name, processed.tool_params, current_response
                )

                if self.reply_handler._ask_permission(processed.tool_name):
                    # Execute tool and get result
                    self.reply_handler.execute_tool(
                        processed.tool_name, processed.tool_params
                    )

                    # Get next response from LLM
                    current_response = self.reply_handler.get_next_response()
                    if not current_response:
                        break
                else:
                    # Handle tool denial
                    self.reply_handler.handle_tool_denial(processed.tool_name)
                    break

    def run(self):
        self.session_manager.io.print_welcome(self.name)

        while True:
            try:
                command = self.session_manager.io.prompt("Enter a command: ")

                if command.lower() == "exit":
                    self.session_manager.io.print_goodbye()
                    break

                command_type = CommandClassifier.classify(command)

                if command_type == CommandType.FILE_ATTACH:
                    parsed_file = self._parse_and_attach_files(command)
                    if parsed_file:
                        self.conversation_history.add_message("user", parsed_file)
                    continue
                elif command_type == CommandType.SHOW_HISTORY:
                    history = self.conversation_history.get_context()
                    for message in history:
                        print(f"{message['role']}: {message['content']}")
                    self.session_manager.io.print_conversation_history(
                        history,
                        len(self.conversation_history.messages),
                        self.conversation_history.get_total_tokens(),
                    )
                    continue
                else:
                    if len(command) > 1:
                        self.conversation_history.add_message("user", command)

                    logging.debug(
                        f"send command: {self.conversation_history.get_context}"
                    )
                    initial_response = self.client.chat(
                        self.conversation_history.get_context()
                    )

                    if initial_response:
                        self._handle_response_loop(initial_response)

            except KeyboardInterrupt:
                continue
            except EOFError:
                break
