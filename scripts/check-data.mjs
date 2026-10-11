#!/usr/bin/env node
// Validates the course data. Run: node scripts/check-data.mjs
// Exits non-zero on any problem, so it can gate commits and CI.
import { readFileSync } from 'node:fs';

const load = (f) => JSON.parse(readFileSync(new URL(`../data/${f}`, import.meta.url), 'utf8'));
const { items } = load('items.json');
const script = load('script.json');
const { sentences } = load('sentences.json');
const course = load('course.json');
const letters = load('letters.json');

const errors = [];
const fail = (msg) => errors.push(msg);

// Khmer block U+1780–U+17FF and Khmer Symbols U+19E0–U+19FF, plus spaces, ZWSP and basic punctuation.
const KHMER_TEXT = /^[ក-៿᧠-᧿ ​?!.,]+$/u;
const HAS_KHMER = /[ក-៿]/u;
const DOTTED = '◌';

function uniqueIds(list, label) {
  const seen = new Set();
  for (const x of list) {
    if (!x.id) fail(`${label}: entry without id: ${JSON.stringify(x).slice(0, 80)}`);
    else if (seen.has(x.id)) fail(`${label}: duplicate id ${x.id}`);
    seen.add(x.id);
  }
  return seen;
}

// ---- items ----
const itemIds = uniqueIds(items, 'items');
for (const it of items) {
  for (const f of ['km', 'rom', 'en', 'cat', 'src']) if (!it[f] || typeof it[f] !== 'string') fail(`item ${it.id}: missing ${f}`);
  if (it.km && !KHMER_TEXT.test(it.km)) fail(`item ${it.id}: non-Khmer characters in "${it.km}"`);
  if (it.km && !HAS_KHMER.test(it.km)) fail(`item ${it.id}: no Khmer letters in "${it.km}"`);
  if (it.rom && HAS_KHMER.test(it.rom)) fail(`item ${it.id}: Khmer characters in romanisation`);
  if (it.en && HAS_KHMER.test(it.en)) fail(`item ${it.id}: Khmer characters in English`);
}
const kmSeen = new Map();
for (const it of items) {
  const key = `${it.km}|${it.en}`;
  if (kmSeen.has(key)) fail(`items ${kmSeen.get(key)} and ${it.id} are the same word and meaning`);
  kmSeen.set(key, it.id);
}

// ---- script ----
const consIds = uniqueIds(script.consonants, 'consonants');
const vowIds = uniqueIds(script.vowels, 'vowels');
const digIds = uniqueIds(script.digits, 'digits');
if (script.consonants.length !== 33) fail(`expected 33 modern consonants, found ${script.consonants.length}`);
const aSeries = script.consonants.filter((c) => c.series === 'a').length;
const oSeries = script.consonants.filter((c) => c.series === 'o').length;
if (aSeries + oSeries !== script.consonants.length) fail('every consonant needs series "a" or "o"');
for (const c of script.consonants) {
  if (!/^[ក-អ]$/u.test(c.char)) fail(`consonant ${c.id}: "${c.char}" is not a single Khmer consonant (U+1780–U+17A2)`);
  for (const f of ['name', 'ipa_name', 'ipa', 'series']) if (!c[f]) fail(`consonant ${c.id}: missing ${f}`);
  // UNGEGN letter names end in â for the a-series and ô for the o-series.
  const tail = c.name.normalize('NFC').slice(-1);
  if ((c.series === 'a' && tail !== 'â') || (c.series === 'o' && tail !== 'ô')) fail(`consonant ${c.id}: name "${c.name}" disagrees with series ${c.series}`);
}
for (const v of script.vowels) {
  if (!v.char.startsWith(DOTTED) || !KHMER_TEXT.test(v.char.slice(1))) fail(`vowel ${v.id}: char should be dotted circle + Khmer vowel sign`);
  if (!KHMER_TEXT.test(v.example)) fail(`vowel ${v.id}: example "${v.example}" not Khmer`);
  for (const f of ['ipa_a', 'ipa_o', 'rom_a', 'rom_o']) if (!v[f]) fail(`vowel ${v.id}: missing ${f}`);
}
// Numerals: Khmer digits are U+17E0 (០) to U+17E9 (៩), in order.
if (script.digits.length !== 10) fail(`expected 10 digits, found ${script.digits.length}`);
for (const d of script.digits) {
  const expected = String.fromCodePoint(0x17e0 + d.value);
  if (d.char !== expected) fail(`digit ${d.id}: ${d.value} should be ${expected} (U+${(0x17e0 + d.value).toString(16).toUpperCase()}), found ${d.char}`);
  if (d.word && !KHMER_TEXT.test(d.word)) fail(`digit ${d.id}: word "${d.word}" not Khmer`);
  if (d.word_item && !itemIds.has(d.word_item)) fail(`digit ${d.id}: unknown word_item ${d.word_item}`);
}
// Number items with a numeric value must agree with the digit words.
for (const it of items.filter((x) => Number.isInteger(x.value))) {
  const digitString = String(it.value).split('').map((ch) => String.fromCodePoint(0x17e0 + Number(ch))).join('');
  if (it.digits && it.digits !== digitString) fail(`item ${it.id}: digits ${it.digits} should be ${digitString} for ${it.value}`);
}

