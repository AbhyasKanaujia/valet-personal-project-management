import os
import mimetypes
from typing import List, Union


class File:
    """
    Represents a file.

    Attributes:
      name (str): The name of the file.
      path (str): The path to the file.

    Methods:
      is_text_file(filepath): [static] Determine if a file is a text file based on its content and MIME type.
    """

    def __init__(self, name: str, path: str):
        """
        Initialize the File object.

        Args:
          name (str): The name of the file.
          path (str): The path to the file.
        """
        self.name = name
        self.path = path

    def __str__(self) -> str:
        return "Generic File: " + self.name

    def __repr__(self) -> str:
        return f"File(name='{self.name}', path='{self.path}')"

    def __eq__(self, other) -> bool:
        return isinstance(other, File) and self.path == other.path


class TextFile(File):
    """
    Represents a text file.

    Attributes:
      name (str): The name of the text file.
      path (str): The path to the text file.

    Methods:
      get_content(): Read and return the content of the text file.
    """

    def __init__(self, name: str, path: str):
        """
        Initialize the TextFile object and check if the path points to a text file before creating the object.

        Args:
          name (str): The name of the text file.
          path (str): The path to the text file.
        """
        if not self.is_text_file(path):
            raise ValueError(f"Path {path} does not point to a text file")
        super().__init__(name, path)

    def __eq__(self, other):
        """
        Check for equality between TextFile objects based on their text content.

        Args:
          other: The TextFile object to compare with.

        Returns:
          bool: True if the text content of both files is the same, False otherwise.
        """
        if not isinstance(other, TextFile):
            return False
        return self.get_content() == other.get_content()

    def get_content(self) -> str:
        """
        Read and return the content of the text file.
        """
        with open(self.path, 'r') as f:
            return f.read()

    @staticmethod
    def is_text_file(filepath: str) -> bool:
        """
        Determine if a file is a text file based on its content and MIME type.

        Args:
          filepath (str): The path to the file.

        Returns:
          bool: True if the file is a text file, False otherwise.
        """
        # Try using mimetypes
        mimetype, _ = mimetypes.guess_type(filepath)
        if mimetype and mimetype.startswith('text/'):
            return True

        # Fallback: Check file content for ASCII/UTF-8 characters
        try:
            with open(filepath, 'rb') as f:
                chunk = f.read(1024)  # Read the first 1KB
                return all(32 <= byte <= 127 or byte in (9, 10, 13) for byte in chunk)
        except Exception:
            return False


class Directory(File):
    """
    Represents a directory, which can contain other files and directories.

    Attributes:
      name (str): The name of the directory.
      path (str): The path to the directory.

    Methods:
      get_content(): Retrieve the contents of the directory, returning a list of File objects.
    """

    def __init__(self, name: str, path: str):
        """
        Initialize the Directory object and check if the path points to a directory before creating the object.

        Args:
          name (str): The name of the directory.
          path (str): The path to the directory.
        """
        if not os.path.isdir(path):
            raise ValueError(f"Path {path} does not point to a directory")
        super().__init__(name, path)

    def get_content(self) -> List[Union['Directory', TextFile, File]]:
        contents = []

        for entry in os.listdir(self.path):
            entry_path = os.path.join(self.path, entry)
            if os.path.isdir(entry_path):
                contents.append(Directory(entry, entry_path))
            elif os.path.isfile(entry_path):
                if TextFile.is_text_file(entry_path):
                    contents.append(TextFile(entry, entry_path))
                else:
                    contents.append(File(entry, entry_path))

        return contents

    def find_file_or_directory(self, name: str) -> Union['Directory', TextFile, File, None]:
        for entry in os.listdir(self.path):
            if entry == name:
                entry_path = os.path.join(self.path, entry)
                if os.path.isdir(entry_path):
                    return Directory(entry, entry_path)
                elif os.path.isfile(entry_path):
                    if TextFile.is_text_file(entry_path):
                        return TextFile(entry, entry_path)
                    else:
                        return File(entry, entry_path)
        return None
