import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend-api"))

from core_services.FileStorageService import FileStorageService


class TestFileStorageService:
    def test_instantiation(self, tmp_path):
        service = FileStorageService(str(tmp_path))
        assert service is not None
        assert isinstance(service, FileStorageService)
        assert service.base_dir == tmp_path

    def test_instantiation_creates_directory(self, tmp_path):
        new_dir = tmp_path / "sub" / "deep"
        service = FileStorageService(str(new_dir))
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_instantiation_existing_directory(self, tmp_path):
        existing = tmp_path / "existing"
        existing.mkdir()
        service = FileStorageService(str(existing))
        assert service.base_dir == existing

    def test_list_files_empty(self, tmp_path):
        service = FileStorageService(str(tmp_path))
        files = service.list_files()
        assert files == []
        assert isinstance(files, list)

    def test_list_files_with_files(self, tmp_path):
        service = FileStorageService(str(tmp_path))
        # Create some files in the base directory
        (tmp_path / "file1.mp4").write_text("data1")
        (tmp_path / "file2.mp3").write_text("data2")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file3.mp4").write_text("data3")  # should not appear

        files = service.list_files()
        assert sorted(files) == ["file1.mp4", "file2.mp3"]

    def test_list_files_ignores_subdirectories(self, tmp_path):
        service = FileStorageService(str(tmp_path))
        (tmp_path / "a_dir").mkdir()
        (tmp_path / "a_file.txt").write_text("test")

        files = service.list_files()
        assert files == ["a_file.txt"]

    def test_save_file(self, tmp_path):
        service = FileStorageService(str(tmp_path))
        # Create a source file outside the base dir
        src = tmp_path / "outside" / "source.mp4"
        src.parent.mkdir()
        src.write_text("video content")

        result = service.save_file(src, "renamed.mp4")
        target = tmp_path / "renamed.mp4"

        assert result == target
        assert target.exists()
        assert target.read_text() == "video content"
        assert not src.exists()  # original moved

    def test_save_file_with_different_extension(self, tmp_path):
        service = FileStorageService(str(tmp_path))
        src = tmp_path / "outside" / "original.mkv"
        src.parent.mkdir()
        src.write_text("mkv data")

        result = service.save_file(src, "converted.mp4")

        assert result.name == "converted.mp4"
        assert (tmp_path / "converted.mp4").exists()

    def test_delete_file_success(self, tmp_path):
        service = FileStorageService(str(tmp_path))
        (tmp_path / "todelete.mp4").write_text("content")

        result = service.delete_file("todelete.mp4")

        assert result is True
        assert not (tmp_path / "todelete.mp4").exists()

    def test_delete_file_not_found(self, tmp_path):
        service = FileStorageService(str(tmp_path))

        result = service.delete_file("nonexistent.mp4")

        assert result is False

    def test_delete_file_directory_not_deleted(self, tmp_path):
        """delete_file should not delete directories."""
        service = FileStorageService(str(tmp_path))
        (tmp_path / "mydir").mkdir()

        result = service.delete_file("mydir")

        assert result is False
        assert (tmp_path / "mydir").exists()

    def test_delete_file_then_list(self, tmp_path):
        service = FileStorageService(str(tmp_path))
        f = tmp_path / "a.mp4"
        f.write_text("x")
        assert "a.mp4" in service.list_files()

        service.delete_file("a.mp4")
        assert service.list_files() == []

    def test_save_and_list(self, tmp_path):
        service = FileStorageService(str(tmp_path))
        src = tmp_path / "outside" / "src.txt"
        src.parent.mkdir()
        src.write_text("hello")

        service.save_file(src, "saved.txt")
        assert service.list_files() == ["saved.txt"]

    def test_save_overwrites_existing(self, tmp_path):
        service = FileStorageService(str(tmp_path))
        existing = tmp_path / "target.txt"
        existing.write_text("old")

        src = tmp_path / "outside" / "src.txt"
        src.parent.mkdir()
        src.write_text("new")

        service.save_file(src, "target.txt")
        assert existing.read_text() == "new"
