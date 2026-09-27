from pathlib import Path

import pytest

import agent_lab.mcp_server as server


def test_safe_path_rejects_traversal(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(server, "ROOT", tmp_path.resolve())
    with pytest.raises(ValueError, match="超出"):
        server.safe_path("../secret.txt")


def test_file_round_trip_and_search(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(server, "ROOT", tmp_path.resolve())
    server.write_file("notes/a.txt", "Agent loop\n工具调用", False)
    assert "Agent loop" in server.read_file("notes/a.txt")
    results = server.search_content("工具", ".", 20)
    assert results[0]["path"] == "notes\\a.txt" or results[0]["path"] == "notes/a.txt"
