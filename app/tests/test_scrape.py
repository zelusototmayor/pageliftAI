import pytest
from unittest.mock import patch, MagicMock
from app.services.scrape import scrape_site, MultiPageScrapeResult, PageScrape, Section
import requests

HTML_MAIN = '''
<html>
  <head>
    <link rel="stylesheet" href="/static/style.css">
  </head>
  <body>
    <nav>
      <a href="/about">About</a>
      <a href="/contact">Contact</a>
    </nav>
    <img src="/images/logo.png">
    <section id="hero">Hero Section</section>
  </body>
</html>
'''

HTML_ABOUT = '''
<html>
  <body>
    <section id="about">About Section</section>
    <img src="/images/about.png">
  </body>
</html>
'''

HTML_CONTACT = '''
<html>
  <body>
    <section id="contact">Contact Section</section>
    <img src="/images/contact.png">
  </body>
</html>
'''

@patch("app.services.scrape.boto3.client")
@patch("app.services.scrape.requests.get")
def test_multi_page_scrape_and_section_extraction(mock_get, mock_boto):
    # Mock responses for each URL
    def side_effect(url, *args, **kwargs):
        mock_resp = MagicMock()
        if url.endswith("/about"):
            mock_resp.text = HTML_ABOUT
        elif url.endswith("/contact"):
            mock_resp.text = HTML_CONTACT
        else:
            mock_resp.text = HTML_MAIN
        mock_resp.raise_for_status = lambda: None
        return mock_resp
    mock_get.side_effect = side_effect
    mock_s3 = MagicMock()
    mock_boto.return_value = mock_s3

    url = "http://example.com"
    result = scrape_site(url, max_pages=3)
    assert isinstance(result, MultiPageScrapeResult)
    assert len(result.pages) == 3
    # Check each page for expected sections
    page_urls = [p.url for p in result.pages]
    assert url in page_urls
    assert url + "/about" in page_urls
    assert url + "/contact" in page_urls
    # Check that sections are extracted
    for page in result.pages:
        assert isinstance(page, PageScrape)
        assert isinstance(page.sections, list)
        # Each page should have at least one section
        assert any(isinstance(s, Section) for s in page.sections)
    # S3 put_object called for each page
    assert mock_s3.put_object.call_count == 3 

def test_403_retry_with_user_agent(monkeypatch):
    from app.services import scrape
    calls = []
    class MockResp:
        def __init__(self, status_code, text):
            self.status_code = status_code
            self.text = text
        def raise_for_status(self):
            if self.status_code == 403:
                raise requests.exceptions.HTTPError(response=self)
        @property
        def content(self):
            return self.text
    def mock_get(url, timeout=30, headers=None):
        calls.append(headers)
        if not headers:
            return MockResp(403, "blocked")
        else:
            return MockResp(200, "<html><body><section>ok</section></body></html>")
    monkeypatch.setattr(scrape.requests, "get", mock_get)
    class DummyS3:
        def put_object(self, **kwargs):
            pass
    monkeypatch.setattr(scrape.boto3, "client", lambda *a, **kw: DummyS3())
    result = scrape.scrape_site("http://fake.com", max_pages=1)
    assert len(calls) == 2  # First without UA, then with UA
    assert calls[0] is None
    assert calls[1] is not None and "User-Agent" in calls[1]
    assert result.pages[0].html == "<html><body><section>ok</section></body></html>" 