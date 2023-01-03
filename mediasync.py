import argparse
from pathlib import Path
import json
import secrets
import string
from mediabrowser import CreateMediaServerfromSettings


def load_settings(path):
    with path.open("r") as file:
        settings = json.loads(file.read())
        if "source" not in settings or "destination" not in settings:
            raise ValueError(
                f"Both a source and desintation object must be defined in {path}"
            )
    return settings


def search(query, items):
    for item in items:
        if "Path" in item and query["Type"] == item["Type"]:
            if query["ProviderIds"].items() & item["ProviderIds"].items():
                return True
            if query["Path"] == item["Path"]:
                return True
    return False


def sync_user_acounts(src, dst, password=None):
    src_users = src.get_users()
    dst_users = dst.get_users()

    users = {}

    for user in src_users:
        if user not in dst_users:
            print(f"User `{user}` is not in destination. Creating...")
            if password is None:
                password = "".join(
                    (
                        secrets.choice(
                            string.ascii_letters + string.digits + string.punctuation
                        )
                        for i in range(32)
                    )
                )
            dst_users |= dst.create_user(user, password)

        users[user] = {"src": src_users[user], "dst": dst_users[user]}

    return users


def sync_items(src, dst, user_id, type):
    src_items = src.get_user_items(user_id["src"], type, played=True)
    dest_items = dst.get_user_items(user_id["dst"], type)
    migration = [
        item
        for item in dest_items
        if "Path" in item and not item["UserData"]["Played"] and search(item, src_items)
    ]
    dst.set_watched(user_id["dst"], migration)


def sync(options):
    settings = load_settings(options.settings)
    src = CreateMediaServerfromSettings(settings["source"])
    dst = CreateMediaServerfromSettings(settings["destination"])

    users = sync_user_acounts(src, dst, options.password)

    for user_id in users.values():
        sync_items(src, dst, user_id, "Movie,Episode")


def diff_run(src, dst, type):
    src_items = src.get_items(type)
    dest_items = dst.get_items(type)
    migration = [
        item for item in src_items if "Path" in item and not search(item, dest_items)
    ]
    if len(migration):
        print(
            f"The following {len(migration)} {type.casefold()}s from source are missing from destination"
        )
        for item in migration:
            print(f"ID: '{item['Id']}', '{item['Name']}', path: '{item['Path']}'")
    else:
        print(
            f"All {type.casefold()} in source were matched with movies in destination"
        )


def diff(options):
    settings = load_settings(options.settings)
    src = CreateMediaServerfromSettings(settings["source"])
    dst = CreateMediaServerfromSettings(settings["destination"])

    diff_run("Movie")
    diff_run("Episode")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("settings", type=Path, help="Path to the JSON settings file")

    subparsers = parser.add_subparsers()

    parser_diff = subparsers.add_parser(
        "diff", help="Report differences between both libraries and exit"
    )
    parser_diff.set_defaults(func=diff)

    parser_sync = subparsers.add_parser(
        "sync", help="Synchronize the watched status of source with the destination"
    )
    parser_sync.set_defaults(func=sync)
    parser_sync.add_argument(
        "-p",
        "--password",
        default=None,
        help="Set default user password used during account creation. Omit to use random password",
    )

    options = parser.parse_args()
    options.func(options)


if __name__ == "__main__":
    main()
