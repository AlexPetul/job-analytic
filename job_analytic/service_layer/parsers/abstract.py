import abc
from typing import List

from bs4 import BeautifulSoup


class BaseParser(abc.ABC):
    @property
    @abc.abstractmethod
    def base_url(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def get_interpolated_query_param(self, query: str) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def get_page_count(self, soup: BeautifulSoup) -> int:
        """Get max number of available pages"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_vacancies(self, soup: BeautifulSoup) -> List[str]:
        """Get list of links pointing to detailed vacancy description"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_skills(self, soup: BeautifulSoup) -> List[str]:
        """Get list of skills related to certain vacancy"""
        raise NotImplementedError
