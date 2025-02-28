#!/usr/bin/env python3

# Try to import pytest, fall back to unittest
try:
    import pytest

    PYTEST_AVAILABLE = True
except ImportError:
    import unittest

    PYTEST_AVAILABLE = False

from templatemaker import Template, NoMatch


# Helper functions
def create_template(tolerance, *inputs):
    """
    Helper function that returns a Template with the given tolerance and
    inputs.
    """
    t = Template(tolerance=tolerance)
    for i in inputs:
        t.learn(i)
    return t


def assert_created(tolerance, expected, *inputs):
    """
    Asserts that a Template with the given tolerance and inputs would be
    rendered as_text('!') to the expected string.
    """
    t = create_template(tolerance, *inputs)
    assert t.as_text("!") == expected


if PYTEST_AVAILABLE:
    # Test functions for template creation using pytest
    def test_noop():
        assert_created(0, "<title>123</title>", "<title>123</title>")
        assert_created(
            0, "<title>123</title>", "<title>123</title>", "<title>123</title>"
        )
        assert_created(
            0,
            "<title>123</title>",
            "<title>123</title>",
            "<title>123</title>",
            "<title>123</title>",
        )

    def test_one_char_start():
        assert_created(0, "!2345", "12345", "_2345")
        assert_created(0, "!2345", "12345", "12345", "_2345")
        assert_created(0, "!2345", "12345", "_2345", "^2345")

    def test_one_char_end():
        assert_created(0, "1234!", "12345", "1234_")
        assert_created(0, "1234!", "12345", "12345", "1234_")
        assert_created(0, "1234!", "12345", "1234_", "1234^")

    def test_one_char_middle():
        assert_created(0, "12!45", "12345", "12_45")
        assert_created(0, "12!45", "12345", "12345", "12_45")
        assert_created(0, "12!45", "12345", "12_45", "12^45")

    def test_multi_char_start():
        assert_created(0, "!345", "12345", "_2345", "1_345")
        assert_created(0, "!345", "12345", "1_345", "_2345")
        assert_created(0, "!45", "12345", "_2345", "1_345", "12_45")
        assert_created(0, "!5", "12345", "_2345", "1_345", "12_45", "123_5")

    def test_multi_char_end():
        assert_created(0, "1234!", "12345", "1234_")
        assert_created(0, "123!", "12345", "1234_", "123_5")
        assert_created(0, "12!", "12345", "1234_", "123_5", "12_45")
        assert_created(0, "1!", "12345", "1234_", "123_5", "12_45", "1_345")

    def test_empty():
        assert_created(0, "", "", "")

    def test_no_similarities():
        assert_created(0, "!", "a", "b")
        assert_created(0, "!", "ab", "ba", "ac", "bc")
        assert_created(0, "!", "abc", "ab_", "a_c", "_bc")

    def test_left_weight():
        assert_created(0, "!a!", "ab", "ba")  # NOT '!b!'
        assert_created(0, "a!b!", "abc", "acb")

    def test_multihole():
        assert_created(0, "!2!", "123", "_23", "12_")
        assert_created(0, "!2!4!", "12345", "_2_4_")
        assert_created(0, "!2!4!", "12345", "_2345", "12_45", "1234_")
        assert_created(0, "!2!456!8", "12345678", "_2_456_8")
        assert_created(0, "!2!456!8", "12345678", "_2345678", "12_45678", "123456_8")
        assert_created(0, "!e! there", "hello there", "goodbye there")

    def test_marker_char():
        """The marker character (\x1f) is deleted from all input."""
        assert_created(
            0, "<title>!</title>", "<title>\x1f1234</title>", "<title>5678\x1f</title>"
        )

    # Tests for creation with tolerance using pytest
    def test_tolerance():
        assert_created(
            1, "<title>!</title>", "<title>123</title>", "<title>a2c</title>"
        )
        assert_created(
            2, "<title>!</title>", "<title>123</title>", "<title>a2c</title>"
        )
        assert_created(
            0, "<title>!23!</title>", "<title>1234</title>", "<title>a23c</title>"
        )
        assert_created(
            1, "<title>!23!</title>", "<title>1234</title>", "<title>a23c</title>"
        )
        assert_created(
            2, "<title>!</title>", "<title>1234</title>", "<title>a23c</title>"
        )
        assert_created(
            3, "<title>!</title>", "<title>1234</title>", "<title>a23c</title>"
        )
        assert_created(
            0, "http://s!me!.com/", "http://suntimes.com/", "http://someing.com/"
        )
        assert_created(
            1, "http://s!me!.com/", "http://suntimes.com/", "http://someing.com/"
        )
        assert_created(
            2, "http://s!.com/", "http://suntimes.com/", "http://someing.com/"
        )
        assert_created(
            3, "http://s!.com/", "http://suntimes.com/", "http://someing.com/"
        )
        assert_created(
            4, "http://s!.com/", "http://suntimes.com/", "http://someing.com/"
        )

    # Tests for template extraction using pytest
    def test_basic_extraction():
        t = Template()
        t.learn("<b>this and that</b>")
        t.learn("<b>alex and sue</b>")
        assert t.extract("<b>larry and curly</b>") == ("larry", "curly")

    def test_dict_extraction():
        t = Template()
        t.learn("<b>this and that</b>")
        t.learn("<b>alex and sue</b>")
        assert t.extract_dict("<b>larry and curly</b>", ("first", "second")) == {
            "first": "larry",
            "second": "curly",
        }

    def test_none_field_name():
        t = Template()
        t.learn("<b>this and that</b>")
        t.learn("<b>alex and sue</b>")
        assert t.extract_dict("<b>larry and curly</b>", ("first", None)) == {
            "first": "larry"
        }

    def test_no_match():
        t = Template()
        t.learn("<b>this and that</b>")
        with pytest.raises(NoMatch):
            t.extract("this and that")

