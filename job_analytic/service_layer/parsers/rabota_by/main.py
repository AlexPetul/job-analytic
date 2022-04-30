from typing import List

from bs4 import BeautifulSoup
from job_analytic.service_layer.parsers.abstract import BaseParser


class RabotaByParser(BaseParser):

    @property
    def base_url(self) -> str:
        return "https://rabota.by/search/vacancy?clusters=true&area=1002&enable_snippets=true"

    def get_interpolated_query_param(self, query: str) -> str:
        return "&text={}".format(query)

    def get_page_count(self, soup: BeautifulSoup) -> int:
        try:
            return int(soup.findAll("a", {"data-qa": "pager-page"})[-1].get_text())
        except IndexError:
            return 1

    def get_skills(self, soup: BeautifulSoup) -> List[str]:
        return list(map(
            lambda tag: tag.get_text(),
            soup.findAll("span", {"data-qa": "bloko-tag__text"})
        ))

    def get_vacancies(self, soup: BeautifulSoup) -> List[str]:
        return list(map(
            lambda tag: tag.get("href"),
            soup.findAll("a", {"data-qa": "vacancy-serp__vacancy-title"}))
        )
