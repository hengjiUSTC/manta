import logging
import os
import signal
from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import Style as PromptStyle

from manta.session.history import ConversationHistory
from manta.session.io import CYAN, IO

# Define prompt_toolkit styles using the same color
prompt_style = PromptStyle.from_dict(
    {
        "prompt": CYAN,
    }
)


class DynamicFileCompleter(Completer):
    def __init__(self, root_dir="."):
        self.root_dir = os.path.abspath(root_dir)

    def _get_completions_for_path(self, current_input: str, is_absolute: bool) -> list:
        completions = []

        # 确定搜索的基础目录
        if is_absolute:
            search_dir = (
                os.path.dirname(current_input) if current_input else os.path.sep
            )
            if not os.path.exists(search_dir):
                search_dir = os.path.sep
        else:
            search_dir = os.path.join(self.root_dir, os.path.dirname(current_input))
            if not os.path.exists(search_dir):
                search_dir = self.root_dir

        try:
            # 获取当前输入的最后一部分作为前缀匹配
            prefix = os.path.basename(current_input)

            # 列出目录下的所有文件和文件夹
            for name in os.listdir(search_dir):
                full_path = os.path.join(search_dir, name)

                if name.startswith(prefix):
                    # 根据路径类型生成适当的补全路径
                    if is_absolute:
                        completion_text = full_path
                    else:
                        completion_text = os.path.relpath(full_path, self.root_dir)

                    # 如果是目录，添加路径分隔符
                    if os.path.isdir(full_path):
                        completion_text += os.path.sep

                    completions.append(completion_text)

        except OSError:
            pass

        return completions

    def get_completions(self, document: Document, complete_event):
        text = document.text_before_cursor
        if "@" not in text:
            return

        # 找到最后一个 @ 符号后的文本
        last_at_index = text.rfind("@")
        input_after_at = text[last_at_index + 1 :]

        # 判断是否是绝对路径
        is_absolute = input_after_at.startswith(os.path.sep)

        # 获取补全列表
        completions = self._get_completions_for_path(input_after_at, is_absolute)

        # 生成补全建议
        for completion in completions:
            yield Completion(
                completion, start_position=-len(input_after_at), display=completion
            )


class IOSessionManager:
    def __init__(self, conversation_history: ConversationHistory):
        self.conversation_history = conversation_history
        self.session = self.create_prompt_session()
        self.io = IO(self.session, conversation_history)

    def get_file_content(self, file_path: str) -> Optional[str]:
        try:
            # 处理相对路径和绝对路径
            abs_path = os.path.abspath(file_path)
            with open(abs_path, "r", encoding="utf-8") as file:
                return file.read()
        except UnicodeDecodeError:
            logging.debug(
                f"Error reading file {file_path}: File encoding is not valid UTF-8."
            )
            return None
        except IOError as e:
            logging.debug(f"Error reading file {file_path}: {e}")
            return None

    def create_prompt_session(self):
        session = PromptSession(
            completer=DynamicFileCompleter(),
            complete_while_typing=True,
            key_bindings=self.create_key_bindings(),
            style=prompt_style,
        )
        return session

    def create_key_bindings(self):
        kb = KeyBindings()

        @kb.add(Keys.ControlZ)
        def _(event):
            os.kill(os.getpid(), signal.SIGTSTP)

        return kb

    def attach_files(self, command: str) -> Optional[str]:
        if "@" not in command:
            return None

        parts = command.split("@")
        file_paths = [path.strip() for path in parts[1:]]

        attached_contents = []

        # 处理所有文件路径
        for file_path in file_paths:
            abs_path = os.path.abspath(file_path)

            if os.path.isdir(abs_path):
                # If the path is a directory, recursively handle all its files
                for root, _, files in os.walk(abs_path):
                    for file_name in files:
                        full_file_path = os.path.join(root, file_name)
                        file_content = self.get_file_content(full_file_path)
                        if file_content:
                            self.io.print_file_attachment(full_file_path)
                            attached_contents.append((full_file_path, file_content))
            else:
                # If the path is a file, process it directly
                file_content = self.get_file_content(abs_path)
                if file_content:
                    self.io.print_file_attachment(file_path)
                    attached_contents.append((file_path, file_content))

        if not attached_contents:
            return None

        # 返回所有附加文件的内容
        result = []
        for path, content in attached_contents:
            result.append(f"{path}\n------file content------{content}")

        return "\n\n".join(result)
