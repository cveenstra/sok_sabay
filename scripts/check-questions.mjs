#!/usr/bin/env node
// Generates every lesson, letters lesson, unit practice, flashcard deck and a full review
// many times over and checks each question: the right answer is among the options, options
// are distinct, and grading the right answer passes. Also measures answer-length bias:
// in a fair multiple-choice set the right answer should not usually be the longest option.
// Run: node scripts/check-questions.mjs
import { readFileSync } from 'node:fs';
import { indexData, buildLesson, buildUnitPractice, buildLettersLesson, buildReview, deckFor, rightAnswer, isCorrect } from '../js/engine.js';

const load = (f) => JSON.parse(readFileSync(new URL(`../data/${f}`, import.meta.url), 'utf8'));
const db = indexData({ items: load('items.json').items, script: load('script.json'), sentences: load('sentences.json').sentences,
  course: load('course.json'), letters: load('letters.json') });

const errors = [];
const typeCount = {};
const longest = {}; // type -> [rightIsLongest, total]
const textOf = (q, o) => {
  switch (q.type) {
    case 'k2e': case 'readWord': case 'k2eSent': return o.en;
    case 'rom': return o.rom;
    case 'mark': return o.summary;
    default: return null;
  }
};
function checkQuestion(q, where) {
  typeCount[q.type] = (typeCount[q.type] || 0) + 1;
  if (q.type === 'intro') { if (!q.x) errors.push(`${where}: intro without content`); return; }
  if (q.type === 'match') { if (q.pairs.length < 3) errors.push(`${where}: match with ${q.pairs.length} pairs`); return; }
  if (q.type === 'build') {
    if (!isCorrect(q, q.words)) errors.push(`${where}: build does not accept its own words`);
    for (const w of q.words) if (!q.bank.includes(w)) errors.push(`${where}: build bank misses ${w.km}`);
    return;
  }
  const right = rightAnswer(q);
  if (q.type === 'series') { if (!isCorrect(q, right)) errors.push(`${where}: series grading`); return; }
  const ids = q.options.map((o) => o.id);
  if (!ids.includes(right)) errors.push(`${where}: ${q.type} right answer ${right} not among options`);
  if (new Set(ids).size !== ids.length) errors.push(`${where}: ${q.type} duplicate option ids`);
  if (q.options.length < 2) errors.push(`${where}: ${q.type} has ${q.options.length} option(s)`);
  if (!isCorrect(q, right)) errors.push(`${where}: ${q.type} does not accept its right answer`);
  if (q.type === 'syllable' || q.type === 'seriesPair') {
    const roms = q.options.map((o) => o.rom);
    if (q.type === 'syllable' && new Set(roms).size !== roms.length) errors.push(`${where}: syllable options repeat a reading`);
  }
  const texts = q.options.map((o) => textOf(q, o));
  if (texts.every((t) => typeof t === 'string')) {
    const rt = textOf(q, q.options.find((o) => o.id === right));
    const max = Math.max(...texts.map((t) => t.length));
    const isLongest = rt.length === max && texts.filter((t) => t.length === max).length === 1;
    const rec = (longest[q.type] ||= [0, 0]);
    rec[0] += isLongest ? 1 : 0; rec[1] += 1;
  }
}

const ROUNDS = 30;
for (let r = 0; r < ROUNDS; r++) {
  for (const unit of db.course.units) {
    for (const lesson of unit.lessons) {
      const qs = buildLesson(db, lesson, unit);
      if (!qs.length) errors.push(`lesson ${lesson.id}: no questions`);
      const introduced = new Set();
      for (const q of qs) {
        if (q.type === 'intro' && q.kind === 'item') introduced.add(q.x.id);
        if (['k2e', 'e2k', 'rom'].includes(q.type) && lesson.items.includes(q.item.id) && !introduced.has(q.item.id))
          errors.push(`lesson ${lesson.id}: ${q.item.id} tested before its intro card`);
        checkQuestion(q, `lesson ${lesson.id}`);
      }
    }
    buildUnitPractice(db, unit).forEach((q) => checkQuestion(q, `practice ${unit.id}`));
  }
  for (const g of db.letters.groups) {
    buildLettersLesson(db, g).forEach((q) => checkQuestion(q, `letters ${g.id}`));
    buildLettersLesson(db, g, { practiceOnly: true }).forEach((q) => { if (q.type === 'intro') errors.push(`letters practice ${g.id}: has an intro`); checkQuestion(q, `letters practice ${g.id}`); });
  }
}
const allKeys = [
  ...db.items.map((x) => `item:${x.id}`), ...db.sentences.map((x) => `sent:${x.id}`),
  ...db.script.consonants.map((x) => `cons:${x.id}`), ...db.script.vowels.map((x) => `vow:${x.id}`),
  ...db.script.combos.map((x) => `comb:${x.id}`), ...db.script.independents.map((x) => `ind:${x.id}`),
  ...db.script.marks.map((x) => `mark:${x.id}`), ...db.script.consonants.filter((c) => c.sub).map((x) => `sub:${x.id}`),
  ...db.script.digits.map((x) => `dig:${x.id}`),
];
const review = buildReview(db, allKeys);
if (review.length < allKeys.length) errors.push(`review built ${review.length} questions for ${allKeys.length} keys`);
review.forEach((q) => checkQuestion(q, 'review'));
for (const u of db.course.units) if (!deckFor(db, { kind: 'unit', id: u.id }).length) errors.push(`deck ${u.id} empty`);
for (const g of db.letters.groups) if (!deckFor(db, { kind: 'letters', id: g.id }).length) errors.push(`deck ${g.id} empty`);

console.log('question types generated:', Object.entries(typeCount).map(([k, v]) => `${k} ${v}`).join(', '));
console.log('right answer is the single longest option:');
for (const [t, [hit, n]] of Object.entries(longest)) {
  const pct = Math.round((hit / n) * 100);
  console.log(`  ${t}: ${pct}% of ${n} (chance is about 25%)`);
  if (n > 50 && pct > 40) errors.push(`${t}: right answer is the longest option ${pct}% of the time (length bias)`);
}
const uniq = [...new Set(errors)];
if (uniq.length) { console.error(uniq.slice(0, 40).map((e) => `✗ ${e}`).join('\n')); console.error(`${uniq.length} problem(s)`); process.exit(1); }
console.log('✓ questions OK');
