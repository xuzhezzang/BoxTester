"""Utilities for transferring files between the local machine and Box.

This module exposes a small command line interface that can upload local
files/directories to a Box folder or download Box files/directories to a
local destination.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Optional

from boxsdk import Client, OAuth2
from boxsdk.exception import BoxAPIException


def _build_client(token: Optional[str]) -> Client:
    if not token:
        raise ValueError(
            "A Box developer token is required. Provide it via --token or "
            "the BOX_DEVELOPER_TOKEN environment variable."
        )
    oauth = OAuth2(client_id=None, client_secret=None, access_token=token)
    return Client(oauth)


def _upload_file(client: Client, file_path: Path, folder_id: str) -> None:
    folder = client.folder(folder_id)
    existing = None
    for item in folder.get_items(limit=1000):
        if item.type == "file" and item.name == file_path.name:
            existing = item
            break
    with file_path.open("rb") as file_stream:
        if existing:
            client.file(existing.id).update_contents(file_stream)
        else:
            folder.upload_stream(file_stream, file_path.name)


def _ensure_subfolder(client: Client, parent_id: str, name: str) -> str:
    folder = client.folder(parent_id)
    for item in folder.get_items(limit=1000):
        if item.type == "folder" and item.name == name:
            return item.id
    try:
        created = folder.create_subfolder(name)
    except BoxAPIException as exc:
        if exc.status == 409 and exc.context_info:
            conflicts = exc.context_info.get("conflicts")
            if conflicts:
                return conflicts[0]["id"]
        raise
    return created.id


def _upload_directory(client: Client, directory: Path, parent_folder_id: str) -> None:
    current_folder_id = _ensure_subfolder(client, parent_folder_id, directory.name)
    for child in directory.iterdir():
        if child.is_file():
            _upload_file(client, child, current_folder_id)
        elif child.is_dir():
            _upload_directory(client, child, current_folder_id)


def upload(local_path: Path, folder_id: str, token: Optional[str]) -> None:
    client = _build_client(token)
    path = local_path.expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")
    if path.is_file():
        _upload_file(client, path, folder_id)
    else:
        _upload_directory(client, path, folder_id)


def _download_file(client: Client, file_id: str, destination: Path) -> Path:
    box_file = client.file(file_id).get()
    destination.mkdir(parents=True, exist_ok=True)
    output_path = destination / box_file.name
    with output_path.open("wb") as output_stream:
        client.file(file_id).download_to(output_stream)
    return output_path


def _download_folder(client: Client, folder_id: str, destination: Path) -> None:
    folder = client.folder(folder_id).get()
    target_dir = destination / folder.name
    target_dir.mkdir(parents=True, exist_ok=True)
    for item in client.folder(folder_id).get_items(limit=1000):
        if item.type == "file":
            _download_file(client, item.id, target_dir)
        elif item.type == "folder":
            _download_folder(client, item.id, target_dir)


def download(item_id: str, item_type: str, destination: Path, token: Optional[str]) -> None:
    client = _build_client(token)
    destination = destination.expanduser().resolve()
    if item_type == "file":
        _download_file(client, item_id, destination)
    elif item_type == "folder":
        _download_folder(client, item_id, destination)
    else:
        raise ValueError("item_type must be either 'file' or 'folder'")


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload/download files with Box")
    parser.add_argument(
        "--token",
        default=os.getenv("BOX_DEVELOPER_TOKEN"),
        help="Box developer token. Defaults to BOX_DEVELOPER_TOKEN env var.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    upload_parser = subparsers.add_parser("upload", help="Upload a file or directory")
    upload_parser.add_argument("local_path", type=Path)
    upload_parser.add_argument("folder_id", help="Box folder ID to upload into")

    download_parser = subparsers.add_parser("download", help="Download a file or folder")
    download_parser.add_argument("item_id", help="Box file or folder ID")
    download_parser.add_argument(
        "item_type",
        choices=["file", "folder"],
        help="Specify whether the ID refers to a file or folder",
    )
    download_parser.add_argument(
        "destination",
        type=Path,
        help="Local directory where the item will be downloaded",
    )

    args = parser.parse_args()
    if args.command == "upload":
        upload(args.local_path, args.folder_id, args.token)
    elif args.command == "download":
        download(args.item_id, args.item_type, args.destination, args.token)


if __name__ == "__main__":
    main()
