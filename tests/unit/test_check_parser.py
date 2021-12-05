from filecheck.filecheck import CheckParser, Config, MatchType, CheckType


def create_default_config(check_file):
    return Config(
        check_file=check_file,
        match_full_lines=False,
        strict_whitespace=False,
        check_prefix=None,
        implicit_check_not=None,
        dump_input=None,
    )


def test_01_most_basic():
    config = create_default_config("fake.filecheck")
    input_string = "CHECK: String 1"
    check = CheckParser.parse_check(input_string, 0, config)
    assert check.check_type == CheckType.CHECK
    assert check.match_type == MatchType.SUBSTRING
    assert check.check_keyword == "CHECK"
    assert check.expression == "String 1"
    assert check.source_line == input_string
    assert check.check_line_idx == 0
    assert check.start_index == 7


def test_02_two_check_words():
    config = create_default_config("fake.filecheck")
    input_string = "CHECK: CHECK: String 1"
    check = CheckParser.parse_check(input_string, 0, config)
    assert check.match_type == MatchType.SUBSTRING
    assert check.check_keyword == "CHECK"
    assert check.expression == "CHECK: String 1"
    assert check.source_line == input_string
    assert check.check_line_idx == 0
    assert check.start_index == 7


def test_10_regex_basic():
    config = create_default_config("fake.filecheck")
    input_string = "CHECK: {{String 1}}"
    check = CheckParser.parse_check(input_string, 0, config)
    assert check.match_type == MatchType.REGEX
    assert check.check_keyword == "CHECK"
    assert check.expression == "String 1"
    assert check.source_line == input_string
    assert check.check_line_idx == 0
    assert check.start_index == 7


def test_11_regex_two_check_words():
    config = create_default_config("fake.filecheck")
    input_string = "CHECK: CHECK: {{String 1}}"
    check = CheckParser.parse_check(input_string, 0, config)
    assert check.match_type == MatchType.REGEX
    assert check.check_keyword == "CHECK"
    assert check.source_line == input_string
    assert check.check_line_idx == 0
    assert check.start_index == 7

    # The behavior seems to be different across Python 3.6 - 3.9.
    assert (
        check.expression == r"CHECK\:\ String 1"
        or check.expression == r"CHECK:\ String 1"
    )


def test_90_check_two_times_no_offset():
    config = create_default_config("fake.filecheck")
    input_string = (
        "CHECK:{{^.*filecheck.check:1:(9|10): "
        "error: CHECK: expected string not found in input$}}"
    )
    check = CheckParser.parse_check(input_string, 0, config)
    assert check.match_type == MatchType.REGEX
    assert check.expression == (
        "^.*filecheck.check:1:(9|10): "
        "error: CHECK: expected string not found in input$"
    )
    assert check.check_keyword == "CHECK"
    assert check.source_line == input_string
    assert check.check_line_idx == 0
    assert check.start_index == 6


def test_91_check_two_times_with_offset():
    config = create_default_config("fake.filecheck")
    input_string = (
        "; CHECK:{{^.*filecheck.check:1:(9|10): "
        "error: CHECK: expected string not found in input$}}"
    )
    check = CheckParser.parse_check(input_string, 0, config)
    assert check.match_type == MatchType.REGEX
    assert check.expression == (
        "^.*filecheck.check:1:(9|10): "
        "error: CHECK: expected string not found in input$"
    )
    assert check.check_keyword == "CHECK"
    assert check.source_line == input_string
    assert check.check_line_idx == 0
    assert check.start_index == 8
