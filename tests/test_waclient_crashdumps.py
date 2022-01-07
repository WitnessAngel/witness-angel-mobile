import sys

import pytest
import responses
from requests import ConnectionError

from wacomponents.logging.crashdumps import generate_and_send_crashdump


@responses.activate
def test_generate_crashdump():

    fake_url = "http://mock/crashdumps/"

    def callback_success(request):
        return (200, {}, u"OK")

    responses.add_callback(
        responses.POST,
        fake_url,
        content_type="application/x-www-form-urlencoded",
        callback=callback_success,
    )

    try:
        raise ValueError("Thîngs hâppened")
    except Exception:
        exc_info = sys.exc_info()

    assert len(responses.calls) == 0
    report = generate_and_send_crashdump(exc_info, target_url=fake_url)
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == fake_url

    assert "SOFTWARE" in report
    assert "Thîngs hâppened" in report
    # print(report)

    with pytest.raises(ConnectionError):
        generate_and_send_crashdump(exc_info, target_url="http://doesnotexist/")
