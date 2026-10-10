// Turns a lesson definition (item, letter, vowel, digit and sentence ids) into a
// shuffled list of questions. Every question carries an SRS key so a miss can be
// resurfaced later in Review.

export function shuffle(arr, rnd = Math.random) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

const sample = (arr, n) => shuffle(arr).slice(0, n);

export function indexData(data) {
  const byId = (list) => Object.fromEntries(list.map((x) => [x.id, x]));
  return {
    ...data,
    item: byId(data.items),
    consonant: byId(data.script.consonants),
    vowel: byId(data.script.vowels),
    digit: byId(data.script.digits),
    sentence: byId(data.sentences),
  };
}

// Distractors: prefer the same category, never the same meaning or spelling.
function itemDistractors(db, item, n = 3) {
  const differs = (x) => x.id !== item.id && x.en !== item.en && x.km !== item.km && x.rom !== item.rom;
  const same = db.items.filter((x) => x.cat === item.cat && differs(x));
  const other = db.items.filter((x) => x.cat !== item.cat && differs(x));
  const picked = sample(same, n);
  if (picked.length < n) picked.push(...sample(other, n - picked.length));
  return picked;
}

const q = {
  k2e: (db, it) => ({ type: 'k2e', key: `item:${it.id}`, item: it, options: shuffle([it, ...itemDistractors(db, it)]) }),
  e2k: (db, it) => ({ type: 'e2k', key: `item:${it.id}`, item: it, options: shuffle([it, ...itemDistractors(db, it)]) }),
  rom: (db, it) => ({ type: 'rom', key: `item:${it.id}`, item: it, options: shuffle([it, ...itemDistractors(db, it)]) }),
  match: (db, items) => ({ type: 'match', key: null, pairs: sample(items, Math.min(5, items.length)) }),
  build: (db, s) => {
    const words = s.tokens.map((id) => db.item[id]);
    const used = new Set(s.tokens);
    const extra = sample(db.items.filter((x) => !used.has(x.id) && x.km.split(' ').length === 1), Math.min(3, Math.max(2, 7 - words.length)));
    return { type: 'build', key: `sent:${s.id}`, sentence: s, words, bank: shuffle([...words, ...extra]) };
  },
  letterSound: (db, c) => ({ type: 'letterSound', key: `cons:${c.id}`, letter: c,
    options: shuffle([c, ...sample(db.script.consonants.filter((x) => x.id !== c.id && x.name !== c.name), 3)]) }),
  letterPick: (db, c) => ({ type: 'letterPick', key: `cons:${c.id}`, letter: c,
    options: shuffle([c, ...sample(db.script.consonants.filter((x) => x.id !== c.id && x.name !== c.name), 3)]) }),
  series: (db, c) => ({ type: 'series', key: `cons:${c.id}`, letter: c }),
  vowel: (db, v) => ({ type: 'vowel', key: `vow:${v.id}`, vowel: v,
    options: shuffle([v, ...sample(db.script.vowels.filter((x) => x.id !== v.id && x.ipa_a !== v.ipa_a), 3)]) }),
  digit: (db, d) => ({ type: 'digit', key: `dig:${d.id}`, digit: d,
    options: shuffle([d, ...sample(db.script.digits.filter((x) => x.id !== d.id), 3)]) }),
};

export function buildLesson(db, lesson) {
  const out = [];
  const items = (lesson.items || []).map((id) => db.item[id]);
  const cons = (lesson.consonants || []).map((id) => db.consonant[id]);
  const vows = (lesson.vowels || []).map((id) => db.vowel[id]);
  const digs = (lesson.digits || []).map((id) => db.digit[id]);
  const sents = (lesson.sentences || []).map((id) => db.sentence[id]);

  // New words first meet you Khmer-to-English, with the romanisation shown.
  items.forEach((it, i) => out.push(i % 3 === 2 ? q.rom(db, it) : q.k2e(db, it)));
  const second = shuffle(items).slice(0, Math.ceil(items.length / 2)).map((it) => q.e2k(db, it));

  cons.forEach((c) => out.push(q.letterSound(db, c)));
  shuffle(cons).slice(0, Math.ceil(cons.length / 2)).forEach((c) => out.push(q.letterPick(db, c)));
  shuffle(cons).slice(0, Math.min(3, cons.length)).forEach((c) => out.push(q.series(db, c)));
  vows.forEach((v) => out.push(q.vowel(db, v)));
  digs.forEach((d) => out.push(q.digit(db, d)));

  const tail = [...second, ...sents.map((s) => q.build(db, s))];
  const list = [...out.slice(0, 14), ...(items.length >= 4 ? [q.match(db, items)] : []), ...shuffle(tail)];
  return list.slice(0, 18);
}

// Review: turn due SRS keys back into questions of a different direction than
// the one usually seen first, so the review isn't a repeat of the lesson.
export function buildReview(db, keys) {
  const out = [];
  for (const key of keys) {
    const [kind, id] = key.split(':');
    if (kind === 'item' && db.item[id]) out.push((out.length % 2 ? q.e2k : q.k2e)(db, db.item[id]));
    else if (kind === 'sent' && db.sentence[id]) out.push(q.build(db, db.sentence[id]));
    else if (kind === 'cons' && db.consonant[id]) out.push((out.length % 2 ? q.letterPick : q.letterSound)(db, db.consonant[id]));
    else if (kind === 'vow' && db.vowel[id]) out.push(q.vowel(db, db.vowel[id]));
    else if (kind === 'dig' && db.digit[id]) out.push(q.digit(db, db.digit[id]));
  }
  const reviewItems = keys.filter((k) => k.startsWith('item:')).map((k) => db.item[k.slice(5)]).filter(Boolean);
  if (reviewItems.length >= 4) out.splice(Math.min(4, out.length), 0, q.match(db, reviewItems));
  return out;
}

export function isCorrect(question, answer) {
  switch (question.type) {
    case 'k2e': case 'e2k': case 'rom': return answer === question.item.id;
    case 'letterSound': case 'letterPick': return answer === question.letter.id;
    case 'series': return answer === question.letter.series;
    case 'vowel': return answer === question.vowel.id;
    case 'digit': return answer === question.digit.id;
    case 'build': return Array.isArray(answer) && answer.map((w) => w.km).join(' ') === question.words.map((w) => w.km).join(' ');
    case 'match': return answer === true;
    default: return false;
  }
}