// Independent vowels, diacritic combinations and marks (Wikipedia: Khmer script).
const indIds = uniqueIds(script.independents, 'independents');
const combIds = uniqueIds(script.combos, 'combos');
const markIds = uniqueIds(script.marks, 'marks');
for (const v of script.independents) {
  if (!v.chars?.length || !v.chars.every((c) => /^[\u17A3-\u17B3]$/u.test(c))) fail(`independent ${v.id}: chars must be independent vowel letters (U+17A3–U+17B3)`);
  for (const f of ['rom', 'ipa']) if (!v[f]) fail(`independent ${v.id}: missing ${f}`);
  if (v.example && !(v.example.km.includes(v.chars[0]) || v.chars.some((c) => v.example.km.includes(c)))) fail(`independent ${v.id}: example ${v.example.km} does not contain it`);
}
for (const k of script.combos) {
  if (!k.char.startsWith(DOTTED) || !/^[\u17B6-\u17C8]+$/u.test(k.sign)) fail(`combo ${k.id}: needs dotted circle + vowel/diacritic signs`);
  for (const f of ['ipa_a', 'ipa_o', 'rom_a', 'rom_o']) if (!k[f]) fail(`combo ${k.id}: missing ${f}`);
}
for (const m of script.marks) {
  if (!/^[\u17C6-\u17D3\u17DD]$/u.test(m.char)) fail(`mark ${m.id}: "${m.char}" is not a Khmer sign`);
  if (!m.shown.includes(m.char)) fail(`mark ${m.id}: shown form must contain the mark`);
  for (const f of ['name_km', 'name_rom', 'summary']) if (!m[f]) fail(`mark ${m.id}: missing ${f}`);
}
for (const c of script.consonants) {
  if (c.char === 'ឡ') { if (c.sub) fail('ឡ has no subscript form (Wikipedia)'); continue; }
  if (c.sub !== DOTTED + '\u17D2' + c.char) fail(`consonant ${c.id}: subscript should be coeng + ${c.char}`);
}

