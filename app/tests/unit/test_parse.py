import pytest
from app.services.parse import parse_html_sections, SectionData

HTML_HEADINGS = '''
<body>
  <h1>Welcome</h1>
  <p>Intro text.</p>
  <h2>About</h2>
  <p>About text.</p>
  <h3>Contact</h3>
  <p>Email us.</p>
</body>
'''

HTML_SECTIONS = '''
<body>
  <section id="hero"><h1>Hero</h1><p>Hero text.</p></section>
  <section id="about"><h2>About</h2><p>About us.</p></section>
</body>
'''

HTML_DIVS = '''
<body>
  <div class="services"><h2>Services</h2><p>Our services.</p><img src="/img/s1.png"></div>
  <div id="gallery"><h2>Gallery</h2><img src="/img/g1.png"></div>
</body>
'''

def test_parse_headings():
    sections = parse_html_sections(HTML_HEADINGS)
    assert len(sections) == 3
    assert sections[0].heading == "Welcome"
    assert "Intro text." in sections[0].text
    assert sections[1].heading == "About"
    assert "About text." in sections[1].text
    assert sections[2].heading == "Contact"
    assert "Email us." in sections[2].text

def test_parse_sections():
    sections = parse_html_sections(HTML_SECTIONS)
    assert len(sections) == 2
    assert any("Hero" in s.text for s in sections)
    assert any("About" in s.text for s in sections)

def test_parse_divs():
    sections = parse_html_sections(HTML_DIVS)
    assert len(sections) == 2
    assert any("services" in s.classes for s in sections)
    assert any("gallery" == s.id for s in sections)
    assert any("/img/s1.png" in s.img_urls for s in sections)
    assert any("/img/g1.png" in s.img_urls for s in sections) 