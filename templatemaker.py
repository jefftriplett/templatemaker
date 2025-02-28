#!/usr/bin/env python3
"""
templatemaker.py - Python Template Generation Library

Given a list of text files in a similar format, templatemaker creates a
template that can extract data from files in that same format.

This implementation is a pure Python version of the original C/Python hybrid.

Copyright (c) 2007 Adrian Holovaty
License: BSD

Original: https://github.com/adrianholovaty/templatemaker
"""

import re
import os
from typing import List, Tuple, Dict, Optional, Union, Any


# Use the same marker character as the original C code
MARKER = "\x1f"


class NoMatch(Exception):
    """Raised when text doesn't match the template."""

    pass


def longest_common_substring(a: str, b: str) -> Tuple[int, int, int]:
    """
    Find the longest common substring between two strings.

    Args:
        a: First string to compare
        b: Second string to compare

    Returns:
        Tuple of (length, a_offset, b_offset)
    """
    # Create a matrix of zeros
    matrix = [[0 for _ in range(len(b) + 1)] for _ in range(len(a) + 1)]

    # Track best match
    max_length = 0
    a_end_pos = 0

    # Fill the matrix
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                matrix[i][j] = matrix[i - 1][j - 1] + 1
                if matrix[i][j] > max_length:
                    max_length = matrix[i][j]
                    a_end_pos = i
            else:
                matrix[i][j] = 0

    if max_length == 0:
        return 0, -1, -1

    a_start_pos = a_end_pos - max_length
    # Find b_start_pos by matching the substring found in a
    b_start_pos = b.find(a[a_start_pos:a_end_pos])

    return max_length, a_start_pos, b_start_pos


def make_template(template_str: str, new_str: str, tolerance: int = 0) -> str:
    """
    Creates a template from comparing template_str and new_str, with a given tolerance.

    Args:
        template_str: Current template string
        new_str: New string to learn
        tolerance: Minimum allowed length of text between holes

    Returns:
        The template string with markers for differences
    """
    # Base cases
    if not template_str and not new_str:
        return ""
    if not template_str or not new_str:
        return MARKER

    # Find longest common substring
    best_size, a_offset, b_offset = longest_common_substring(template_str, new_str)

    if best_size == 0:
        # No common substring found
        return MARKER

    # If the common part is shorter than tolerance, treat as if no match
    if tolerance > 0 and best_size <= tolerance:
        return MARKER

    # Process left parts
    left_template = ""
    if a_offset > 0 or b_offset > 0:
        if a_offset > 0 and b_offset > 0:
            # Both strings have content on the left
            left_template = make_template(
                template_str[:a_offset], new_str[:b_offset], tolerance
            )
        else:
            # Only one string has content on the left
            left_template = MARKER

    # Process right parts
    right_template = ""
    a_end = a_offset + best_size
    b_end = b_offset + best_size

    if a_end < len(template_str) or b_end < len(new_str):
        if a_end < len(template_str) and b_end < len(new_str):
            # Both strings have content on the right
            right_template = make_template(
                template_str[a_end:], new_str[b_end:], tolerance
            )
        else:
            # Only one string has content on the right
            right_template = MARKER

    # Build the complete template
    common_part = template_str[a_offset:a_end]
    return left_template + common_part + right_template


class Template:
    """
    Template class that can learn patterns from example strings and extract data.
    """

    def __init__(self, tolerance: int = 0, brain: Optional[str] = None):
        """
        Initialize a new template.

        Args:
            tolerance: Minimum allowed length of text between holes
            brain: Optional pre-existing template string
        """
        self._brain = brain
        self._tolerance = tolerance
        self.version = 0

    def clean(self, text: str) -> str:
        """
        Strips any unwanted stuff from the given Sample String.

        Args:
            text: The input text to clean

        Returns:
            Cleaned text
        """
        return re.sub(r"\r\n", "\n", text)

    def learn(self, text: str) -> Optional[bool]:
        """
        Learns the given Sample String.

        Args:
            text: The input text to learn

        Returns:
            - None if this is the first Sample String in this template
            - True if this Sample String created more holes in the template
            - False otherwise
        """
        text = self.clean(text)
        text = text.replace(MARKER, "")
        self.version += 1

        if self._brain is None:
            self._brain = text
            return None

        old_holes = self.num_holes()
        self._brain = make_template(self._brain, text, self._tolerance)
        return self.num_holes() > old_holes

    def as_text(self, custom_marker: str = "{{ HOLE }}") -> str:
        """
        Returns a display-friendly version of the template.

        Args:
            custom_marker: The string to use to mark template holes

        Returns:
            A readable template string
        """
        if self._brain is None:
            return ""
        return self._brain.replace(MARKER, custom_marker)

    def num_holes(self) -> int:
        """
        Returns the number of holes in this template.

        Returns:
            Number of holes
        """
        if self._brain is None:
            return 0
        return self._brain.count(MARKER)

    def extract(self, text: str) -> Tuple[str, ...]:
        """
        Extract data from text that matches this template.

        Args:
            text: The text to extract data from

        Returns:
            A tuple of extracted values

        Raises:
            NoMatch: If the text doesn't match the template
        """
        if self._brain is None:
            raise NoMatch("Template has not learned any patterns yet")

        text = self.clean(text)
        pattern = re.escape(self._brain).replace(re.escape(MARKER), "(.*?)")
        m = re.search(f"(?s)^{pattern}$", text)
        if m:
            return m.groups()
        raise NoMatch

    def extract_dict(
        self, text: str, field_names: Tuple[Optional[str], ...]
    ) -> Dict[str, str]:
        """
        Extract data as a dictionary from text that matches this template.

        Args:
            text: The text to extract data from
            field_names: Names to use for each extracted field

        Returns:
            Dictionary of field names to extracted values

        Raises:
            NoMatch: If the text doesn't match the template
        """
        data = self.extract(text)
        data_dict = {
            name: value for name, value in zip(field_names, data) if name is not None
        }
        return data_dict

    @classmethod
    def from_directory(cls, dirname: str, tolerance: int = 0) -> "Template":
        """
        Create a template by learning from all files in a directory.

        Args:
            dirname: Path to the directory containing example files
            tolerance: Minimum allowed length of text between holes

        Returns:
            A new Template instance
        """
        t = cls(tolerance)
        for f in os.listdir(dirname):
            with open(os.path.join(dirname, f), "r") as file:
                print(t.learn(file.read()))
        return t


class HTMLTemplate(Template):
    """
    A special version of Template that is a bit smarter about dealing with HTML.
    Focuses on identifying differences in the content rather than markup/script.
    """

    def __init__(self, *args: Any, **kwargs: Any):
        """Initialize a new HTML template."""
        super().__init__(*args, **kwargs)
        self.unwanted_tags_re = re.compile(
            r"(?si)<\s*?(script|style|noscript)\b.*?</\1>"
        )

    def clean(self, text: str) -> str:
        """
        Strips out <script>, <style> and <noscript> tags and everything within them.

        Args:
            text: The HTML text to clean

        Returns:
            Cleaned HTML text
        """
        text = self.unwanted_tags_re.sub("", text)
        return super().clean(text)


__version__ = "0.1.0"


if __name__ == "__main__":
    # Simple usage example
    print(f"Templatemaker v{__version__}")

    # Create a template
    t = Template()
    t.learn("<b>this and that</b>")
    t.learn("<b>alex and sue</b>")

    # Display the template
    print(f"Template: {t.as_text('!')}")

    # Extract data
    data = t.extract("<b>larry and curly</b>")
    print(f"Extracted: {data}")
