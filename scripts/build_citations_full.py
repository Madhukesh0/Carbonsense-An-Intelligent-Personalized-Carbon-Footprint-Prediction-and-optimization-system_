"""Regenerate citations-full.tex from citations.tex + references.bib.

Produces the self-contained LaTeX file (inline thebibliography) with
LaTeX-safe output: bare URLs wrapped in \\url{}, ~ -> \\approx, < > -> $<$/$>$.
Run: py -3.13 scripts/build_citations_full.py
"""

import re

BS = chr(92)
tex = open('citations/citations.tex', encoding='utf-8').read()
bib = open('citations/references.bib', encoding='utf-8').read()

url_re = re.compile(r'https?://[^\s,;)}\\]+')
tilde_re = re.compile(r'(?<![A-Za-z0-9])~(?=[0-9])')


def latex_safe(text):
    text = url_re.sub(lambda m: BS + 'url{' + m.group(1) + '}', text)
    text = tilde_re.sub(lambda m: BS + 'approx', text)
    text = text.replace('<', '$<$').replace('>', '$>$')
    return text


entries = []
for m in re.finditer(r'@(\w+)\{([^,]+),\n(.*?)\n\}', bib, re.S):
    key, body = m.group(2).strip(), m.group(3)
    fields = {}
    for fm in re.finditer(r'(\w+)\s*=\s*\{(.*?)\}\s*,?\s*\n(?=\s*\w+\s*=|\Z)', body + '\n', re.S):
        fields[fm.group(1).lower()] = re.sub(r'\s+', ' ', fm.group(2)).strip()
    entries.append((key, fields))


def make_item(key, f):
    parts = []
    author = f.get('author', '').replace('{', '').replace('}', '')
    if author:
        parts.append(author)
    title = f.get('title', '')
    hp = f.get('howpublished', '')
    m_url = re.search(r'url\{([^}]+)\}', hp)
    if m_url:
        parts.append(title + '. ' + BS + 'url{' + m_url.group(1) + '}')
    elif f.get('journal'):
        j = title + '. ' + BS + 'textit{' + f['journal'] + '}'
        if f.get('volume'):
            j += ', vol. ' + f['volume']
        if f.get('pages'):
            j += ', ' + f['pages']
        if f.get('year'):
            j += ', ' + f['year']
        parts.append(j)
    elif f.get('institution'):
        parts.append(title + '. ' + f['institution'] + (', ' + f['year'] if f.get('year') else ''))
    else:
        parts.append(title)
    url = f.get('url', '')
    if url and not m_url:
        parts.append(BS + 'url{' + url + '}')
    doi = f.get('doi', '')
    if doi and not url:
        parts.append('doi: ' + doi)
    note = f.get('note', '')
    if note:
        parts.append(latex_safe(note))
    parts = [parts[0].rstrip('. ')] + [p.rstrip('. ') for p in parts[1:]]
    return '. '.join([p for p in parts if p]) + '.'


items = [BS + 'bibitem{' + key + '}\n' + make_item(key, f) for key, f in entries]
bib_block = (BS + 'begin{thebibliography}{99}\n' + BS + 'small\n\n'
             + '\n\n'.join(items) + '\n\n' + BS + 'end{thebibliography}')

bib_re = re.compile(
    re.escape(BS + 'bibliographystyle{plain}') + r'\s*\n' +
    re.escape(BS + 'bibliography{references}'))
s = bib_re.sub(lambda m: bib_block, tex)
s = s.replace('%   pdflatex citations.tex   (then bibtex citations, pdflatex x2)\n', '')
s = s.replace(
    '% citations.tex — CarbonSense: Emission Factors, Sources and Access Dates',
    '% citations-full.tex — CarbonSense: Emission Factors, Sources and Access Dates\n'
    '% SELF-CONTAINED: bibliography is inline (compile with pdflatex alone, twice).')

assert BS + 'bibliography{references}' not in s
open('citations/citations-full.tex', 'w', encoding='utf-8').write(s)
print('regenerated; bibitems:', s.count(BS + 'bibitem'))
