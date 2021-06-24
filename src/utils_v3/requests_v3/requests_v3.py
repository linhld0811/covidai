#!/usr/bin/env python3

# Copyright 2020 (author: lamnt45)


# requests
import requests


# urllib
import urllib.parse


# logger
from ..logger import getLogger
logger = getLogger(__name__)



def parse_Requests_Response(Response:requests.Response, max_text_length=500):

    Response_Dict = {}

    try:
        Response_Dict['__JSON__'] = Response.json()
    except: pass

    try:
        if '__JSON__' not in Response_Dict:
            Response_Dict['__Text__'] = Response.text
            if len(Response_Dict['__Text__']) > max_text_length:
                Response_Dict['__Text__'] = Response_Dict['__Text__'][:max_text_length] + ' ... +{} MORE CHARACTERS'.format(
                    len(Response_Dict['__Text__']) - max_text_length
                )
    except: pass

    try:
        Response_Dict['__Status_Code__'] = Response.status_code
    except: pass

    return Response_Dict


def add_params_to_url(url, Added_Params_Dict):

    # stage 0
    url__Parts = list(urllib.parse.urlparse(url))

    # stage 1
    Params_Dict = dict(urllib.parse.parse_qsl(url__Parts[4]))
    Params_Dict.update(Added_Params_Dict)
    url__Parts[4] = urllib.parse.urlencode(Params_Dict)

    # stage 2
    new_url = urllib.parse.urlunparse(url__Parts)

    return new_url
