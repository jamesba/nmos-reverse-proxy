#!/usr/bin/python

# Copyright 2017 British Broadcasting Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import mock
import os

class WebAPIStub(object):
    """This is used to replace the WebAPI class so that ProxyListingAPI can inherit from it"""
    def __init__(self):
        super(WebAPIStub, self).__setattr__('mock', mock.MagicMock(name='WebAPI'))

    def __getattr__(self, name):
        return getattr(self.mock, name)

    def __setattr__(self, name, value):
        return setattr(self.mock, name, value)

route = mock.MagicMock(name="route")
def _route(path):
    """This ensures that a unique mock is accessible for each call to resource_route"""
    m = getattr(route, path)
    m.side_effect = lambda f : f
    return m
route.side_effect = _route

_orig_getenv = os.getenv
def _getenv(*args, **kwargs):
    """This allows us to substitue known values for the environment variables used by the code."""
    if args[0] == "PROXYLISTING_ALIAS_SITES":
        return "/ALIAS_SITES/"
    elif args[0] == "PROXYLISTING_PROXY_SITES":
        return "/PROXY_SITES/"
    else:
        return _orig_getenv(*args, **kwargs)

with mock.patch('os.getenv', side_effect=_getenv) as getenv:
    with mock.patch('nmoscommon.webapi.WebAPI', WebAPIStub):
        with mock.patch('nmoscommon.webapi.route', route):
            from nmosreverseproxy.proxylisting import *

class TestProxyListingAPI(unittest.TestCase):
    def setUp(self):
        self.UUT = ProxyListingAPI()
        self.routes = {}
        for (name, args, kwargs) in route.mock_calls:
            if name != "":
                self.routes[name] = args[0]

    def test_init(self):
        """Just check that routes have been resgistered for the necessary paths."""
        self.assertIn('/', self.routes)
        self.assertIn('/x-ipstudio/', self.routes)
        self.assertIn('/x-nmos/', self.routes)
        self.assertIn(mock.call("PROXYLISTING_ALIAS_SITES", "/etc/apache2/sites-enabled/"), getenv.mock_calls)
        self.assertIn(mock.call("PROXYLISTING_PROXY_SITES", "/etc/apache2/sites-available/"), getenv.mock_calls)

    @mock.patch('__builtin__.open')
    @mock.patch('nmosreverseproxy.proxylisting.isfile')
    @mock.patch('nmosreverseproxy.proxylisting.listdir')
    def assert_route_call_behaves_as_expected(self, path, listdir, isfile, _open, alias_sites={}, proxy_sites={}, expected=None):
        """Test the resource registered for path '/' with the given files in the alias directory."""
        f = self.routes[path]

        def _listdir(dir):
            if dir == "/ALIAS_SITES/":
                return [ key for key in alias_sites ]
            else:
                return [ key for key in proxy_sites ]
        listdir.side_effect = _listdir
        isfile.side_effect = lambda key : (key[:13] == "/ALIAS_SITES/" and alias_sites[key[13:]] is not None) or (key[:13] == "/PROXY_SITES/" and proxy_sites[key[13:]] is not None)
        open.side_effect = lambda key : mock.MagicMock(__enter__=mock.MagicMock(return_value=alias_sites[key[13:]] if key[:13] == "/ALIAS_SITES/" else proxy_sites[key[13:]]))

        ret_list = f(self.UUT)
        self.assertListEqual(ret_list, expected)

    def test_base_with_no_alias_sites(self):
        """With no files in the alias directory only the default sites exist"""
        self.assert_route_call_behaves_as_expected('/', alias_sites={}, expected=['x-ipstudio/', 'x-nmos/'])

    def test_base_with_alias_sites(self):
        """Alias sites will add extra entries here, and that is all."""
        self.assert_route_call_behaves_as_expected('/', alias_sites={ "notafile" : None, "notaconffile" : [], "dummy.conf" : [ "Alias /dummy/path/1/",
                                                                                                                             "Alias /dimmy/path/2/"] },
                                                      expected=[ "dimmy/", "dummy/", 'x-ipstudio/', 'x-nmos/' ])

    def test_x_ipstudio_with_no_proxy_sites(self):
        """With no files in the proxy directory only no sites exist"""
        self.assert_route_call_behaves_as_expected('/x-ipstudio/', expected=[])

    def test_x_ipstudio_with_proxy_sites(self):
        """With no files in the proxy directory only no sites exist"""
        self.assert_route_call_behaves_as_expected('/x-ipstudio/',
                                                       proxy_sites={
                                                           "notafile" : None,
                                                           "notaconffile" : [ "<Location /BAD/UNPLEASANT/" ],
                                                           "dummy.conf" : [ "<Location /ANGRY/UNMUTUAL/" ],
                                                           "ips-api-dummy.conf" : [ "<Location /x-ipstudio/GOOD/",
                                                                                        "<Location /x-ipstudio/VGOOD/"],
                                                           "nmos-api-dummy.conf" : [ "<Location /x-nmos/NICE/",
                                                                                         "<Location /x-nmos/VNICE/"]
                                                           },
                                                       expected=[ 'GOOD/', "VGOOD/" ])

    def test_x_nmos_with_no_proxy_sites(self):
        """With no files in the proxy directory only no sites exist"""
        self.assert_route_call_behaves_as_expected('/x-nmos/', expected=[])

    def test_x_nmos_with_proxy_sites(self):
        """With no files in the proxy directory only no sites exist"""
        self.assert_route_call_behaves_as_expected('/x-nmos/',
                                                       proxy_sites={
                                                           "notafile" : None,
                                                           "notaconffile" : [ "<Location /BAD/UNPLEASANT/" ],
                                                           "dummy.conf" : [ "<Location /ANGRY/UNMUTUAL/" ],
                                                           "ips-api-dummy.conf" : [ "<Location /x-ipstudio/GOOD/",
                                                                                        "<Location /x-ipstudio/VGOOD/"],
                                                           "nmos-api-dummy.conf" : [ "<Location /x-nmos/NICE/",
                                                                                         "<Location /x-nmos/VNICE/"]
                                                           },
                                                       expected=[ 'NICE/', "VNICE/" ])
