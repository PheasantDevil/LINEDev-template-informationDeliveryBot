"""Information collection system"""

from .base import BaseInformationCollector, InformationItem
from .email_collector import EmailCollector
from .rss_reader import RSSReaderCollector

__all__ = ["BaseInformationCollector", "InformationItem", "EmailCollector", "RSSReaderCollector"]
