from fake_useragent import UserAgent
import httpx
import tenacity


class Driver:
    _ua: UserAgent = UserAgent(platforms=["pc"])


class HttpDriver(Driver):
    def __init__(
        self,
        headers: dict[str, str],
    ) -> None:
        self._headers: dict[str, str] = headers | {"User-Agent": self._ua.random}

    @tenacity.retry(
        reraise=True,
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_fixed(2),
        retry=tenacity.retry_if_exception_type(httpx.ReadTimeout)
        | tenacity.retry_if_exception_type(httpx.ConnectError),
    )
    def make_request(
        self,
        url: str,
        method: str = "GET",
        headers: dict | None = None,
        params: dict | None = None,
        body: dict | None = None,
    ) -> httpx.Response | None:
        if headers is None:
            headers = self._headers

        if method == "GET":
            return self._make_get_request(url, headers, params)
        elif method == "POST":
            return self._make_post_request(url, headers, params, body)
        else:
            raise NotImplementedError

    def _make_post_request(
        self,
        url: str,
        headers: dict,
        params: dict | None = None,
        body: dict | None = None,
    ) -> httpx.Response | None:
        with httpx.Client() as client:  # type: ignore
            try:
                resp = client.post(
                    url=url, headers=headers, params=params, data=body, timeout=15
                )
            except httpx.ReadError as err:
                print(err)
                return
            if resp.status_code in {
                httpx.codes.BAD_REQUEST,
                httpx.codes.NOT_FOUND,
                httpx.codes.BAD_GATEWAY,
            }:
                print(f"Response with {resp.status_code} in {resp.url}")
                return None
            if resp.status_code != httpx.codes.OK:
                raise ConnectionError(f"Response with {resp.status_code} in {resp.url}")
            return resp

    def _make_get_request(
        self,
        url: str,
        headers: dict,
        params: dict | None = None,
    ) -> httpx.Response | None:
        with httpx.Client() as client:  # type: ignore
            try:
                resp = client.get(
                    url=url,
                    headers=headers,
                    params=params,
                    timeout=15,
                    follow_redirects=True,
                )
            except httpx.ReadError as err:
                print(err)
                return
            if resp.status_code in {
                httpx.codes.BAD_REQUEST,
                httpx.codes.NOT_FOUND,
                httpx.codes.BAD_GATEWAY,
            }:
                return None
            if resp.status_code != httpx.codes.OK:
                raise ConnectionError(f"Response with {resp.status_code} in {resp.url}")
            return resp
