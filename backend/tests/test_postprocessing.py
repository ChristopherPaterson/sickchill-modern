"""Post-processing engine tests: parsing, file discovery, and file operations.

These exercise the risky filesystem logic with temp dirs and no database.
"""
from __future__ import annotations

from pathlib import Path

from app.postprocessing.namer import episode_path, sanitize
from app.postprocessing.processor import (
    _do_file_op,
    find_video_file,
    normalise,
    parse_release_name,
)


def test_normalise_matches_punctuation_variants():
    assert normalise("Bob's Burgers") == normalise("Bobs.Burgers")
    assert normalise("3 Body Problem") == "3bodyproblem"


def test_parse_release_name():
    title, season, episode = parse_release_name("Bobs.Burgers.S16E15.1080p.WEB-DL.x264")
    assert normalise(title) == "bobsburgers"
    assert season == 16
    assert episode == 15


def test_sanitize_removes_illegal_chars():
    assert sanitize('Show: The "Best"?/Worst') == "Show The BestWorst"


def test_episode_path_layout(tmp_path):
    p = episode_path(tmp_path, "Bob's Burgers", 16, 15, "Smellbound", ".mkv")
    assert p == tmp_path / "Bob's Burgers" / "Season 16" / "Bob's Burgers - S16E15 - Smellbound.mkv"


def test_find_video_file_picks_largest(tmp_path):
    (tmp_path / "sample.mkv").write_bytes(b"x" * 10)
    big = tmp_path / "episode.mkv"
    big.write_bytes(b"x" * 1000)
    (tmp_path / "readme.txt").write_bytes(b"x" * 5000)  # not a video
    assert find_video_file(tmp_path) == big


def test_do_file_op_move(tmp_path):
    src = tmp_path / "src.mkv"
    src.write_bytes(b"data")
    dest = tmp_path / "lib" / "Show" / "Season 01" / "Show - S01E01.mkv"
    _do_file_op(src, dest, "move")
    assert dest.exists()
    assert not src.exists()  # moved
    assert dest.read_bytes() == b"data"


def test_do_file_op_copy_keeps_source(tmp_path):
    src = tmp_path / "src.mkv"
    src.write_bytes(b"data")
    dest = tmp_path / "lib" / "out.mkv"
    _do_file_op(src, dest, "copy")
    assert dest.exists() and src.exists()  # copy leaves the source


def test_do_file_op_hardlink(tmp_path):
    src = tmp_path / "src.mkv"
    src.write_bytes(b"data")
    dest = tmp_path / "lib" / "out.mkv"
    _do_file_op(src, dest, "hardlink")
    assert dest.exists() and src.exists()
    assert Path(dest).read_bytes() == b"data"
