// Turns lesson definitions into question lists. Every graded question carries an
// SRS key so a miss (or a peek at the answer) can be resurfaced later in Review.
// New words and letters are always met first on an "intro" flashcard.

export function shuffle(arr, rnd = Math.random) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
const sample = (arr, n) => shuffle(arr).slice(0, Math.max(0, n));
const uniqBy = (arr, f) => { const seen = new Set(); return arr.filter((x) => { const k = f(x); if (seen.has(k)) return false; seen.add(k); return true; }); };

export function indexData(data) {
  const byId = (list) => Object.fromEntries(list.map((x) => [x.id, x]));
  const s = data.script;
  return {
    ...data,
    item: byId(data.items),
    consonant: byId(s.consonants),
    vowel: byId(s.vowels),
    digit: byId(s.digits),
    combo: byId(s.combos),
    indep: byId(s.independents),
    mark: byId(s.marks),
    sentence: byId(data.sentences),
    group: byId(data.letters.groups),
  };
}

// ---------- symbols: what a letters group teaches, and what a learner can read ----------
const SIGN = (v) => v.char.replace('◌', '');
export function groupSymbols(db, g) {
  return [
    ...(g.consonants || []).map((id) => ({ kind: 'cons', id, key: `cons:${id}`, sym: db.consonant[id] })),
    ...(g.vowels || []).map((id) => ({ kind: 'vow', id, key: `vow:${id}`, sym: db.vowel[id] })),
    ...(g.combos || []).map((id) => ({ kind: 'comb', id, key: `comb:${id}`, sym: db.combo[id] })),
    ...(g.indep || []).map((id) => ({ kind: 'ind', id, key: `ind:${id}`, sym: db.indep[id] })),
    ...(g.marks || []).map((id) => ({ kind: 'mark', id, key: `mark:${id}`, sym: db.mark[id] })),
    ...(g.subs || []).map((id) => ({ kind: 'sub', id, key: `sub:${id}`, sym: db.consonant[id] })),
    ...(g.digits || []).map((id) => ({ kind: 'dig', id, key: `dig:${id}`, sym: db.digit[id] })),
  ];
}

/** Every Khmer character a learner can read after finishing groups[0..upto]. */
export function readableChars(db, upto) {
  const set = new Set();
  for (const g of db.letters.groups.slice(0, upto + 1)) {
    for (const s of groupSymbols(db, g)) {
      if (s.kind === 'cons') set.add(s.sym.char);
      if (s.kind === 'vow') [...SIGN(s.sym)].forEach((c) => set.add(c));
      if (s.kind === 'comb') [...s.sym.sign].forEach((c) => set.add(c));
      if (s.kind === 'ind') s.sym.chars.forEach((c) => set.add(c));
      if (s.kind === 'mark') set.add(s.sym.char);
      if (s.kind === 'sub') { set.add('្'); set.add(s.sym.char); }
      if (s.kind === 'dig') set.add(s.sym.char);
    }
  }
  return set;
}
const isKhmerChar = (c) => /[ក-៿]/.test(c);
export function wordsReadableWith(db, chars) {
  return db.items.filter((it) => [...it.km].filter(isKhmerChar).every((c) => chars.has(c)));
}

// ---------- distractors ----------
function itemDistractors(db, item, n = 3) {
  const differs = (x) => x.id !== item.id && x.en !== item.en && x.km !== item.km && x.rom !== item.rom;
  const same = db.items.filter((x) => x.cat === item.cat && differs(x));
  const other = db.items.filter((x) => x.cat !== item.cat && differs(x));
  const picked = sample(same, n);
  if (picked.length < n) picked.push(...sample(other, n - picked.length));
  return picked;
}
const others = (list, x, n, same = () => false) => sample(list.filter((y) => y.id !== x.id && !same(y, x)), n);

// first IPA variant and first UNGEGN value, e.g. "[ɓ], [p]" -> "[ɓ]"
const firstIpa = (s) => (s.match(/\[[^\]]*\]/) || [s])[0];
const firstVal = (s) => s.split(',')[0].trim();
/** A consonant + vowel syllable, read by the spelling rule (UNGEGN + IPA from Wikipedia's tables). */
export function syllable(c, v) {
  const a = c.series === 'a';
  const ipaC = firstIpa(c.ipa).slice(1, -1);
  const ipaV = firstIpa(a ? v.ipa_a : v.ipa_o).slice(1, -1);
  return { id: `${c.id}+${v.id}`, km: c.char + SIGN(v), rom: firstVal(c.value) + (a ? v.rom_a : v.rom_o), ipa: `[${ipaC}${ipaV}]`, c, v };
}

