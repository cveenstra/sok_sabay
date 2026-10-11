"""Extract the independent vowels, diacritics and diacritic-vowel combinations from
Wikipedia's "Khmer script" article (wikitext) into scripts/source/*_raw.json.
Usage: python3 scripts/parse_script_extra.py <khmer_script.wiki>
Fetch the wikitext with:
  https://en.wikipedia.org/w/api.php?action=parse&page=Khmer_script&prop=wikitext&format=json&formatversion=2
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'source')
wiki = open(sys.argv[1]).read()

def section(title):
    m = re.search(r'^=+\s*' + re.escape(title) + r'\s*=+\s*$(.*?)(?=^==)', wiki, re.S | re.M)
    return m.group(1)

def clean(cell):
    cell = re.sub(r'^\s*(?:(?:colspan|rowspan|bgcolor|style|align)="?[^"|]*"?\s*)+\|', '', cell)
    cell = re.sub(r'<ref[^>]*/>|<ref[^>]*>.*?</ref>', '', cell, flags=re.S)
    cell = re.sub(r'\{\{(?:lang|transliteration)\|km\|([^}]*)\}\}', r'\1', cell)
    cell = re.sub(r'\{\{IPA\|(?:km\|)?([^}|]*)(?:\|[^}]*)?\}\}', r'\1', cell)
    cell = re.sub(r"<[^>]+>|'''?|\[\[(?:[^]|]*\|)?([^]]*)\]\]", lambda m: m.group(1) or '', cell)
    return re.sub(r'\s+', ' ', cell).strip()

def rows(table_text):
    out = []
    for raw in re.split(r'^\|-.*$', table_text, flags=re.M)[1:]:
        cells = []
        for line in raw.strip().split('\n'):
            if line.startswith('|}') or not line.startswith('|'): continue
            for part in re.split(r'\|\|', line[1:]):
                span = re.search(r'colspan="?(\d+)', part)
                cells.extend([clean(part)] * (int(span.group(1)) if span else 1))
        if cells: out.append(cells)
    return out

def first_table(text):
    m = re.search(r'\{\|.*?\n\|\}', text, re.S)
    return m.group(0)

# independent vowels: char | IPA | GD | UNGEGN
indep = []
for c in rows(first_table(section('Independent vowels'))):
    chars = re.findall(r'[ក-៿]+', c[0])
    if len(c) < 4 or 'Obsolete' in ' '.join(c): continue
    indep.append({'chars': chars, 'ipa': c[1], 'gd': c[2], 'ungegn': c[3]})

# diacritics: char | Khmer name + translit | function
diac = []
for c in rows(first_table(section('Diacritics'))):
    if len(c) < 3: continue
    ch = re.findall(r'[ំ-៓៝ុ]', c[0])
    name_km = ' '.join(re.findall(r'[ក-៿]+', c[1]))
    name_rom = re.sub(r'[ក-៿]+', '', c[1]).strip()
    diac.append({'char': ch[0] if ch else c[0], 'name_km': name_km, 'name_rom': name_rom, 'function': c[2]})

# diacritic + vowel combinations (shown on អ): combo | IPA a | IPA o | GD a | GD o | UNGEGN a | UNGEGN o | ALA | notes
mod = re.search(r'===Modification by diacritics===(.*?)===', wiki, re.S).group(1)
combos = []
for c in rows(first_table(mod)):
    if len(c) < 7 or not re.search(r'[ក-៿]', c[0]): continue
    combos.append({'combo': c[0], 'ipa_a': c[1], 'ipa_o': c[2], 'ungegn_a': c[5], 'ungegn_o': c[6]})

for name, obj in (('independent_raw.json', indep), ('diacritics_raw.json', diac), ('combos_raw.json', combos)):
    json.dump(obj, open(os.path.join(SRC, name), 'w'), ensure_ascii=False, indent=1)
print(f'independent {len(indep)}, diacritics {len(diac)}, combos {len(combos)}')
