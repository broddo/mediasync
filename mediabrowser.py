import sessions
import requests


class APIError(Exception):
    def __init__(self, name, response, message):
        code = f"{name} responded with {response.status_code}. {response.content.decode('utf-8')}"
        super().__init__(f"{message}. {code}")


class MediaBrowser:
    def __init__(self, url, headers):
        self.s = sessions.BaseUrlSession(url, headers)

    def get_users(self):
        response = self.s.get("/Users")
        if response.status_code != 200:
            raise APIError(self.name, response, "Failed to retrieve user list")
        items = response.json()
        return {item["Name"]: item["Id"] for item in items}

    def get_item(self, id):
        response = self.s.get(f"/Items/{id}/ExternalIdInfos")
        if response.status_code != 200:
            raise APIError(self.name, response, f"Failed to retrieve item {id}")
        return response.json()

    def get_user_items(self, id, type, played=False):
        params = {
            "Filters": "IsPlayed" if played else "",
            "IncludeItemTypes": type,
            "Recursive": True,
            "Fields": "ProviderIds, Path",
        }
        response = self.s.get(f"/Users/{id}/Items", params=params)
        if response.status_code != 200:
            raise APIError(
                self.name, response, f"Failed to retrieve items for user id '{id}'"
            )
        return response.json()["Items"]

    def get_items(self, type):
        params = {
            "IncludeItemTypes": type,
            "Recursive": True,
            "Fields": "ProviderIds, Path",
        }
        response = self.s.get(f"/Items", params=params)
        if response.status_code != 200:
            raise APIError(self.name, response, f"Failed to retrieve items")
        return response.json()["Items"]

    def create_user(self, user, password):
        data = {"Name": user, "Password": password}
        response = self.s.post("/Users/New", json=data)
        if response.status_code != 200:
            raise APIError(self.name, response, f"Failed to create user '{user}'")
        item = response.json()
        return {item["Name"]: item["Id"]}

    def set_watched(self, user_id, items):
        for item in items:
            response = self.s.post(f"/Users/{user_id}/PlayedItems/{item['Id']}")
            if response.status_code != 200:
                raise APIError(
                    self.name,
                    response,
                    f"Failed to update watch status for item {item['Id']}, user '{user_id}'",
                )


class Emby(MediaBrowser):
    name = "Emby"

    def __init__(self, url, key):
        headers = {"X-Emby-Token": key}
        super().__init__(url, headers)


class Jellyfin(MediaBrowser):
    name = "Jellyfin"

    def __init__(self, url, key):
        headers = {"X-MediaBrowser-Token": key}
        super().__init__(url, headers)


def CreateMediaServer(type, url, key):
    servers = {"Emby": Emby, "Jellyfin": Jellyfin}

    try:
        return servers[type](url, key)
    except KeyError as k:
        raise SystemExit(
            f"Unknown server type {k}. Only Emby and Jellyfin are supported."
        )


def CreateMediaServerfromSettings(settings):
    return CreateMediaServer(settings["type"], settings["url"], settings["apikey"])
