from enum import Enum


class CommandType(Enum):
    FILE_ATTACH = "file_attach"
    REGULAR = "regular"
    SHOW_HISTORY = "show_history"


class CommandClassifier:
    @staticmethod
    def classify(command: str) -> CommandType:
        if "@" in command:
            return CommandType.FILE_ATTACH
        if command == "history":
            return CommandType.SHOW_HISTORY
        else:
            return CommandType.REGULAR