// ---------- question makers ----------
const q = {
  intro: (kind, x) => ({ type: 'intro', kind, x, key: null }),
  k2e: (db, it) => ({ type: 'k2e', key: `item:${it.id}`, item: it, options: shuffle([it, ...itemDistractors(db, it)]) }),
  e2k: (db, it) => ({ type: 'e2k', key: `item:${it.id}`, item: it, options: shuffle([it, ...itemDistractors(db, it)]) }),
  rom: (db, it) => ({ type: 'rom', key: `item:${it.id}`, item: it, options: shuffle([it, ...itemDistractors(db, it)]) }),
  match: (db, items) => ({ type: 'match', key: null, pairs: sample(uniqBy(items, (x) => x.en), Math.min(5, items.length)) }),
  build: (db, s) => {
    const words = s.tokens.map((id) => db.item[id]);
    const used = new Set(s.tokens);
    const extra = sample(db.items.filter((x) => !used.has(x.id) && !x.km.includes(' ') && !words.some((w) => w.km === x.km)), Math.min(3, Math.max(2, 7 - words.length)));
    return { type: 'build', key: `sent:${s.id}`, sentence: s, words, bank: shuffle([...words, ...extra]) };
  },
  k2eSent: (db, s) => ({ type: 'k2eSent', key: `sent:${s.id}`, sentence: s, words: s.tokens.map((id) => db.item[id]),
    options: shuffle([s, ...others(db.sentences, s, 3, (y, x) => y.en === x.en)]) }),
  letterSound: (db, c) => ({ type: 'letterSound', key: `cons:${c.id}`, letter: c,
    options: shuffle([c, ...others(db.script.consonants, c, 3, (y, x) => y.name === x.name)]) }),
  letterPick: (db, c) => ({ type: 'letterPick', key: `cons:${c.id}`, letter: c,
    options: shuffle([c, ...others(db.script.consonants, c, 3, (y, x) => y.name === x.name)]) }),
  series: (db, c) => ({ type: 'series', key: `cons:${c.id}`, letter: c }),
  vowel: (db, v) => ({ type: 'vowel', key: `vow:${v.id}`, vowel: v,
    options: shuffle([v, ...others(db.script.vowels, v, 3, (y, x) => y.ipa_a === x.ipa_a || y.rom_a === x.rom_a)]) }),
  vowelPick: (db, v) => ({ type: 'vowelPick', key: `vow:${v.id}`, vowel: v,
    options: shuffle([v, ...others(db.script.vowels, v, 3, (y, x) => y.rom_a === x.rom_a)]) }),
  syllable: (db, c, v, pool) => {
    const right = syllable(c, v);
    // Wrong answers: the same consonant with other vowels, and the same spelling read with the other series.
    const twin = db.script.consonants.find((x) => x.series !== c.series && x.value === c.value);
    const wrong = uniqBy([
      ...(twin ? [{ ...syllable(twin, v), id: `${c.id}+${v.id}~` }] : []),
      ...pool.concat(db.script.vowels).filter((x) => x.id !== v.id).map((x) => syllable(c, x)),
    ].filter((x) => x.rom !== right.rom), (x) => x.rom);
    return { type: 'syllable', key: `vow:${v.id}`, syl: right, options: shuffle([right, ...wrong.slice(0, 1), ...sample(wrong.slice(1), 2)]) };
  },
  seriesPair: (db, v, a, o) => {
    const pick = Math.random() < 0.5 ? a : o;
    return { type: 'seriesPair', key: `vow:${v.id}`, vowel: v, target: syllable(pick, v), options: shuffle([syllable(a, v), syllable(o, v)]) };
  },
  combo: (db, k) => ({ type: 'combo', key: `comb:${k.id}`, combo: k,
    options: shuffle([k, ...others(db.script.combos, k, 3, (y, x) => y.rom_a === x.rom_a)]) }),
  indep: (db, iv) => ({ type: 'indep', key: `ind:${iv.id}`, indep: iv,
    options: shuffle([iv, ...others(db.script.independents, iv, 3, (y, x) => y.rom === x.rom)]) }),
  indepPick: (db, iv) => ({ type: 'indepPick', key: `ind:${iv.id}`, indep: iv,
    options: shuffle([iv, ...others(db.script.independents, iv, 3, (y, x) => y.rom === x.rom)]) }),
  mark: (db, m) => ({ type: 'mark', key: `mark:${m.id}`, mark: m, options: shuffle([m, ...others(db.script.marks, m, 3)]) }),
  sub: (db, c, pool) => ({ type: 'sub', key: `sub:${c.id}`, letter: c,
    options: shuffle([c, ...sample(uniqBy(pool, (x) => x.id).filter((x) => x.id !== c.id && x.sub), 3)]) }),
  digit: (db, d) => ({ type: 'digit', key: `dig:${d.id}`, digit: d, options: shuffle([d, ...others(db.script.digits, d, 3)]) }),
  readWord: (db, it, pool) => ({ type: 'readWord', key: `item:${it.id}`, item: it,
    options: shuffle([it, ...sample(uniqBy(pool, (x) => x.en).filter((x) => x.id !== it.id && x.en !== it.en), 3)]) }),
};

