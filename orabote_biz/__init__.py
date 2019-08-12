# -*- coding: utf-8 -*-

"""Top-level package for orabote.biz."""
from .orabote_biz import OraboteBiz, Rating

__author__ = """NMelis"""
__email__ = 'melis.zhoroev+scrubbers@gmail.com'
__version__ = '0.1.4'
__title__ = 'OraboteBiz'
__slug_img_link__ = 'https://i.ibb.co/v44RKcD/image.png'
__how_get_slug__ = """
Slug это цифры в конце url'а конкретной компании
<img src="{}" alt="image" border="0">
""".format(__slug_img_link__)

provider = OraboteBiz
rating = Rating