else:
    # Test functions for template creation using unittest
    class TestTemplateMaker(unittest.TestCase):
        def test_noop(self):
            assert_created(0, "<title>123</title>", "<title>123</title>")
            assert_created(
                0, "<title>123</title>", "<title>123</title>", "<title>123</title>"
            )
            assert_created(
                0,
                "<title>123</title>",
                "<title>123</title>",
                "<title>123</title>",
                "<title>123</title>",
            )

        def test_one_char_start(self):
            assert_created(0, "!2345", "12345", "_2345")
            assert_created(0, "!2345", "12345", "12345", "_2345")
            assert_created(0, "!2345", "12345", "_2345", "^2345")

        def test_one_char_end(self):
            assert_created(0, "1234!", "12345", "1234_")
            assert_created(0, "1234!", "12345", "12345", "1234_")
            assert_created(0, "1234!", "12345", "1234_", "1234^")

        def test_one_char_middle(self):
            assert_created(0, "12!45", "12345", "12_45")
            assert_created(0, "12!45", "12345", "12345", "12_45")
            assert_created(0, "12!45", "12345", "12_45", "12^45")

        def test_multi_char_start(self):
            assert_created(0, "!345", "12345", "_2345", "1_345")
            assert_created(0, "!345", "12345", "1_345", "_2345")
            assert_created(0, "!45", "12345", "_2345", "1_345", "12_45")
            assert_created(0, "!5", "12345", "_2345", "1_345", "12_45", "123_5")

        def test_multi_char_end(self):
            assert_created(0, "1234!", "12345", "1234_")
            assert_created(0, "123!", "12345", "1234_", "123_5")
            assert_created(0, "12!", "12345", "1234_", "123_5", "12_45")
            assert_created(0, "1!", "12345", "1234_", "123_5", "12_45", "1_345")

        def test_empty(self):
            assert_created(0, "", "", "")

        def test_no_similarities(self):
            assert_created(0, "!", "a", "b")
            assert_created(0, "!", "ab", "ba", "ac", "bc")
            assert_created(0, "!", "abc", "ab_", "a_c", "_bc")

        def test_left_weight(self):
            assert_created(0, "!a!", "ab", "ba")  # NOT '!b!'
            assert_created(0, "a!b!", "abc", "acb")

        def test_multihole(self):
            assert_created(0, "!2!", "123", "_23", "12_")
            assert_created(0, "!2!4!", "12345", "_2_4_")
            assert_created(0, "!2!4!", "12345", "_2345", "12_45", "1234_")
            assert_created(0, "!2!456!8", "12345678", "_2_456_8")
            assert_created(
                0, "!2!456!8", "12345678", "_2345678", "12_45678", "123456_8"
            )
            assert_created(0, "!e! there", "hello there", "goodbye there")

        def test_marker_char(self):
            """The marker character (\x1f) is deleted from all input."""
            assert_created(
                0,
                "<title>!</title>",
                "<title>\x1f1234</title>",
                "<title>5678\x1f</title>",
            )

    # Tests for creation with tolerance using unittest
    class TestToleranceCreation(unittest.TestCase):
        def test_tolerance(self):
            assert_created(
                1, "<title>!</title>", "<title>123</title>", "<title>a2c</title>"
            )
            assert_created(
                2, "<title>!</title>", "<title>123</title>", "<title>a2c</title>"
            )
            assert_created(
                0, "<title>!23!</title>", "<title>1234</title>", "<title>a23c</title>"
            )
            assert_created(
                1, "<title>!23!</title>", "<title>1234</title>", "<title>a23c</title>"
            )
            assert_created(
                2, "<title>!</title>", "<title>1234</title>", "<title>a23c</title>"
            )
            assert_created(
                3, "<title>!</title>", "<title>1234</title>", "<title>a23c</title>"
            )
            assert_created(
                0, "http://s!me!.com/", "http://suntimes.com/", "http://someing.com/"
            )
            assert_created(
                1, "http://s!me!.com/", "http://suntimes.com/", "http://someing.com/"
            )
            assert_created(
                2, "http://s!.com/", "http://suntimes.com/", "http://someing.com/"
            )
            assert_created(
                3, "http://s!.com/", "http://suntimes.com/", "http://someing.com/"
            )
            assert_created(
                4, "http://s!.com/", "http://suntimes.com/", "http://someing.com/"
            )

    # Tests for template extraction using unittest
    class TestTemplateExtraction(unittest.TestCase):
        def test_basic_extraction(self):
            t = Template()
            t.learn("<b>this and that</b>")
            t.learn("<b>alex and sue</b>")
            self.assertEqual(t.extract("<b>larry and curly</b>"), ("larry", "curly"))

        def test_dict_extraction(self):
            t = Template()
            t.learn("<b>this and that</b>")
            t.learn("<b>alex and sue</b>")
            self.assertEqual(
                t.extract_dict("<b>larry and curly</b>", ("first", "second")),
                {"first": "larry", "second": "curly"},
            )

        def test_none_field_name(self):
            t = Template()
            t.learn("<b>this and that</b>")
            t.learn("<b>alex and sue</b>")
            self.assertEqual(
                t.extract_dict("<b>larry and curly</b>", ("first", None)),
                {"first": "larry"},
            )

        def test_no_match(self):
            t = Template()
            t.learn("<b>this and that</b>")
            with self.assertRaises(NoMatch):
                t.extract("this and that")


if __name__ == "__main__":
    if PYTEST_AVAILABLE:
        pytest.main()
    else:
        unittest.main()
