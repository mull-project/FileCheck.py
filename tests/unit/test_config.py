from filecheck.filecheck import Config

FAKE_CHECK_PATH = "filecheck.check"


def test_01_default_configuration():
    parser = Config.create_parser()
    args = parser.parse_args([FAKE_CHECK_PATH])

    assert len(args._get_kwargs()) == 6

    assert args.check_file_arg == FAKE_CHECK_PATH
    assert args.strict_whitespace is False
    assert args.match_full_lines is False
    assert args.check_prefix is None
    assert args.implicit_check_not is None
    assert args.dump_input is None

    config = Config.create(args)
    assert config.check_file == FAKE_CHECK_PATH
    assert config.match_full_lines is False
    assert config.strict_whitespace is False
    assert config.check_prefix == "CHECK"
    assert config.implicit_check_not is None
    assert config.dump_input is None
    assert config.strict_mode is False
