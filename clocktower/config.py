from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Type

from ruamel.yaml import YAML

from .mp import ImageQuality

__all__ = (
    "parse_config",
    "Config",
    "ConfigKomga",
    "ConfigManga",
)


@dataclass
class ConfigManga:
    id: int
    title: Optional[str] = None
    download_dir: Optional[str] = None
    quality: ImageQuality = ImageQuality.SuperHigh

    # Komga related
    komga_id: Optional[str] = None

    @classmethod
    def from_yaml(cls: Type["ConfigManga"], yaml_data: dict) -> "ConfigManga":
        img_quality = yaml_data.get("quality", "super_high").lower()
        if img_quality not in ["low", "high", "super_high"]:
            raise ValueError(f"Invalid quality: {img_quality}")
        return cls(
            id=yaml_data["id"],
            title=yaml_data.get("title"),
            download_dir=yaml_data.get("downloadDir"),
            quality=ImageQuality(img_quality),
            komga_id=yaml_data.get("komgaId"),
        )


@dataclass
class ConfigKomga:
    username: str
    password: str
    base_url: str

    @classmethod
    def from_yaml(cls: Type["ConfigKomga"], yaml_data: dict) -> "ConfigKomga":
        return cls(
            username=yaml_data["username"],
            password=yaml_data["password"],
            base_url=yaml_data["baseUrl"],
        )


@dataclass
class Config:
    manga_list: List[ConfigManga] = field(default_factory=list)
    komga: Optional[ConfigKomga] = None

    @classmethod
    def from_yaml(cls: Type["Config"], yaml_data: dict) -> "Config":
        manga_list = yaml_data.get("manga", [])
        manga_list = [ConfigManga.from_yaml(manga) for manga in manga_list]
        komga = yaml_data.get("komga")
        if komga:
            komga = ConfigKomga.from_yaml(komga)
        return cls(
            manga_list=manga_list,
            komga=komga,
        )


def parse_config(config_path: Path):
    yaml = YAML(typ="safe")
    yaml_data = yaml.load(config_path.read_text())
    return Config.from_yaml(yaml_data)
