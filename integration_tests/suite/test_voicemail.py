# -*- coding: utf-8 -*-
# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import ari as ari_client
import logging
import os
import pytest
import time

from hamcrest import assert_that
from hamcrest import calling
from hamcrest import not_
from hamcrest import has_property
from requests.exceptions import HTTPError
from xivo_test_helpers import until
from xivo_test_helpers.asset_launching_test_case import AssetLaunchingTestCase
from xivo_test_helpers.hamcrest.raises import raises

log_level = logging.DEBUG if os.environ.get('TEST_LOGS') == 'verbose' else logging.INFO
logging.basicConfig(level=log_level)


class AssetLauncher(AssetLaunchingTestCase):

    assets_root = os.path.join(os.path.dirname(__file__), '..', 'assets')
    asset = 'base'
    service = 'asterisk'

greeting_args = {'context': 'default', 'voicemail': 6001, 'greeting': 'name'}

def _reset_test(ari):
    ari.wazo.removeVoicemailGreeting(**greeting_args)

@pytest.fixture()
def ari():
    AssetLauncher.kill_containers()
    AssetLauncher.rm_containers()
    AssetLauncher.launch_service_with_asset()
    ari_url = 'http://localhost:{port}'.format(port=AssetLauncher.service_port(5039, 'ari'))
    ari = until.return_(ari_client.connect, ari_url, 'wazo', 'wazo', timeout=5, interval=0.1)

    yield ari

    AssetLauncher.kill_containers()


def test_delete_voicemail_message_without_body(ari):
    assert_that(calling(ari.wazo.deleteVoicemailMessage).with_args(body={'wrong_key': 'wrong_value'}),
                raises(HTTPError).matching(has_property('response', has_property('status_code', 400))))


def test_move_voicemail_message_without_body(ari):
    assert_that(calling(ari.wazo.moveVoicemailMessage).with_args(body={'wrong_key': 'wrong_value'}),
                raises(HTTPError).matching(has_property('response', has_property('status_code', 400))))

def test_delete_voicemail_greeting(ari):
    assert_that(
        calling(ari.wazo.removeVoicemailGreeting).with_args(**greeting_args),
        not_(raises(Exception))
    )
    _reset_test(ari)

# def test_post_voicemail_greeting(ari):
#     with open('voicemail_data_base64') as file:
#         greeting_base64 = file.read()
#
#     assert_that(
#         calling(ari.wazo.createVoicemailGreeting).with_args(body={"greeting_base64": greeting_base64}, **greeting_args),
#         not_(raises(Exception))
#     )
#     _reset_test(ari)

def test_put_voicemail_greeting(ari):
    with open('voicemail_data_base64') as file:
        greeting_base64 = file.read()

    # ari.wazo.createVoicemailGreeting(body={"greeting_base64": greeting_base64}, **greeting_args)
    _reset_test(ari)
    assert_that(
        calling(ari.wazo.changeVoicemailGreeting).with_args(body={"greeting_base64": greeting_base64}, **greeting_args),
        not_(raises(Exception))
    )

    ari.wazo.getVoicemailGreeting(**greeting_args)
    # _reset_test(ari)
#
# def test_get_voicemail_greeting(ari):
#     with open('voicemail_data_base64') as file:
#         greeting_base64 = file.read()
#
#     ari.wazo.createVoicemailGreeting(body={"greeting_base64": greeting_base64}, **greeting_args)
#
#     try:
#         ari.wazo.getVoicemailGreeting(**greeting_args)
#     except Exception as e:
#         print e.original_error.response.text
#
#     assert_that(
#         calling(ari.wazo.getVoicemailGreeting).with_args(**greeting_args), not_(raises(Exception))
#     )
#     _reset_test(ari)