// ---------- course lessons (words) ----------
// Gentle by design: every new word is introduced on a card, tested three ways, then
// mixed with a couple of words from earlier lessons in the same unit.
export function buildLesson(db, lesson, unit) {
  const fresh = (lesson.items || []).map((id) => db.item[id]);
  const digs = (lesson.digits || []).map((id) => db.digit[id]);
  const sents = (lesson.sentences || []).map((id) => db.sentence[id]);
  const idx = unit.lessons.findIndex((l) => l.id === lesson.id);
  const earlier = unit.lessons.slice(0, idx).flatMap((l) => l.items || []).map((id) => db.item[id]);
  const prior = sample(earlier, 2);
  const out = [];
  fresh.forEach((it) => out.push(q.intro('item', it), q.k2e(db, it)));
  digs.forEach((d) => out.push(q.intro('dig', d), q.digit(db, d)));
  out.push(...shuffle([...fresh.map((it, i) => (i % 2 ? q.e2k : q.rom)(db, it)), ...prior.map((it) => q.k2e(db, it))]));
  if (fresh.length + prior.length >= 3) out.push(q.match(db, [...fresh, ...prior]));
  out.push(...shuffle(fresh).slice(0, 2).map((it) => q.e2k(db, it)));
  sents.forEach((s) => out.push(q.k2eSent(db, s), q.build(db, s)));
  return out;
}

/** A unit's closing practice: everything in the unit, no intros. */
export function buildUnitPractice(db, unit) {
  const items = uniqBy(unit.lessons.flatMap((l) => l.items || []), (x) => x).map((id) => db.item[id]);
  const sents = unit.lessons.flatMap((l) => l.sentences || []).map((id) => db.sentence[id]);
  const out = sample(items, 9).map((it, i) => [q.k2e, q.e2k, q.rom][i % 3](db, it));
  if (items.length >= 4) out.splice(3, 0, q.match(db, sample(items, 5)));
  sample(sents, 2).forEach((s, i) => out.push((i ? q.k2eSent : q.build)(db, s)));
  return out;
}

// ---------- letters lessons ----------
export function buildLettersLesson(db, group, { practiceOnly = false } = {}) {
  const gi = db.letters.groups.findIndex((g) => g.id === group.id);
  const out = [];
  const intro = (k, x) => { if (!practiceOnly) out.push(q.intro(k, x)); };
  const list = (field, table) => (group[field] || []).map((id) => db[table][id]);
  const cons = list('consonants', 'consonant');
  const vows = list('vowels', 'vowel');
  const combos = list('combos', 'combo');
  const indeps = list('indep', 'indep');
  const marks = list('marks', 'mark');
  const subs = list('subs', 'consonant');
  const digs = list('digits', 'digit');

  const knownCons = db.letters.groups.slice(0, gi + 1).flatMap((g) => g.consonants || []).map((id) => db.consonant[id]);
  const knownA = knownCons.filter((c) => c.series === 'a');
  const knownO = knownCons.filter((c) => c.series === 'o');

  cons.forEach((c) => { intro('cons', c); out.push(q.letterSound(db, c)); });
  shuffle(cons).forEach((c) => out.push(q.letterPick(db, c)));
  if (knownO.length) shuffle(cons).slice(0, 3).forEach((c) => out.push(q.series(db, c)));

  vows.forEach((v) => {
    intro('vow', v);
    out.push(q.vowel(db, v));
    const ca = sample(knownA, 1)[0]; const co = sample(knownO, 1)[0];
    if (ca) out.push(q.syllable(db, ca, v, vows));
    if (co) out.push(q.syllable(db, co, v, vows));
  });
  if (vows.length) {
    shuffle(vows).slice(0, 2).forEach((v) => out.push(q.vowelPick(db, v)));
    const pairs = knownA.flatMap((a) => knownO.filter((o) => o.value === a.value).map((o) => [a, o]));
    shuffle(vows).slice(0, 2).forEach((v) => { const p = sample(pairs, 1)[0]; if (p) out.push(q.seriesPair(db, v, p[0], p[1])); });
  }
  combos.forEach((k) => { intro('comb', k); out.push(q.combo(db, k)); });
  indeps.forEach((iv) => { intro('ind', iv); out.push(q.indep(db, iv)); });
  shuffle(indeps).forEach((iv) => out.push(q.indepPick(db, iv)));
  marks.forEach((m) => { intro('mark', m); out.push(q.mark(db, m)); });
  subs.forEach((c) => { intro('sub', c); out.push(q.sub(db, c, knownCons)); });
  digs.forEach((d) => { intro('dig', d); out.push(q.digit(db, d)); });

  // read real words made only of letters learned so far
  const readable = wordsReadableWith(db, readableChars(db, gi));
  if (readable.length >= 4) sample(readable, practiceOnly ? 4 : 3).forEach((it) => out.push(q.readWord(db, it, readable)));
  return practiceOnly ? shuffle(out).slice(0, 14) : out;
}

