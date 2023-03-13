#!/usr/bin/env python3

import abc
import argparse
import typing

import requests


class ResourceChangedException(Exception):
    pass


class SearchRes(typing.NamedTuple):
    total_results: int
    movies: typing.List[typing.Dict[str, str]]


class TitleSearcher(abc.ABC):
    def __init__(self, title: str, api_key: str, media_type="movie") -> None:
        self.title = title
        self.api_key = api_key
        self.media_type = media_type
        self._session = requests.Session()

    def __del__(self):
        self._session.close()

    def _get_search(self, page: int = 1) -> SearchRes:
        res = self._session.get(
            "https://www.omdbapi.com",
            params={
                "apikey": self.api_key,
                "s": self.title,
                "page": page,
                "type": self.media_type,
            },
        )
        requests.Response
        res.raise_for_status()
        res_js = res.json()
        if res_js["Response"] != "True":
            raise KeyError(res_js["Error"])
        return SearchRes(
            total_results=int(res_js["totalResults"]), movies=res_js["Search"]
        )

    def search_iterator(self) -> typing.Generator[typing.Dict[str, str], None, None]:
        page = 1
        res = self._get_search(page)
        total_results = res.total_results
        got_results = len(res.movies)
        for movie in res.movies:
            yield movie
        while total_results > got_results:
            page += 1
            res = self._get_search(page)
            if total_results != res.total_results:
                raise ResourceChangedException(
                    "the total number of results changed while querying: "
                    f"{total_results} -> {res.total_results}"
                )
            got_results += len(res.movies)
            for movie in res.movies:
                yield movie

    def search_id(self) -> typing.List[str]:
        return [res["imdbID"] for res in self.search_iterator()]


def main():
    parser = argparse.ArgumentParser(
        description="A simple program to extract records from OMDb"
        "(The Open Movie Database)"
    )
    parser.add_argument("title", help="the title to search for")
    parser.add_argument("apikey", help="the api key for OMDb API")
    args = parser.parse_args()
    searcher = TitleSearcher(args.title, args.apikey)
    print(*searcher.search_id(), sep="\n")


if __name__ == "__main__":
    main()
