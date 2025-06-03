import zlib
from http import client
from http.client import HTTPResponse


class Query:
    TIME_OUT = 120

    def __init__(self, api_url: str, request_uri: str, method: str, body: str):
        self.request_uri = request_uri
        self.api_url = api_url
        self.method = method
        self.body = body
        self.last_response: HTTPResponse
        self.last_data: str = ""
        self.count_retry = 3
        self.headers: {} = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Cache-Control": "no-cache",
        }

    def set_base_domain(self, api_url: str):
        self.api_url = api_url

    def set_request_uri(self, request_uri: str):
        self.request_uri = request_uri

    def query(self):
        conn = self._run_query()
        data = self.last_response.read()
        if self.last_response.getheader("content-encoding") == "gzip":
            data = zlib.decompress(data, 16 + zlib.MAX_WBITS)
        conn.close()
        self.last_data = data.decode("utf-8")
        return self.last_data

    def _run_query(self):
        conn = client.HTTPSConnection(self.api_url, port=443, timeout=Query.TIME_OUT)
        conn.request(self.method, self.request_uri, self.body, self.headers)
        self.last_response = conn.getresponse()
        return conn

    def query_headers(self):
        conn = self._run_query()
        headers = dict(self.last_response.getheaders())
        conn.close()
        return headers

    def set_headers(self, headers: {}):
        self.headers.update(headers)