// ---------- flashcards ----------
export function deckFor(db, deck) {
  if (deck.kind === 'unit') {
    const unit = db.course.units.find((u) => u.id === deck.id);
    return uniqBy(unit.lessons.flatMap((l) => l.items || []), (x) => x).map((id) => ({ key: `item:${id}`, kind: 'item', x: db.item[id] }));
  }
  return groupSymbols(db, db.group[deck.id]).map((s) => ({ key: s.key, kind: s.kind, x: s.sym }));
}

// ---------- review ----------
export function buildReview(db, keys) {
  const out = [];
  for (const key of keys) {
    const [kind, id] = key.split(':');
    const flip = out.length % 2;
    if (kind === 'item' && db.item[id]) out.push((flip ? q.e2k : q.k2e)(db, db.item[id]));
    else if (kind === 'sent' && db.sentence[id]) out.push((flip ? q.k2eSent : q.build)(db, db.sentence[id]));
    else if (kind === 'cons' && db.consonant[id]) out.push((flip ? q.letterPick : q.letterSound)(db, db.consonant[id]));
    else if (kind === 'vow' && db.vowel[id]) out.push((flip ? q.vowelPick : q.vowel)(db, db.vowel[id]));
    else if (kind === 'comb' && db.combo[id]) out.push(q.combo(db, db.combo[id]));
    else if (kind === 'ind' && db.indep[id]) out.push((flip ? q.indepPick : q.indep)(db, db.indep[id]));
    else if (kind === 'mark' && db.mark[id]) out.push(q.mark(db, db.mark[id]));
    else if (kind === 'sub' && db.consonant[id]) out.push(q.sub(db, db.consonant[id], db.script.consonants));
    else if (kind === 'dig' && db.digit[id]) out.push(q.digit(db, db.digit[id]));
  }
  const reviewItems = keys.filter((k) => k.startsWith('item:')).map((k) => db.item[k.slice(5)]).filter(Boolean);
  if (reviewItems.length >= 4) out.splice(Math.min(4, out.length), 0, q.match(db, reviewItems));
  return out;
}

// ---------- grading ----------
export function rightAnswer(question) {
  switch (question.type) {
    case 'k2e': case 'e2k': case 'rom': case 'readWord': return question.item.id;
    case 'k2eSent': return question.sentence.id;
    case 'letterSound': case 'letterPick': case 'sub': return question.letter.id;
    case 'series': return question.letter.series;
    case 'vowel': case 'vowelPick': return question.vowel.id;
    case 'syllable': return question.syl.id;
    case 'seriesPair': return question.target.id;
    case 'combo': return question.combo.id;
    case 'indep': case 'indepPick': return question.indep.id;
    case 'mark': return question.mark.id;
    case 'digit': return question.digit.id;
    default: return null;
  }
}

export function isCorrect(question, answer) {
  if (question.type === 'build') return Array.isArray(answer) && answer.map((w) => w.km).join(' ') === question.words.map((w) => w.km).join(' ');
  if (question.type === 'match') return answer === true;
  return answer != null && answer === rightAnswer(question);
}