// ---- letters course ----
const groupIds = uniqueIds(letters.groups, 'letter groups');
const letterRefs = { consonants: consIds, vowels: vowIds, combos: combIds, indep: indIds, marks: markIds, subs: consIds, digits: digIds };
const taught = {};
for (const g of letters.groups) {
  if (!g.title) fail(`letter group ${g.id}: missing title`);
  let n = 0;
  for (const [field, ids] of Object.entries(letterRefs)) {
    for (const id of g[field] || []) {
      n += 1;
      if (!ids.has(id)) fail(`letter group ${g.id}: unknown ${field} id ${id}`);
      const key = `${field}:${id}`;
      if (taught[key]) fail(`letter group ${g.id}: ${key} already taught in ${taught[key]}`);
      taught[key] = g.id;
    }
  }
  if (n === 0) fail(`letter group ${g.id}: empty`);
  if (n > 6) fail(`letter group ${g.id}: ${n} symbols; keep sets to 6 or fewer`);
}
for (const id of consIds) if (!taught[`consonants:${id}`]) fail(`consonant ${id} is not taught in any letter group`);
for (const id of vowIds) if (!taught[`vowels:${id}`]) fail(`vowel ${id} is not taught in any letter group`);
for (const sec of letters.sections) for (const gid of sec.groups) if (!groupIds.has(gid)) fail(`letters section "${sec.title}": unknown group ${gid}`);
const inSections = new Set(letters.sections.flatMap((x) => x.groups));
for (const gid of groupIds) if (!inSections.has(gid)) fail(`letter group ${gid} is not in any section`);

// ---- sentences ----
const sentIds = uniqueIds(sentences, 'sentences');
for (const s of sentences) {
  if (!Array.isArray(s.tokens) || s.tokens.length < 2) fail(`sentence ${s.id}: needs at least two tokens`);
  for (const t of s.tokens || []) if (!itemIds.has(t)) fail(`sentence ${s.id}: token ${t} is not an item`);
  if (!s.en) fail(`sentence ${s.id}: missing en`);
  if (!s.src) fail(`sentence ${s.id}: missing src`);
}

// ---- course ----
const lessonIds = new Set();
const refs = { items: itemIds, consonants: consIds, vowels: vowIds, digits: digIds, sentences: sentIds };
for (const u of course.units) {
  if (!u.id || !u.title || !u.lessons?.length) fail(`unit ${u.id}: needs id, title and lessons`);
  if (u.km && !KHMER_TEXT.test(u.km)) fail(`unit ${u.id}: km title not Khmer`);
  for (const l of u.lessons) {
    if (lessonIds.has(l.id)) fail(`duplicate lesson id ${l.id}`);
    lessonIds.add(l.id);
    let n = 0;
    for (const [field, ids] of Object.entries(refs)) {
      for (const id of l[field] || []) { n += 1; if (!ids.has(id)) fail(`lesson ${l.id}: unknown ${field} id ${id}`); }
    }
    if (n === 0) fail(`lesson ${l.id}: has no content`);
    // The on-ramp: a lesson introduces at most four new words (the very first, three).
    if ((l.items || []).length > 4) fail(`lesson ${l.id}: ${l.items.length} new words; keep it to 4`);
  }
}
const firstLesson = course.units[0]?.lessons[0];
if (firstLesson && (firstLesson.items || []).length > 3) fail('the first lesson should introduce at most 3 words');
const used = new Set(course.units.flatMap((u) => u.lessons.flatMap((l) => l.items || [])));
const twice = course.units.flatMap((u) => u.lessons.flatMap((l) => l.items || [])).filter((id, i, a) => a.indexOf(id) !== i);
if (twice.length) fail(`items introduced in more than one lesson: ${[...new Set(twice)].join(', ')}`);
const unused = items.filter((it) => !used.has(it.id) && !sentences.some((s) => s.tokens.includes(it.id)));
if (unused.length) console.warn(`note: ${unused.length} items are not taught in any lesson or sentence: ${unused.map((x) => x.id).join(', ')}`);

const summary = `${course.units.length} units, ${lessonIds.size} lessons, ${items.length} items, ${sentences.length} sentences, ${letters.groups.length} letter groups; ${script.consonants.length} consonants (${aSeries} a-series, ${oSeries} o-series), ${script.vowels.length} vowels, ${script.combos.length} vowel+mark combinations, ${script.independents.length} independent vowels, ${script.marks.length} marks, ${script.digits.length} digits`;
if (errors.length) {
  console.error(errors.map((e) => `✗ ${e}`).join('\n'));
  console.error(`\n${errors.length} problem(s). ${summary}`);
  process.exit(1);
}
console.log(`✓ data OK: ${summary}`);
