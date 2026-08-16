import tempfile
import unittest
from pathlib import Path

from shared.app import AppConstants


class TestAppConstants(unittest.TestCase):
    def test_user_config_is_preferred_over_program_config(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            user_folder = root / "user" / "l4d2ModManager-dev"
            program_folder = root / "program" / "l4d2ModManager-dev"
            self._create_config(user_folder)
            self._create_config(program_folder)

            selected = AppConstants._select_data_folder(user_folder, program_folder)

            self.assertEqual(selected, user_folder)

    def test_program_config_is_used_when_user_config_is_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            user_folder = root / "user" / "l4d2ModManager-dev"
            program_folder = root / "program" / "l4d2ModManager-dev"
            self._create_config(program_folder)

            selected = AppConstants._select_data_folder(user_folder, program_folder)

            self.assertEqual(selected, program_folder)

    def test_program_config_is_used_when_user_folder_has_no_config(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            user_folder = root / "user" / "l4d2ModManager-dev"
            program_folder = root / "program" / "l4d2ModManager-dev"
            user_folder.mkdir(parents=True)
            self._create_config(program_folder)

            selected = AppConstants._select_data_folder(user_folder, program_folder)

            self.assertEqual(selected, program_folder)

    def test_user_folder_is_default_when_no_config_exists(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            user_folder = root / "user" / "l4d2ModManager-dev"
            program_folder = root / "program" / "l4d2ModManager-dev"
            user_folder.mkdir(parents=True)
            program_folder.mkdir(parents=True)

            selected = AppConstants._select_data_folder(user_folder, program_folder)

            self.assertEqual(selected, user_folder)

    def test_debug_and_release_folder_names(self):
        self.assertEqual(
            AppConstants._data_folder_name(debug=True), "l4d2ModManager-dev"
        )
        self.assertEqual(AppConstants._data_folder_name(debug=False), "l4d2ModManager")

    @staticmethod
    def _create_config(data_folder):
        config_file = data_folder / "config" / "config.json"
        config_file.parent.mkdir(parents=True)
        config_file.write_text("{}", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
