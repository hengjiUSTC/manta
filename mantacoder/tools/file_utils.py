import os


class FileUtils:
    @staticmethod
    def ensure_directory(path: str) -> None:
        dir_path = os.path.dirname(path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

    @staticmethod
    def read_file(path: str) -> str:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()

    @staticmethod
    def write_file(path: str, content: str) -> None:
        FileUtils.ensure_directory(path)
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)
