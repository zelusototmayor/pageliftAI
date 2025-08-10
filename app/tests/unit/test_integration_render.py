import pytest
from unittest.mock import patch, MagicMock
from app.services.scrape import scrape_site
from app.services.parse import parse_html_sections
from app.services.analyze import analyze_sections
from app.services.render import render_site
import zipfile
import os

HTML_FIXTURE = '''
<html>
  <body>
    <section id="hero"><h1>Welcome</h1><p>Intro text.</p></section>
    <section id="about"><h2>About</h2><p>About us.</p></section>
    <section id="contact"><h2>Contact</h2><p>Email us.</p></section>
  </body>
</html>
'''

@pytest.mark.integration
def test_full_scrape_parse_analyze_render(tmp_path):
    # --- Scrape (simulate single page) ---
    with patch("app.services.scrape.requests.get") as mock_get, \
         patch("app.services.scrape.boto3.client") as mock_boto:
        mock_resp = MagicMock()
        mock_resp.text = HTML_FIXTURE
        mock_resp.raise_for_status = lambda: None
        mock_get.return_value = mock_resp
        mock_boto.return_value = MagicMock()
        result = scrape_site("http://example.com", max_pages=1)
        html = result.pages[0].html
    # --- Parse ---
    sections = parse_html_sections(html)
    # --- Analyze (mock OpenAI) ---
    with patch("app.services.analyze.openai.ChatCompletion.create") as mock_openai:
        mock_openai.return_value = {
            "choices": [{
                "message": {
                    "content": '[{"section_id": 0, "category": "hero", "short_copy": "Welcome!"},'
                                '{"section_id": 1, "category": "about", "short_copy": "About us."},'
                                '{"section_id": 2, "category": "contact", "short_copy": "Contact info."}]'
                }
            }]
        }
        # Convert dataclasses to dicts for analyze_sections
        section_dicts = [s.__dict__ for s in sections]
        analyzed = analyze_sections(section_dicts)
    # --- Render ---
    zip_path = render_site([a.__dict__ for a in analyzed], title="Test Site")
    # Check ZIP exists and contains index.html
    assert os.path.exists(zip_path)
    with zipfile.ZipFile(zip_path) as z:
        assert "index.html" in z.namelist() 