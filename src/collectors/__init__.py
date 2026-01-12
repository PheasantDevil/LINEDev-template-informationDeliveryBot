"""情報収集システム"""

from .base import BaseInformationCollector, InformationItem
from .email_collector import EmailCollector

__all__ = ['BaseInformationCollector', 'InformationItem', 'EmailCollector']

