import unittest
import responses
from mediabrowser import MediaBrowser, MediaBrowserAPIError


class TestMediaBrowser(unittest.TestCase):
    def setUp(self):
        responses.start()
        self.url = "https://example.com"
        self.headers = {"X-Emby-Token": "12345"}
        self.server = MediaBrowser("TestServer", self.url, self.headers)
        self.users = [{"Name": "User1", "Id": "1"}, {"Name": "User2", "Id": "2"}]
        self.items = {
            "Items": [
                {
                    "Id": "1",
                    "ProviderIds": {"Imdb": "tt0111161"},
                    "Path": "path/to/movie",
                }
            ]
        }

        responses.add(responses.GET, f"{self.url}/Users", json=self.users, status=200)
        responses.add(
            responses.GET,
            f"{self.url}/Items/abcdef/ExternalIdInfos",
            json=self.items,
            status=200,
        )
        responses.add(
            responses.GET, f"{self.url}/Users/123/Items", json=self.items, status=200
        )
        responses.add(responses.GET, f"{self.url}/Items", json=self.items, status=200)
        responses.add(
            responses.POST,
            f"{self.url}/Users/New",
            json={"Name": "testuser", "Id": "1"},
            status=200,
        )
        responses.add(
            responses.POST, f"{self.url}/Users/123/PlayedItems/abcdef", status=200
        )

    def tearDown(self):
        responses.stop()

    def test_get_users(self):
        users = self.server.get_users()
        self.assertIsInstance(users, dict)
        self.assertEqual(users, {"User1": "1", "User2": "2"})

    def test_get_item(self):
        item = self.server.get_item("abcdef")
        self.assertIsInstance(item, list)
        self.assertEqual(item, self.items)

    def test_get_user_items(self):
        items = self.server.get_user_items("123", "Movie")
        self.assertIsInstance(items, list)
        self.assertEqual(items, self.items["Items"])

    def test_get_items(self):
        items = self.server.get_items("Movie")
        self.assertIsInstance(items, list)
        self.assertEqual(items, self.items["Items"])

    def test_create_user(self):
        user = self.server.create_user("testuser", "password")
        self.assertIsInstance(user, dict)
        self.assertEqual(user, {"testuser": "1"})

    def test_api_error(self):
        responses.add(
            responses.GET,
            f"{self.url}/Users",
            json={"Error": "An error occurred"},
            status=500,
        )
        # with self.assertRaises(MediaBrowserAPIError):
        #     self.server.get_users()
