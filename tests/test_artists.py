import pytest

from ytmusic_discography.artists import parse_line


def test_skips_blank_and_comments():
    assert parse_line("", 1) is None
    assert parse_line("   # note", 1) is None


def test_multiple_urls_deduplicated():
    e = parse_line(
        "12ος Πίθηκος — https://music.youtube.com/channel/UCfq90uTcoqOPKPk_BhPwpBw "
        "https://www.youtube.com/channel/UC8J0vy5x7scOm6itUxWH8gg "
        "https://www.youtube.com/channel/UCfq90uTcoqOPKPk_BhPwpBw", 3)
    assert e.name == "12ος Πίθηκος"
    assert e.channel_ids == ("UCfq90uTcoqOPKPk_BhPwpBw", "UC8J0vy5x7scOm6itUxWH8gg")
    assert e.line_no == 3


def test_user_and_handle_urls_give_no_ids():
    assert parse_line("Πέγκυ Ζήνα — https://www.youtube.com/user/PeggyZinaVEVO", 1).channel_ids == ()
    assert parse_line("Νίκος Παπάζογλου — https://www.youtube.com/@NikosPapazoglouOfficial", 1).channel_ids == ()


def test_none_url():
    assert parse_line("Κάποιος — (none)", 1).channel_ids == ()


def test_missing_separator_raises():
    with pytest.raises(ValueError):
        parse_line("No dash here https://www.youtube.com/channel/UCfq90uTcoqOPKPk_BhPwpBw", 1)
