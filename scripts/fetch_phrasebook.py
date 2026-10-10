import json,re,html,time,urllib.parse,urllib.request,sys
def strip(t): return html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',t))).strip()
pages=sys.argv[1:]
out={}
for p in pages:
    url='https://en.wiktionary.org/w/api.php?action=parse&format=json&formatversion=2&prop=text&redirects=1&page='+urllib.parse.quote(p)
    req=urllib.request.Request(url,headers={'User-Agent':'sok-sabay-khmer-course/0.1 (learner app data verification; https://github.com/cveenstra)'})
    for a in range(5):
        try: d=json.load(urllib.request.urlopen(req,timeout=30)); break
        except Exception as e: time.sleep(6*(a+1))
    time.sleep(1.5)
    if 'error' in d: print(p,'MISSING'); continue
    t=d['parse']['text']
    hits=[]
    for m in re.finditer(r'<li>Khmer:(.*?)</li>',t,re.S):
        seg=m.group(1)
        for k in re.finditer(r'<span class="Khmr" lang="km">(.*?)</span>\s*<span class="mention-gloss-paren annotation-paren">\(</span><span lang="km-Latn" class="tr Latn">(.*?)</span>',seg,re.S):
            hits.append((strip(k.group(1)),strip(k.group(2))))
        if not hits: hits.append(('RAW',strip(seg)[:200]))
    out[p]=hits
    print(p,'=>',hits)
json.dump(out,open('phrasebook.json','w'),ensure_ascii=False,indent=1)
