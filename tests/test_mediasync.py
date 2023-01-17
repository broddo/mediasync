import unittest
import json
from pathlib import Path
from unittest.mock import MagicMock
from mediasync import *


class TestSyncScript(unittest.TestCase):
    def test_load_settings(self):
        # Test loading valid settings
        with open("settings.json", "w") as file:
            json.dump({"source": {}, "destination": {}}, file)

        settings = load_settings(Path("settings.json"))
        self.assertIsInstance(settings, dict)
        self.assertIn("source", settings)
        self.assertIn("destination", settings)

        # Test loading invalid settings
        with open("settings.json", "w") as file:
            json.dump({}, file)

        with self.assertRaises(ValueError):
            load_settings(Path("settings.json"))

    def test_search(self):
        # Test finding item in list
        items = [
            {
                "Type": "Movie",
                "ProviderIds": {"IMDB": "tt1234567"},
                "Path": "/path/to/movie.mkv",
            }
        ]
        query = {
            "Type": "Movie",
            "ProviderIds": {"IMDB": "tt1234567"},
            "Path": "/path/to/movie.mkv",
        }
        assert search(query, items) == True

        # Test not finding item in list
        items = [
            {
                "Type": "Movie",
                "ProviderIds": {"IMDB": "tt1234567"},
                "Path": "/path/to/movie.mkv",
            }
        ]
        query = {
            "Type": "Movie",
            "ProviderIds": {"IMDB": "tt7654321"},
            "Path": "/path/to/movie.mkv",
        }
        assert search(query, items) == False

    def test_sync_user_accounts(self):
        # Test syncing users
        src = MagicMock()
        src.get_users.return_value = {"user1": {"id": 1}, "user2": {"id": 2}}
        dst = MagicMock()
        dst.get_users.return_value = {"user1": {"id": 1}}

        password = "password"
        users = sync_user_acounts(src, dst, password)
        self.assertEqual(
            users,
            {
                "user1": {"src": {"id": 1}, "dst": {"id": 1}},
                "user2": {"src": {"id": 2}, "dst": {"id": 3}},
            },
        )
        dst.create_user.assert_called_with("user2", password)

    def test_sync_items(self):
        # Test syncing items
        src = MagicMock()
        src.get_user_items.return_value = [
            {"Type": "Movie", "Path": "/path/to/movie.mkv"}
        ]
        dst = MagicMock()
        dst.get_user_items.return_value = [
            {
                "Type": "Movie",
                "Path": "/path/to/movie.mkv",
                "UserData": {"Played": False},
            }
        ]

        user_id = {"src": 1, "dst": 2}
        sync_items(src, dst, user_id, "Movie,Episode")
        dst.set_watched.assert_called_with(
            2,
            [
                {
                    "Type": "Movie",
                    "Path": "/path/to/movie.mkv",
                    "UserData": {"Played": False},
                }
            ],
        )

    def test_diff(self):
        # Test finding differences
        src = Magic
