"""Fetch each candidate word's Khmer section from English Wiktionary and record its WT
romanisation, IPA and senses in source/verified.json.
Usage: python3 scripts/fetch_wiktionary.py scripts/source/candidates.txt   (lines: khmer|intended English)
Pages are cached under scripts/source/html/ (not committed)."""
import json,re,html,sys,time,urllib.parse,urllib.request,os,hashlib
def strip(t): return html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',t))).strip()
HERE=os.path.dirname(os.path.abspath(__file__)); SRC=os.path.join(HERE,'source'); os.makedirs(os.path.join(SRC,'html'),exist_ok=True)
def fname(w): return os.path.join(SRC,'html',hashlib.md5(w.encode()).hexdigest()+'.html')
def fetch(word):
    f=fname(word)
    if os.path.exists(f): return open(f).read()
    url='https://en.wiktionary.org/w/api.php?action=parse&format=json&formatversion=2&prop=text&redirects=1&page='+urllib.parse.quote(word)
    req=urllib.request.Request(url,headers={'User-Agent':'sok-sabay-khmer-course/0.1 (learner app data verification; https://github.com/cveenstra)'})
    for attempt in range(6):
        try:
            d=json.load(urllib.request.urlopen(req,timeout=30)); break
        except urllib.error.HTTPError as e:
            if e.code==429: time.sleep(10*(attempt+1)); continue
            raise
        except (urllib.error.URLError, TimeoutError, OSError):
            time.sleep(5*(attempt+1)); continue
    else: raise RuntimeError('429 forever')
    time.sleep(1.5)
    if 'error' in d: t='__MISSING__'
    else:
        t=d['parse']['text']
        m=re.search(r'<h2 id="Khmer".*?(?=<h2 |\Z)',t,re.S)
        t=m.group(0) if m else '__NOKHMER__'
    open(f,'w').write(t); return t
def parse(k):
    if k in ('__MISSING__','__NOKHMER__'): return {'status':k.strip('_')}
    wt=[strip(x) for x in re.findall(r'WT romanisation</a></i></th>\s*<td[^>]*>(.*?)</td>',k,re.S)]
    ipa=[strip(x) for x in re.findall(r'>IPA</a>.*?</th>\s*<td[^>]*>(.*?)</td>',k,re.S)]
    defs=[]
    for ol in re.findall(r'<ol>(.*?)</ol>',k,re.S):
        for li in re.findall(r'<li[^>]*>(.*?)</li>',ol,re.S):
            s=strip(re.sub(r'<(dl|ul)>.*?</\1>','',li,flags=re.S))
            if s: defs.append(s[:600])
    return {'status':'ok','wt':wt,'ipa':ipa,'defs':defs}
if __name__=='__main__':
    words=[w for w in open(sys.argv[1]).read().split('\n') if w.strip() and not w.startswith('#')]
    vpath=os.path.join(SRC,'verified.json')
    old=json.load(open(vpath)) if os.path.exists(vpath) else {}
    for i,w in enumerate(words):
        k,_,eng=w.partition('|'); k=k.strip()
        r=parse(fetch(k)); old[k]=r
        print(f"{k}\t{eng.strip()}\t{r['status']}\t{' / '.join(r.get('wt',[]))}\t{' ; '.join(r.get('defs',[]))[:170]}",flush=True)
        if i%20==19: json.dump(old,open(vpath,'w'),ensure_ascii=False,indent=1)
    json.dump(old,open(vpath,'w'),ensure_ascii=False,indent=1)
