"""
MIT License

Copyright (c) 2022-present noaione

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Optional, Union
from uuid import uuid4

import aiohttp
import orjson

from .models import Chapter, ImageQuality, Manga

__all__ = ("MangaPlusAPI",)
__UA__ = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"  # noqa


class MangaPlusAPI:
    BASE_API = "https://jumpg-webapi.tokyo-cdn.com/api"
    BASE_URL = "https://mangaplus.shueisha.co.jp"

    def __init__(self, session: Optional[aiohttp.ClientSession] = None) -> None:
        self.__headers = {
            "User-Agent": __UA__,
            "Session-Token": str(uuid4()),
        }
        self.session = session or aiohttp.ClientSession(headers={"User-Agent": __UA__})

    async def get_manga(self, title_id: Union[int, str]):
        request_api = f"{self.BASE_API}/title_detail"
        params = {"title_id": str(title_id), "format": "json"}

        async with self.session.get(request_api, params=params, headers=self.__headers) as response:
            response.raise_for_status()
            resp_text = await response.text()
            resp_json = orjson.loads(resp_text)

        return Manga.from_api(resp_json)

    async def get_chapter(self, chapter_id: Union[int, str], quality: ImageQuality = ImageQuality.SuperHigh):
        request_api = f"{self.BASE_API}/manga_viewer"
        params = {
            "chapter_id": str(chapter_id),
            "split": "no",
            "img_quality": quality.value,
            "format": "json",
        }

        async with self.session.get(request_api, params=params, headers=self.__headers) as response:
            response.raise_for_status()
            resp_text = await response.text()
            resp_json = orjson.loads(resp_text)

        return Chapter.from_api(resp_json)

    async def get_image(self, image_url: str, encryption_key: str):
        async with self.session.get(image_url, headers=self.__headers) as response:
            response.raise_for_status()
            image_data = await response.read()

        image_array = bytearray(image_data)
        key = bytes.fromhex(encryption_key)
        a = len(key)
        for s in range(len(image_array)):
            image_array[s] ^= key[s % a]
        return bytes(image_array)
