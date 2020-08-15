from functools import partial
from cachetools import cachedmethod, TTLCache
from cachetools.keys import typedkey
import json
import requests
from requests.auth import HTTPBasicAuth


def _aspireblock_cache_key(method, params={}, aspireblock=None):
    if aspireblock is None:
        aspireblock = ''
    return 'block' + aspireblock + method + json.dumps(params)


def _aspired_cache_key(method, params={}):
    return 'aspired' + method + json.dumps(params)


def _gasp_cache_key(method, params={}, timeout=4):
    return 'gasp' + method + json.dumps(params)


class Aspire:

    def __init__(self, app=None):
        self._aspireblock_url = 'http://aspireblock-testnet:14100/api/'
        self._aspireblock_auth = HTTPBasicAuth('rpc', 'rpc')
        self._gasp_host = 'gasp-testnet'
        self._gasp_port = 18332
        self._gasp_user = 'rpc'
        self._gasp_pass = 'rpc'
        self.cache = TTLCache(maxsize=1024, ttl=30)
        if app:
            self.init_app(app)

    def init_app(self, app):
        self._aspireblock_url = app.config.get('ASPIRE_BLOCK_URL', self._aspireblock_url)
        user = app.config.get('ASPIRE_BLOCK_USER', 'rpc')
        passw = app.config.get('ASPIRE_BLOCK_PASS', 'rpc')
        self._aspireblock_auth = HTTPBasicAuth(user, passw)
        self._gasp_host = app.config.get('ASPIRE_GAS_HOST', self._gasp_host)
        self._gasp_port = app.config.get('ASPIRE_GAS_PORT', self._gasp_port)
        self._gasp_user = app.config.get('ASPIRE_GAS_USER', self._gasp_user)
        self._gasp_pass = app.config.get('ASPIRE_GAS_PASS', self._gasp_pass)

    # @cachedmethod(lambda self: self.cache, key=_aspireblock_cache_key)
    def aspireblock(self, method, params={}, aspireblock=None):
        headers = {"content-type": "application/json"}
        payload = {
          "method": method,
          "params": params,
          "jsonrpc": "2.0",
          "id": 0
        }
        if aspireblock is None:
            aspireblock = self._aspireblock_url
        response = requests.post(aspireblock, data=json.dumps(payload), headers=headers, auth=self._aspireblock_auth)
        try:
            return response.json()
        except json.decoder.JSONDecodeError:
            raise Exception('Could node decode json from "' + str(response.content) + '"')

    # @cachedmethod(lambda self: self.cache, key=_aspired_cache_key)
    def aspired(self, method, params={}):
        return self.aspireblock('proxy_to_aspired', {'method': method, 'params': params})

    # @cachedmethod(lambda self: self.cache, key=_gasp_cache_key)
    def gasp(self, method, params={}, timeout=4):
        url = ''.join(['http://', self._gasp_user, ':', self._gasp_pass, '@', self._gasp_host, ':', str(self._gasp_port)])
        headers = {'content-type': 'application/json'}
        payload = {
            'jsonrpc': '2.0',
            'method': method
        }

        if params:
            if type(params) is tuple:
                lst = []
                for item in params[0]:
                    lst.append(item)
                payload.update({'params': lst})
            else:
                payload.update({'params': list(params)})

        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=timeout)
        try:
            json_resp = response.json()
        except json.decoder.JSONDecodeError:
            raise Exception('Could node decode json from "' + str(response.content) + '"')
        success = json_resp['error'] is None
        if not success:
            error = json_resp['error']
            return {"success": success, "error": error}
        return {"success": success, "data": json_resp['result']}
