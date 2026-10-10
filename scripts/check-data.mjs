#!/usr/bin/env node
// Validates the course data. Run: node scripts/check-data.mjs
// Exits non-zero on any problem, so it can gate commits and CI.
import { readFileSync } from 'node:fs';

const load = (f) => JSON.parse(readFileSync(new URL(`../data/${f}`, import.meta.url), 'utf8'));
const { items } = load('items.json');
const script = load('script.json');
const { sentences } = load('sentences.json');
const course = load('course.json');

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
    if ((l.items || []).length > 0 && (l.items || []).length < 4 && !(l.consonants || l.vowels || l.digits)) fail(`lesson ${l.id}: fewer than 4 items leaves too few answer options`);
  }
}
const used = new Set(course.units.flatMap((u) => u.lessons.flatMap((l) => l.items || [])));
const unused = items.filter((it) => !used.has(it.id) && !sentences.some((s) => s.tokens.includes(it.id)));
if (unused.length) console.warn(`note: ${unused.length} items are not taught in any lesson or sentence: ${unused.map((x) => x.id).join(', ')}`);

const summary = `${course.units.length} units, ${lessonIds.size} lessons, ${items.length} items, ${sentences.length} sentences, ${script.consonants.length} consonants (${aSeries} a-series, ${oSeries} o-series), ${script.vowels.length} vowels, ${script.digits.length} digits`;
if (errors.length) {
  console.error(errors.map((e) => `✗ ${e}`).join('\n'));
  console.error(`\n${errors.length} problem(s). ${summary}`);
  process.exit(1);
}
console.log(`✓ data OK: ${summary}`);
