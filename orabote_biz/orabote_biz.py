# -*- coding: utf-8 -*-
"""Main module."""
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
import re


class _Logger:
    def send_info(self, message):
        print('INFO: ' + message)

    def send_warning(self, message):
        print('WARNING: ' + message)

    def send_error(self, message):
        print('ERROR: ' + message)


class OraboteBiz:
    BASE_URL = 'https://orabote.biz'
    _count_reviews = 0
    reviews = []

    def __init__(self, company_id, logger=_Logger()):
        self.company_id = company_id
        self.logger = logger
        self.session = requests.Session()

    def start(self, page=1, max_page=None):
        self.request('GET', urljoin(self.BASE_URL,
                                    'feedback/list/company/{}/page/{}'
                                    .format(self.company_id, page)))
        self.reviews.extend(self._collect_reviews())
        page += 1
        self._count_reviews = self._convert_string_to_int(self.\
    soup.find('span', class_='sright', text=re.compile('Всего отзывов: \d+')).text)
        while not self._count_reviews <= len(self.reviews):
            if max_page and page >= max_page:
                break
            self.request('GET', urljoin(self.BASE_URL,
                                        'feedback/list/company/{}/page/{}'
                                        .format(self.company_id, page)))
            self.reviews.extend(self._collect_reviews())
            page += 1

    def _collect_reviews(self):
        """TODO:
         Собрать более подробную информация о отзыве с переходом на
          более подробную информации о отзыве:
           https://orabote.biz/feedback/show/id/1286292"""
        reviews_soup = self.soup.find_all('div', class_=['div.panel', 'panel-default'])[3:13]
        for review_soup in reviews_soup:
            if 'Отзыв был удален автором' in review_soup.text:
                continue
            try:
                yield self._collect_review(review_soup)
            except ValueError:
                """TODO: Некоторые отзывы не получается спарсить, например:
                https://orabote.biz/feedback/list/company/9094/page/3
                 отзыв с id 143222 """
                self._count_reviews -= 1
                continue

    def _collect_review(self, review_soup):
        new_review = Review()
        plus_comment, minus_comment = review_soup.select('div.col-md-6')
        plus_comment = plus_comment.text.rstrip().replace('\n', '').replace('\t', '').replace('\r', '')
        minus_comment = minus_comment.text.rstrip().replace('\n', '').replace('\t', '').replace('\r', '')
        new_review.plus_comment = plus_comment
        new_review.minus_comment = minus_comment
        new_review.id = self._convert_string_to_int(
            review_soup.find('a', itemprop='url')['href'])
        new_review.date = review_soup.find('meta', itemprop='datePublished').attrs['content']
        new_review.rating.average_rating = self._convert_string_to_int(review_soup.find('meta', itemprop='ratingValue')['content'])
        new_review.author.name = review_soup.find_all('meta', itemprop='name')[1].attrs['content']
        new_review.author.location = review_soup.select('div.panel.panel-default>div>span>i')[1].text
        return new_review

    @staticmethod
    def _convert_string_to_float(text):
        try:
            return float(text)
        except ValueError:
            return float(re.findall("\d+\.\d+", text)[0])

    @staticmethod
    def _convert_string_to_int(text):
        try:
            return int(text)
        except (ValueError, TypeError):
            return int(re.findall("\d+", text)[0])

    def request(self, method, url, **kwargs):
        self.logger.send_info(url)
        time.sleep(1)
        response = self.session.request(method, url, **kwargs)
        if not response.status_code == 200:
            self.logger.send_error(response.text)
            raise Exception("{}: {}".format(response.status_code,
                                            response.text))

        self.soup = BeautifulSoup(response.text, 'html.parser')
        return self.soup


class Author:

    def __init__(self):
        self.name = ''
        self.location = ''

    def get_name(self):
        return self.name

    def get_dict(self):
        return {
            'name': self.name,
            'location': self.location,
        }


class Rating:
    min_scale = 1
    max_scale = 5

    def __init__(self):
        self.average_rating = None

    def get_dict(self):
        return {
            'min_scale': self.min_scale,
            'max_scale': self.max_scale,
            'average_rating': self.average_rating,
        }


class Review:

    def __init__(self):
        self.id = None
        self.plus_comment = None
        self.minus_comment = None
        self.date = None
        self.rating = Rating()
        self.author = Author()
        self.sub_reviews = []

    def get_text(self):
        return 'Плюсы: {}\n Минусы: {}'.format(self.plus_comment,
                                               self.minus_comment)

    def get_dict(self):
        return {
            'id': self.id,
            'plus_comment': self.plus_comment,
            'minus_comment': self.minus_comment,
            'text': self.get_text(),
            'date': self.date,
            'rating': self.rating.get_dict(),
            'author': self.author.get_dict(),
        }


if __name__ == '__main__':
    prov = OraboteBiz(1169)
    prov.start()
    print(prov._count_reviews, len(prov.reviews))
    for r in prov.reviews:
        print(r.get_dict())
