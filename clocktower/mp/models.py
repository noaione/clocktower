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

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Type

__all__ = (
    "Chapter",
    "Manga",
    "ImageQuality",
)


@dataclass
class MangaTitle:
    title_id: int
    name: str
    author: str
    portrait_image_url: Optional[str] = None
    landscape_image_url: Optional[str] = None
    view_count: Optional[int] = None

    @classmethod
    def from_api(cls: Type["MangaTitle"], api_response: dict) -> "MangaTitle":
        return cls(
            title_id=api_response["titleId"],
            name=api_response["name"],
            author=api_response["author"],
            portrait_image_url=api_response.get("portraitImageUrl"),
            landscape_image_url=api_response.get("landscapeImageUrl"),
            view_count=api_response.get("viewCount"),
        )


@dataclass
class MangaChapterList:
    title_id: int
    chapter_id: int
    name: str
    start_time_stamp: int
    sub_title: Optional[str] = None
    thumbnail_url: Optional[str] = None
    end_time_stamp: Optional[int] = None
    already_viewed: bool = False

    @classmethod
    def from_api(cls: Type["MangaChapterList"], api_response: dict) -> "MangaChapterList":
        return cls(
            title_id=api_response["titleId"],
            chapter_id=api_response["chapterId"],
            name=api_response["name"],
            start_time_stamp=api_response["startTimeStamp"],
            sub_title=api_response.get("subTitle"),
            thumbnail_url=api_response.get("thumbnailUrl"),
            end_time_stamp=api_response.get("endTimeStamp"),
            already_viewed=api_response.get("alreadyViewed", False),
        )


@dataclass
class Manga:
    title: MangaTitle
    title_image_url: str
    overview: str
    background_image_url: str
    first_chapter_list: List[MangaChapterList]
    last_chapter_list: List[MangaChapterList] = field(default_factory=list)
    next_time_stamp: Optional[int] = None
    viewing_period_description: Optional[str] = None

    @classmethod
    def from_api(cls: Type["Manga"], api_response: dict) -> "Manga":
        success = api_response.get("success", {})
        if not success:
            raise Exception("Invalid manga json")

        title_view = success.get("titleDetailView")
        if not title_view:
            raise Exception("Invalid manga json")

        first_chapters = list(map(MangaChapterList.from_api, title_view["firstChapterList"]))
        last_chapters: List[MangaChapterList] = []
        if "lastChapterList" in title_view:
            last_chapters = list(map(MangaChapterList.from_api, title_view["lastChapterList"]))
        return cls(
            title=MangaTitle.from_api(title_view["title"]),
            title_image_url=title_view["titleImageUrl"],
            overview=title_view["overview"],
            background_image_url=title_view["backgroundImageUrl"],
            first_chapter_list=first_chapters,
            last_chapter_list=last_chapters,
            next_time_stamp=title_view.get("nextTimeStamp"),
            viewing_period_description=title_view.get("viewingPeriodDescription"),
        )


@dataclass
class ChapterPage:
    image_url: str
    width: int
    height: int
    encryption_key: str

    @classmethod
    def from_api(cls: "ChapterPage", api_response: dict) -> "ChapterPage":
        if "mangaPage" in api_response:
            api_response = api_response["mangaPage"]

        image_url = api_response["imageUrl"]
        width = api_response["width"]
        height = api_response["height"]
        encryption_key = api_response["encryptionKey"]
        return cls(
            image_url=image_url,
            width=width,
            height=height,
            encryption_key=encryption_key,
        )


@dataclass
class Chapter:
    chapter_id: int
    title_id: int
    chapters: List[MangaChapterList]
    title_name: str
    chapter_name: str
    pages: List[ChapterPage]
    number_of_comments: int = 0
    region_code: Optional[str] = None

    @classmethod
    def from_api(cls: Type["Chapter"], api_response: dict) -> "Chapter":
        success = api_response.get("success", {})
        if not success:
            raise Exception("Invalid chapter json")

        manga_viewer = success.get("mangaViewer")
        if not manga_viewer:
            raise Exception("Invalid chapter json")

        chapter_id = manga_viewer["chapterId"]
        chapters = manga_viewer["chapters"]
        title_name = manga_viewer["titleName"]
        chapter_name = manga_viewer["chapterName"]
        parsed_pages: List[ChapterPage] = list(
            map(ChapterPage.from_api, filter(lambda x: "mangaPage" in x, manga_viewer["pages"]))
        )
        number_of_comments = manga_viewer.get("numberOfComments", 0)
        region_code = manga_viewer.get("regionCode")
        return cls(
            chapter_id=chapter_id,
            title_id=manga_viewer["titleId"],
            chapters=chapters,
            title_name=title_name,
            chapter_name=chapter_name,
            pages=parsed_pages,
            number_of_comments=number_of_comments,
            region_code=region_code,
        )


class ImageQuality(Enum):
    Low = "log"
    High = "high"
    SuperHigh = "super_high"
