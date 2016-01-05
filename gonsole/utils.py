# coding: utf8

import requests

from .const import STANDARD_SPACE


def inflate_space(code, indent):
    return STANDARD_SPACE * indent + code


def post_to_playground(context):
    result = requests.post("https://play.golang.org/share", data=context)
    return "https://play.golang.org/p/" + result.text
