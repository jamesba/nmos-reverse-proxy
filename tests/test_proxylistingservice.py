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
from signal import SIGINT

class ProxyListingService(unittest.TestCase):
    def setUp(self):
        from nmosreverseproxy.proxylistingservice import ProxyListingService
        self.UUT = ProxyListingService()

    def test_init(self):
        self.assertFalse(self.UUT.running)

    @mock.patch('nmosreverseproxy.proxylistingservice.HttpServer')
    @mock.patch('signal.signal')
    @mock.patch('time.sleep')
    def test_run(self, sleep, _signal, HttpServer):
        """The run method should just start up a webserver and then wait forever"""
        from nmosreverseproxy.proxylisting import ProxyListingAPI

        HttpServer.return_value.started.is_set.side_effect = [ False, False, True ]
        HttpServer.return_value.failed = None
        sleep.side_effect = lambda _ : self.UUT.stop()

        self.UUT.run()

        _signal.assert_called_once_with(SIGINT, mock.ANY)
        self.sighandle = _signal.call_args[0][1]
        HttpServer.assert_called_once_with(ProxyListingAPI, 12344, "127.0.0.1")
        HttpServer.return_value.start.assert_called_once_with()
        HttpServer.return_value.started.wait.mock_calls = [ mock.call() for _ in range(0,3) ]

    @mock.patch('nmosreverseproxy.proxylistingservice.HttpServer')
    @mock.patch('signal.signal')
    @mock.patch('time.sleep')
    def test_run_bails_when_http_server_fails_to_start(self, sleep, _signal, HttpServer):
        from nmosreverseproxy.proxylisting import ProxyListingAPI

        expected = Exception()

        HttpServer.return_value.started.is_set.side_effect = [ False, False, True ]
        HttpServer.return_value.failed = expected
        sleep.side_effect = lambda _ : self.UUT.stop()

        with self.assertRaises(Exception) as e:
            self.UUT.run()

        _signal.assert_called_once_with(SIGINT, mock.ANY)
        self.sighandle = _signal.call_args[0][1]
        HttpServer.assert_called_once_with(ProxyListingAPI, 12344, "127.0.0.1")
        HttpServer.return_value.start.assert_called_once_with()
        HttpServer.return_value.started.wait.mock_calls = [ mock.call() for _ in range(0,3) ]

        self.assertEqual(e.exception, expected)

    @mock.patch('nmosreverseproxy.proxylistingservice.HttpServer')
    @mock.patch('signal.signal')
    @mock.patch('time.sleep')
    def test_signal_handler_set_by_run_calls_stop(self, sleep, _signal, HttpServer):
        """The run method should just start up a webserver and then wait forever"""
        from nmosreverseproxy.proxylisting import ProxyListingAPI

        HttpServer.return_value.started.is_set.side_effect = [ False, False, True ]
        HttpServer.return_value.failed = None
        sleep.side_effect = lambda _ : self.UUT.stop()

        self.UUT.run()

        sighandle = _signal.call_args[0][1]

        with mock.patch.object(self.UUT, 'stop') as _stop:
            sighandle(mock.sentinel.sig, mock.sentinel.frame)
            _stop.assert_called_once_with()
