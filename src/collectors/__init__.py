"""情報収集システム"""

from .base import BaseInformationCollector, InformationItem
from .email_collector import EmailCollector
from .rss_reader import RSSReaderCollector

__all__ = ['BaseInformationCollector', 'InformationItem', 'EmailCollector']

