from pathlib import Path
from typing import List


class FileStorageService:
    def __init__(self, base_dir: str):
        """Initialize FileStorageService with a base directory."""
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_file(self, current_path: Path, target_filename: str) -> Path:
        """Move/Save a file to the base directory.
        
        Args:
            current_path: The current location of the file.
            target_filename: The name to save it as in the base directory.
        """
        target_path = self.base_dir / target_filename
        if target_path.exists():
            target_path.unlink()
        current_path.rename(target_path)
        return target_path

    def list_files(self) -> List[str]:
        """List all files in the base directory.

        Returns:
            List of filenames (strings).
        """
        return [f.name for f in self.base_dir.iterdir() if f.is_file()]

    def delete_file(self, filename: str) -> bool:
        """Delete a file from the base directory.

        Args:
            filename: Name of the file to delete.

        Returns:
            True if deleted, False if not found.
        """
        file_path = self.base_dir / filename
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
            return True
        return False
