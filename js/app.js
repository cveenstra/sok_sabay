import { indexData, buildLesson, buildUnitPractice, buildLettersLesson, buildReview, deckFor, groupSymbols,
  readableChars, wordsReadableWith, isCorrect, rightAnswer, shuffle, syllable } from './engine.js';
import * as store from './storage.js';
import { startCloudSync, onCloudStatus, cloudStatus } from './cloud.js';
import { initSpeech, canSpeak, onVoiceChange, speak } from './speech.js';

const app = document.getElementById('app');
const ZWSP = '​'; // Khmer writes words together; zero-width space marks word breaks.
const DAILY_GOAL = 30;
const HEARTS = 5;
let db = null;
let state = store.load();

// ---------- tiny DOM helper ----------
function h(tag, attrs = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k === 'class') el.className = v;
    else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
    else if (k === 'html') el.innerHTML = v;
    else el.setAttribute(k, v === true ? '' : v);
  }
  for (const kid of kids.flat()) if (kid != null && kid !== false) el.append(kid.nodeType ? kid : document.createTextNode(kid));
  return el;
}
const km = (text, cls = '') => h('span', { class: `km ${cls}`, lang: 'km' }, text);
const rom = (text) => h('span', { class: 'rom' }, text);
const sentenceKm = (words) => words.map((w) => w.km).join(ZWSP);
const sentenceRom = (words) => words.map((w) => w.rom).join(' ');
const go = (hash) => { if (location.hash === hash) route(); else location.hash = hash; };
const pick = (a) => a[Math.floor(Math.random() * a.length)];

function speakBtn(text) {
  if (!canSpeak()) return null;
  return h('button', { class: 'speak', type: 'button', 'aria-label': 'Play Khmer audio', onclick: () => speak(text) }, '🔊');
}
function toast(msg) {
  const t = h('div', { class: 'toast', role: 'status' }, msg);
  document.body.append(t);
  setTimeout(() => t.remove(), 2000);
}

/** A Khmer sentence whose words can be tapped; the tapped word's reading and meaning show underneath. */
function tappableSentence(words, cls = 'big') {
  const wrap = h('div', { class: 'tap-wrap' });
  const line = h('div', { class: `tap-line ${cls}`, lang: 'km' });
  const gloss = h('p', { class: 'gloss-box', 'aria-live': 'polite' }, 'Tap a word for its meaning.');
  words.forEach((w) => {
    const b = h('button', { class: 'tap-word', type: 'button', 'aria-label': `${w.km}: ${w.rom}, ${w.en}` }, km(w.km));
    b.addEventListener('click', () => {
      line.querySelectorAll('.tap-word.open').forEach((x) => x.classList.remove('open'));
      b.classList.add('open');
      gloss.replaceChildren(km(w.km), ' ', h('b', {}, w.rom), ` = ${w.en}`);
      if (canSpeak()) speak(w.km);
    });
    line.append(b);
  });
  wrap.append(line, gloss);
  return wrap;
}

// ---------- chrome ----------
function refreshStats() {
  document.getElementById('stat-streak').textContent = store.currentStreak(state);
  document.getElementById('stat-xp').textContent = state.xp;
}
function renderCloud() {
  const el = document.getElementById('cloud');
  if (!el) return;
  const s = cloudStatus();
  const text = { off: '', connecting: 'Connecting…', synced: 'Saved to your account', saving: 'Saving…', error: 'Not saved yet, will retry' }[s];
  el.hidden = s === 'off';
  el.textContent = s === 'synced' || s === 'saving' ? '☁︎' : s === 'error' ? '⚠︎' : '…';
  el.title = text; el.setAttribute('aria-label', text);
  el.className = `cloud ${s}`;
}
function setTab(name) {
  document.querySelectorAll('.tabbar button').forEach((b) => b.classList.toggle('on', b.dataset.nav === name));
}
document.addEventListener('click', (e) => {
  const nav = e.target.closest('[data-nav]');
  if (!nav) return;
  go(nav.dataset.nav === 'home' ? '#/' : `#/${nav.dataset.nav}`);
});

// ---------- home / path ----------
function allLessons() { return db.course.units.flatMap((u) => u.lessons); }
function unitOf(lessonId) { return db.course.units.find((u) => u.lessons.some((l) => l.id === lessonId)); }
function isUnlocked(lessonId) {
  const list = allLessons();
  const i = list.findIndex((l) => l.id === lessonId);
  return i === 0 || !!state.done[list[i - 1].id] || !!state.done[lessonId];
}
const unitDone = (u) => u.lessons.every((l) => state.done[l.id]);

function goalRing() {
  const xp = state.today.date === store.today() ? state.today.xp : 0;
  const pct = Math.min(1, xp / DAILY_GOAL);
  const r = 24, c = 2 * Math.PI * r;
  return h('span', { class: 'goal', role: 'img', 'aria-label': `Daily goal: ${xp} of ${DAILY_GOAL} XP`,
    html: `<svg viewBox="0 0 58 58" width="58" height="58" aria-hidden="true">
      <circle cx="29" cy="29" r="${r}" fill="none" stroke="var(--line)" stroke-width="7"/>
      <circle cx="29" cy="29" r="${r}" fill="none" stroke="var(--saffron)" stroke-width="7" stroke-linecap="round"
        stroke-dasharray="${c}" stroke-dashoffset="${c * (1 - pct)}" transform="rotate(-90 29 29)"/>
      <text x="29" y="34" text-anchor="middle" font-family="Nunito, sans-serif" font-weight="900" font-size="14" fill="var(--ink)">${xp}</text></svg>` });
}

function viewHome() {
  setTab('home');
  const lessons = allLessons();
  const current = lessons.find((l) => !state.done[l.id]);
  const streak = store.currentStreak(state);
  const fresh = Object.keys(state.done).length === 0;
  app.replaceChildren(...[
    h('section', { class: 'hello' },
      goalRing(),
      h('div', {},
        h('h1', {}, km('សួស្តី!'), ' ', h('span', { class: 'rom hello-rom' }, 'suəsdəy, hello!')),
        h('p', {}, streak ? `${streak}-day streak. Daily goal ${DAILY_GOAL} XP.` : `Finish a lesson to start a streak. Daily goal ${DAILY_GOAL} XP.`))),
    fresh ? h('section', { class: 'welcome' },
      h('h2', {}, 'New to Khmer? Start here'),
      h('p', {}, 'Each lesson shows you three or four new words on cards first, then practises them. Stuck? Tap "Show answer" any time: it costs no heart, and the word comes back later in Review.'),
      h('div', { class: 'row-actions' },
        h('button', { class: 'btn', onclick: () => go(`#/lesson/${lessons[0].id}`) }, 'Start lesson 1'),
        h('button', { class: 'btn ghost', onclick: () => go('#/letters') }, 'Learn the letters'))) : null,
    ...db.course.units.map((u, ui) =>
      h('section', { class: `unit tone-${ui % 4}` },
        h('div', { class: 'unit-head' },
          h('div', {}, h('p', { class: 'eyebrow' }, `Unit ${ui + 1}`), h('h2', {}, u.title), h('p', {}, u.subtitle)),
          h('div', { class: 'unit-side' }, km(u.km, 'unit-km'),
            h('button', { class: 'chip-btn', onclick: () => go(`#/cards/unit/${u.id}`) }, 'Flashcards'))),
        h('div', { class: 'path' },
          ...u.lessons.map((l, li) => {
            const unlocked = isUnlocked(l.id);
            const done = !!state.done[l.id];
            return h('button', {
              class: `node ${done ? 'done' : ''} ${unlocked ? '' : 'locked'} ${current && current.id === l.id ? 'current' : ''}`,
              style: `--wiggle:${[0, 34, 52, 34, 0, -34, -52, -34][li % 8]}px`,
              'aria-label': `${l.title}${done ? ' (completed)' : unlocked ? '' : ' (locked)'}`,
              onclick: () => unlocked ? go(`#/lesson/${l.id}`) : toast('Finish the lesson before this one first'),
            }, h('span', { class: 'disc', 'aria-hidden': 'true' }, done ? '✓' : unlocked ? l.icon : '🔒'), h('span', { class: 'label' }, l.title));
          }),
          h('button', { class: `node practice ${unitDone(u) ? '' : 'locked'}`, 'aria-label': `${u.title} practice${unitDone(u) ? '' : ' (locked)'}`,
            onclick: () => unitDone(u) ? go(`#/practice/${u.id}`) : toast('Finish every lesson in this unit to unlock its practice') },
            h('span', { class: 'disc', 'aria-hidden': 'true' }, unitDone(u) ? '🏆' : '🔒'), h('span', { class: 'label' }, 'Unit practice')))))].filter(Boolean));
}

// ---------- lesson player ----------
function startSession({ title, questions, lessonId, isReview, tip, back = '#/' }) {
  document.body.classList.add('in-lesson');
  const s = { title, queue: questions.slice(), total: questions.length, done: 0, hearts: HEARTS, correct: 0, graded: 0,
    missed: new Set(), lessonId, isReview, tip, back, requeued: new Set() };
  nextQuestion(s);
}

function lessonChrome(s) {
  return h('div', { class: 'lesson-top' },
    h('button', { class: 'quit', 'aria-label': 'Quit lesson', onclick: () => { document.body.classList.remove('in-lesson'); go(s.back); } }, '✕'),
    h('div', { class: 'bar', role: 'progressbar', 'aria-valuemin': 0, 'aria-valuemax': s.total, 'aria-valuenow': s.done },
      h('i', { style: `width:${Math.round((s.done / s.total) * 100)}%` })),
    h('span', { class: 'hearts', 'aria-label': `${s.hearts} hearts left` }, `❤ ${s.hearts}`));
}

function nextQuestion(s) {
  if (s.hearts <= 0) return finish(s, false);
  const qn = s.queue.shift();
  if (!qn) return finish(s, true);
  if (qn.type === 'intro') return renderIntro(s, qn);
  renderQuestion(s, qn);
}

// New words and letters are met first on a card, before anything is tested.
function renderIntro(s, qn) {
  const card = introCard(qn.kind, qn.x);
  const cont = h('button', { class: 'btn wide', onclick: () => { s.done += 1; nextQuestion(s); } }, 'Got it');
  app.replaceChildren(h('div', { class: 'lesson' }, lessonChrome(s),
    s.done === 0 && s.tip ? h('p', { class: 'tip' }, s.tip) : null,
    card, h('div', { class: 'spacer' }), h('div', { class: 'check-row' }, cont)));
  app.focus();
  cont.focus();
  if (canSpeak() && (qn.kind === 'item')) speak(qn.x.km);
}

function introCard(kind, x) {
  const badge = (t) => h('span', { class: 'new-badge' }, t);
  const seriesTag = (c) => h('span', { class: `ser ${c.series}` }, `${c.series}-series`);
  switch (kind) {
    case 'item': return h('div', { class: 'card-intro' }, badge('New word'),
      h('div', { class: 'card-face' }, speakBtn(x.km), km(x.km, 'huge')),
      h('p', { class: 'card-rom' }, x.rom), h('p', { class: 'card-en' }, x.en),
      x.note ? h('p', { class: 'card-note' }, x.note) : null);
    case 'cons': return h('div', { class: 'card-intro' }, badge('New letter'),
      h('p', { class: 'letter-huge', lang: 'km' }, x.char),
      h('p', { class: 'card-en' }, `"${x.name}" `, rom(x.ipa_name)),
      h('p', { class: 'card-note' }, seriesTag(x), ' ', `Sound: ${x.ipa}. `, x.series === 'a'
        ? 'a-series letters carry the vowel â [ɑː] when nothing else is written.' : 'o-series letters carry the vowel ô [ɔː] when nothing else is written.'));
    case 'vow': return h('div', { class: 'card-intro' }, badge('New vowel sign'),
      h('p', { class: 'letter-huge', lang: 'km' }, x.char),
      h('div', { class: 'two-up' },
        h('div', {}, h('small', {}, 'after an a-series letter'), h('b', {}, x.rom_a), rom(x.ipa_a)),
        h('div', {}, h('small', {}, 'after an o-series letter'), h('b', {}, x.rom_o), rom(x.ipa_o))),
      h('p', { class: 'card-note' }, 'The dotted circle stands for the consonant. A vowel sign is always read after its consonant, wherever it is written.'));
    case 'comb': return h('div', { class: 'card-intro' }, badge('Vowel + mark'),
      h('p', { class: 'letter-huge', lang: 'km' }, x.char),
      h('div', { class: 'two-up' },
        h('div', {}, h('small', {}, 'after an a-series letter'), h('b', {}, x.rom_a), rom(x.ipa_a)),
        h('div', {}, h('small', {}, 'after an o-series letter'), h('b', {}, x.rom_o), rom(x.ipa_o))),
      h('p', { class: 'card-note' }, x.note));
    case 'ind': return h('div', { class: 'card-intro' }, badge('Independent vowel'),
      h('p', { class: 'letter-huge', lang: 'km' }, x.chars.join(' ')),
      h('p', { class: 'card-en' }, h('b', {}, x.rom), ' ', rom(x.ipa)),
      h('p', { class: 'card-note' }, 'Written on its own, without a consonant. It already includes the sound before the vowel.'),
      x.example ? h('p', { class: 'card-note' }, 'In a word: ', km(x.example.km), ' ', rom(x.example.rom), ` "${x.example.en}"`) : null);
    case 'mark': return h('div', { class: 'card-intro' }, badge('New mark'),
      h('p', { class: 'letter-huge', lang: 'km' }, x.shown),
      h('p', { class: 'card-en' }, km(x.name_km), ' ', rom(x.name_rom)),
      h('p', { class: 'card-note' }, x.summary));
    case 'sub': return h('div', { class: 'card-intro' }, badge('Subscript'),
      h('div', { class: 'two-up' },
        h('div', {}, h('small', {}, 'letter'), km(x.char, 'mid')),
        h('div', {}, h('small', {}, 'its foot (subscript)'), km(x.sub, 'mid'))),
      h('p', { class: 'card-note' }, `In a cluster like ${x.cluster ? '' : 'this'}`, x.cluster ? km(x.cluster.km) : '',
        x.cluster ? ` (${x.cluster.rom}, "${x.cluster.en}")` : '',
        ', the second consonant is written small under the first, with no vowel between them.'));
    case 'dig': return h('div', { class: 'card-intro' }, badge('New number'),
      h('p', { class: 'letter-huge', lang: 'km' }, x.char),
      h('p', { class: 'card-en' }, String(x.value)),
      x.word ? h('p', { class: 'card-note' }, km(x.word), ' ', rom(x.word_rom)) : null);
    default: return h('div');
  }
}

function renderQuestion(s, qn) {
  let answer = null;
  let settled = false;
  const checkBtn = h('button', { class: 'btn wide', disabled: true }, 'Check');
  const setAnswer = (a, ready = true) => { answer = a; checkBtn.disabled = !ready; };
  const body = questionBody(qn, setAnswer, () => grade());
  const peek = h('button', { class: 'peek', type: 'button', onclick: () => reveal() }, 'Show answer');
  const row = h('div', { class: 'check-row' }, checkBtn);

  function settle(ok, peeked) {
    settled = true;
    if (qn.key) store.grade(state, qn.key, ok);
    s.graded += 1;
    if (ok) s.correct += 1;
    else {
      if (!peeked) s.hearts -= 1;
      if (qn.key) s.missed.add(qn.key);
      if (!s.requeued.has(qn) && qn.type !== 'match') { s.requeued.add(qn); s.queue.push(qn); s.total += 1; }
    }
    s.done += 1;
    store.save(state);
    body.querySelectorAll('button.choice, button.word, button.tile').forEach((b) => { b.disabled = true; });
    peek.remove();
    const cont = h('button', { class: `btn wide ${ok ? 'ok-btn' : ''}`, onclick: () => nextQuestion(s) }, 'Continue');
    row.replaceChildren(feedback(qn, ok, peeked), cont);
    row.hidden = false;
    cont.focus();
  }
  function grade() {
    if (settled) return;
    const ok = isCorrect(qn, answer);
    markChoices(body, qn, answer);
    settle(ok, false);
  }
  // Peeking flips to the answer: no heart lost, but it counts as a miss for Review.
  function reveal() {
    if (settled) return;
    markChoices(body, qn, null);
    if (qn.type === 'build') fillBuild(body, qn);
    if (qn.type === 'match') body.querySelectorAll('.tile').forEach((b) => b.classList.add('ok'));
    settle(false, true);
  }
  checkBtn.addEventListener('click', grade);
  app.replaceChildren(h('div', { class: 'lesson' }, lessonChrome(s), s.done === 0 && s.tip ? h('p', { class: 'tip' }, s.tip) : null,
    body, h('div', { class: 'peek-row' }, peek), h('div', { class: 'spacer' }), row));
  if (qn.type === 'match') row.hidden = true;
  app.focus();
}

function markChoices(body, qn, answer) {
  const right = rightAnswer(qn);
  body.querySelectorAll('button.choice').forEach((b) => {
    const id = b.dataset.id;
    if (id === right) b.classList.add('right');
    else if (id === answer) b.classList.add('wrong');
    else if (qn.type !== 'series' && qn.type !== 'seriesPair') b.classList.add('faded');
  });
}

function fillBuild(body, qn) {
  const line = body.querySelector('.answer-line');
  line.replaceChildren(...qn.words.map((w) => h('span', { class: 'word shown' }, km(w.km), h('small', {}, w.rom))));
}

function feedback(qn, ok, peeked) {
  const title = peeked ? 'Here’s the answer' : ok ? pick(['Nice!', 'Correct!', 'Great job!', 'ល្អណាស់! Very good!']) : 'Not quite';
  const sheet = h('div', { class: `sheet ${ok ? 'ok' : peeked ? 'peeked' : 'no'}`, role: 'status' }, h('h3', {}, title));
  const line = (...k) => h('p', {}, ...k);
  switch (qn.type) {
    case 'k2e': case 'e2k': case 'rom': case 'readWord':
      sheet.append(line(km(qn.item.km), ' ', rom(qn.item.rom), ` = ${qn.item.en}`));
      if (qn.item.note) sheet.append(line(h('small', {}, qn.item.note)));
      break;
    case 'build': case 'k2eSent':
      sheet.append(line(km(sentenceKm(qn.words))), line(rom(sentenceRom(qn.words))), line(qn.sentence.en));
      break;
    case 'letterSound': case 'letterPick': case 'series':
      sheet.append(line(km(qn.letter.char), ` is "${qn.letter.name}" ${qn.letter.ipa_name}, an ${qn.letter.series}-series consonant.`));
      break;
    case 'sub':
      sheet.append(line(km(qn.letter.sub), ' is the subscript form of ', km(qn.letter.char), ` "${qn.letter.name}".`));
      break;
    case 'vowel': case 'vowelPick':
      sheet.append(line(km(qn.vowel.char), ` reads ${qn.vowel.rom_a} ${qn.vowel.ipa_a} after an a-series letter, ${qn.vowel.rom_o} ${qn.vowel.ipa_o} after an o-series one.`));
      break;
    case 'syllable':
      sheet.append(line(km(qn.syl.km), ` = ${qn.syl.rom} ${qn.syl.ipa}: `, km(qn.syl.c.char), ` is ${qn.syl.c.series}-series, so `, km(qn.syl.v.char),
        ` reads ${qn.syl.c.series === 'a' ? qn.syl.v.rom_a : qn.syl.v.rom_o}.`));
      break;
    case 'seriesPair':
      sheet.append(line(km(qn.target.km), ` reads ${qn.target.rom} ${qn.target.ipa}, because `, km(qn.target.c.char), ` is ${qn.target.c.series}-series.`));
      break;
    case 'combo':
      sheet.append(line(km(qn.combo.char), ` reads ${qn.combo.rom_a} ${qn.combo.ipa_a} after an a-series letter, ${qn.combo.rom_o} ${qn.combo.ipa_o} after an o-series one.`));
      break;
    case 'indep': case 'indepPick':
      sheet.append(line(km(qn.indep.chars.join(' ')), ` reads ${qn.indep.rom} ${qn.indep.ipa}.`));
      break;
    case 'mark':
      sheet.append(line(km(qn.mark.shown), ' ', km(qn.mark.name_km), ` ${qn.mark.name_rom}: ${qn.mark.summary}`));
      break;
    case 'digit':
      sheet.append(line(km(qn.digit.char), ` is ${qn.digit.value}`, qn.digit.word ? [' (', km(qn.digit.word), ' ', rom(qn.digit.word_rom), ')'] : ''));
      break;
    case 'match':
      sheet.append(line(ok ? 'All pairs matched.' : 'These words come back in Review.'));
      break;
  }
  return sheet;
}

function choiceList(options, render, setAnswer, cls = '') {
  const list = h('div', { class: `choices ${cls}` });
  options.forEach((opt, i) => {
    const id = opt.id ?? opt;
    const b = h('button', { class: 'choice', 'data-id': id, onclick: () => {
      list.querySelectorAll('.choice').forEach((x) => x.classList.remove('sel'));
      b.classList.add('sel');
      setAnswer(id);
    } }, render(opt, i));
    list.append(b);
  });
  return list;
}

function questionBody(qn, setAnswer, autoGrade) {
  const wrap = h('div', { class: 'qbody' });
  const label = (t) => h('h2', { class: 'prompt-label' }, t);
  const bigLetter = (t) => h('p', { class: 'letter-big', lang: 'km' }, t);
  switch (qn.type) {
    case 'k2e':
      wrap.append(label('What does this mean?'),
        h('div', { class: 'prompt' }, speakBtn(qn.item.km), km(qn.item.km, 'big'), rom(qn.item.rom)),
        choiceList(qn.options, (o) => o.en, setAnswer));
      break;
    case 'readWord':
      wrap.append(label('Read this word. What does it mean?'),
        h('div', { class: 'prompt' }, speakBtn(qn.item.km), km(qn.item.km, 'big')),
        h('p', { class: 'lead center' }, 'Every letter in it is one you have learned.'),
        choiceList(qn.options, (o) => o.en, setAnswer));
      break;
    case 'e2k':
      wrap.append(label('Pick the Khmer'),
        h('div', { class: 'prompt' }, h('span', { class: 'en-big' }, qn.item.en)),
        choiceList(qn.options, (o) => [km(o.km)], setAnswer, qn.options.every((o) => o.km.length < 9) ? 'two' : ''));
      break;
    case 'rom':
      wrap.append(label('How is this read?'),
        h('div', { class: 'prompt' }, speakBtn(qn.item.km), km(qn.item.km, 'big'), h('span', { class: 'rom' }, `(${qn.item.en})`)),
        choiceList(qn.options, (o) => o.rom, setAnswer));
      break;
    case 'k2eSent':
      wrap.append(label('What does this sentence mean?'),
        h('p', { class: 'lead' }, 'Tap any word to see what it means.'),
        tappableSentence(qn.words),
        choiceList(qn.options, (o) => o.en, setAnswer));
      break;
    case 'letterSound':
      wrap.append(label('What is this letter called?'), bigLetter(qn.letter.char),
        choiceList(qn.options, (o) => [h('b', {}, o.name), ' ', h('span', { class: 'rom' }, o.ipa_name)], setAnswer, 'two'));
      break;
    case 'letterPick':
      wrap.append(label(`Which letter is "${qn.letter.name}" ${qn.letter.ipa_name}?`),
        choiceList(qn.options, (o) => [km(o.char, 'glyph')], setAnswer, 'two glyphs'));
      break;
    case 'series':
      wrap.append(label('Which series is this consonant?'), bigLetter(qn.letter.char),
        choiceList(['a', 'o'], (o) => [h('b', {}, `${o}-series`), ' ', h('span', { class: 'rom' }, o === 'a' ? 'inherent vowel â [ɑː]' : 'inherent vowel ô [ɔː]')], setAnswer, 'two'));
      break;
    case 'vowel':
      wrap.append(label('How does this vowel read after an a-series letter?'), bigLetter(qn.vowel.example),
        h('p', { class: 'lead center' }, 'Shown on អ, an a-series consonant.'),
        choiceList(qn.options, (o) => [h('b', {}, o.rom_a), ' ', h('span', { class: 'rom' }, o.ipa_a)], setAnswer, 'two'));
      break;
    case 'vowelPick':
      wrap.append(label(`Which vowel sign reads "${qn.vowel.rom_a}" ${qn.vowel.ipa_a} after an a-series letter?`),
        choiceList(qn.options, (o) => [km(o.char, 'glyph')], setAnswer, 'two glyphs'));
      break;
    case 'syllable':
      wrap.append(label('How is this syllable read?'), bigLetter(qn.syl.km),
        h('p', { class: 'lead center' }, km(qn.syl.c.char), ` is ${qn.syl.c.series}-series.`),
        choiceList(qn.options, (o) => [h('b', {}, o.rom), ' ', h('span', { class: 'rom' }, o.ipa)], setAnswer, 'two'));
      break;
    case 'seriesPair':
      wrap.append(label(`Which one reads "${qn.target.rom}" ${qn.target.ipa}?`),
        h('p', { class: 'lead' }, 'Same vowel sign, different consonant series. The series changes the vowel.'),
        choiceList(qn.options, (o) => [km(o.km, 'glyph')], setAnswer, 'two glyphs'));
      break;
    case 'combo':
      wrap.append(label('How does this read after an a-series letter?'), bigLetter(qn.combo.char),
        choiceList(qn.options, (o) => [h('b', {}, o.rom_a), ' ', h('span', { class: 'rom' }, o.ipa_a)], setAnswer, 'two'));
      break;
    case 'indep':
      wrap.append(label('How is this vowel read?'), bigLetter(qn.indep.chars.join(' ')),
        choiceList(qn.options, (o) => [h('b', {}, o.rom), ' ', h('span', { class: 'rom' }, o.ipa)], setAnswer, 'two'));
      break;
    case 'indepPick':
      wrap.append(label(`Which independent vowel reads "${qn.indep.rom}" ${qn.indep.ipa}?`),
        choiceList(qn.options, (o) => [km(o.chars[0], 'glyph')], setAnswer, 'two glyphs'));
      break;
    case 'mark':
      wrap.append(label('What does this mark do?'), bigLetter(qn.mark.shown),
        choiceList(qn.options, (o) => o.summary, setAnswer));
      break;
    case 'sub':
      wrap.append(label('This subscript is the foot of which letter?'), bigLetter(qn.letter.sub),
        choiceList(qn.options, (o) => [km(o.char, 'glyph'), ' ', h('span', { class: 'rom' }, o.name)], setAnswer, 'two'));
      break;
    case 'digit':
      wrap.append(label('Which number is this?'), bigLetter(qn.digit.char),
        choiceList(qn.options, (o) => h('b', { class: 'num' }, String(o.value)), setAnswer, 'two'));
      break;
    case 'build':
      wrap.append(...buildSentence(qn, setAnswer));
      break;
    case 'match':
      wrap.append(...matchPairs(qn, autoGrade, setAnswer));
      break;
  }
  return wrap;
}

function buildSentence(qn, setAnswer) {
  const line = h('div', { class: 'answer-line', 'aria-label': 'Your answer' });
  const bank = h('div', { class: 'bank' });
  const chosen = [];
  const sync = () => setAnswer(chosen.map((c) => c.word), chosen.length > 0);
  const tile = (w, onclick) => h('button', { class: 'word', onclick }, km(w.km), h('small', {}, w.rom), h('small', { class: 'hint-en' }, w.en));
  qn.bank.forEach((w) => {
    const tileIn = tile(w, () => {
      if (tileIn.classList.contains('used')) return;
      tileIn.classList.add('used');
      const tileOut = tile(w, () => {
        tileOut.remove(); tileIn.classList.remove('used');
        chosen.splice(chosen.findIndex((c) => c.el === tileOut), 1); sync();
      });
      chosen.push({ word: w, el: tileOut }); line.append(tileOut); sync();
      if (canSpeak()) speak(w.km);
    });
    bank.append(tileIn);
  });
  const hintBtn = h('button', { class: 'peek', type: 'button', 'aria-pressed': 'false', onclick: () => {
    const on = bank.classList.toggle('hints');
    line.classList.toggle('hints', on);
    hintBtn.setAttribute('aria-pressed', String(on));
    hintBtn.textContent = on ? 'Hide word meanings' : 'Show word meanings';
  } }, 'Show word meanings');
  return [h('h2', { class: 'prompt-label' }, 'Write this in Khmer'),
    h('div', { class: 'prompt' }, h('span', { class: 'en-big' }, qn.sentence.en)), line, bank, h('div', { class: 'hint-row' }, hintBtn)];
}

function matchPairs(qn, autoGrade, setAnswer) {
  let selected = null; let left = qn.pairs.length; let mistakes = 0;
  const leftCol = h('div', { class: 'col' }); const rightCol = h('div', { class: 'col' });
  const onPick = (btn, side, it) => {
    if (btn.classList.contains('ok')) return;
    if (!selected || selected.side === side) {
      if (selected) selected.btn.classList.remove('sel');
      selected = { btn, side, it }; btn.classList.add('sel'); return;
    }
    if (selected.it.id === it.id) {
      [btn, selected.btn].forEach((b) => { b.classList.remove('sel'); b.classList.add('ok'); b.disabled = true; });
      if (side === 'km' && canSpeak()) speak(it.km);
      left -= 1;
    } else {
      mistakes += 1;
      [btn, selected.btn].forEach((b) => { b.classList.remove('sel'); b.classList.add('miss'); setTimeout(() => b.classList.remove('miss'), 450); });
      store.grade(state, `item:${it.id}`, false); store.grade(state, `item:${selected.it.id}`, false);
    }
    selected = null;
    if (left === 0) { setAnswer(mistakes === 0); setTimeout(() => autoGrade(), 250); }
  };
  shuffle(qn.pairs).forEach((it) => { const b = h('button', { class: 'tile', onclick: () => onPick(b, 'km', it) }, km(it.km)); leftCol.append(b); });
  shuffle(qn.pairs).forEach((it) => { const b = h('button', { class: 'tile', onclick: () => onPick(b, 'en', it) }, it.en); rightCol.append(b); });
  return [h('h2', { class: 'prompt-label' }, 'Match the pairs'), h('div', { class: 'match' }, leftCol, rightCol)];
}

function finish(s, completed) {
  document.body.classList.remove('in-lesson');
  const accuracy = s.graded ? Math.round((s.correct / s.graded) * 100) : 100;
  let xp = 0;
  if (completed) {
    xp = (s.isReview ? 5 : 10) + Math.min(s.correct, 15);
    store.recordLesson(state, { lessonId: s.isReview ? null : s.lessonId, xp });
  } else store.save(state);
  refreshStats();
  app.replaceChildren(h('section', { class: 'results' },
    h('div', { class: 'burst', 'aria-hidden': 'true' }, completed ? '🪷' : '💔'),
    h('h1', {}, completed ? (s.isReview ? 'Practice done!' : 'Lesson complete!') : 'Out of hearts'),
    h('p', { class: 'lead' }, completed ? s.title : 'Missed words are saved for Review. Try the lesson again, and use "Show answer" when you are stuck.'),
    h('div', { class: 'result-grid' },
      h('div', { class: 'card' }, h('b', {}, `+${xp}`), h('span', {}, 'XP')),
      h('div', { class: 'card' }, h('b', {}, `${accuracy}%`), h('span', {}, 'Accuracy')),
      h('div', { class: 'card' }, h('b', {}, store.currentStreak(state)), h('span', {}, 'Day streak'))),
    h('div', { class: 'row-actions center' },
      completed ? null : h('button', { class: 'btn', onclick: () => route() }, 'Try again'),
      h('button', { class: `btn ${completed ? '' : 'ghost'}`, onclick: () => go(s.back) }, 'Continue'))));
}

// ---------- letters ----------
const KIND_LABEL = { cons: 'consonants', vow: 'vowel signs', comb: 'vowel + mark', ind: 'independent vowels', mark: 'marks', sub: 'subscripts', dig: 'numerals' };
function symbolGlyph(s) {
  if (s.kind === 'ind') return s.sym.chars[0];
  if (s.kind === 'mark') return s.sym.shown;
  if (s.kind === 'sub') return s.sym.sub;
  return s.sym.char;
}
function meter(n) {
  return h('span', { class: 'meter', role: 'img', 'aria-label': `strength ${n} of 5` }, ...[1, 2, 3, 4, 5].map((i) => h('i', { class: i <= n ? 'on' : '' })));
}
function viewLetters() {
  setTab('letters');
  const groups = db.letters.groups;
  const next = groups.find((g) => !state.done[`L:${g.id}`]);
  // count only letter sets actually finished
  const chars = new Set();
  groups.forEach((g, i) => { if (state.done[`L:${g.id}`]) { const prev = i ? readableChars(db, i - 1) : new Set(); readableChars(db, i).forEach((c) => { if (!prev.has(c)) chars.add(c); }); } });
  const canRead = chars.size ? wordsReadableWith(db, chars).length : 0;
  app.replaceChildren(h('section', {},
    h('h1', { class: 'section-title' }, 'Letters'),
    h('p', { class: 'lead' }, 'Learn to read Khmer script a few symbols at a time: consonants by series, then vowel signs, then the rarer pieces. Each set ends with real words you can already read.'),
    h('div', { class: 'read-meter' }, h('b', {}, canRead), ` of ${db.items.length} course words use only letters you have learned.`),
    ...db.letters.sections.map((sec) => h('div', { class: 'letter-section' },
      h('h2', { class: 'sub-title' }, sec.title), sec.note ? h('p', { class: 'lead small' }, sec.note) : null,
      ...sec.groups.map((gid) => {
        const g = db.group[gid];
        const syms = groupSymbols(db, g);
        const done = !!state.done[`L:${g.id}`];
        const avg = syms.length ? syms.reduce((a, s) => a + store.strength(state, s.key), 0) / syms.length : 0;
        return h('article', { class: `lgroup ${done ? 'done' : ''} ${next && next.id === g.id ? 'next' : ''}` },
          h('div', { class: 'lgroup-head' },
            h('div', {}, h('h3', { lang: 'km' }, g.title), h('p', { class: 'small muted' }, `${syms.length} ${KIND_LABEL[syms[0]?.kind] || 'symbols'}${done ? ' · learned' : ''}`)),
            meter(Math.round(avg))),
          h('div', { class: 'glyph-row' }, ...syms.map((s) => h('span', { class: 'glyph-chip', title: `strength ${store.strength(state, s.key)} of 5` },
            km(symbolGlyph(s)), h('i', { class: 'bar5', style: `--n:${store.strength(state, s.key)}` })))),
          h('div', { class: 'row-actions' },
            h('button', { class: `btn ${done ? 'ghost' : ''}`, onclick: () => go(`#/learn-letters/${g.id}`) }, done ? 'Learn again' : 'Learn'),
            done ? h('button', { class: 'btn', onclick: () => go(`#/practice-letters/${g.id}`) }, 'Practice') : null,
            h('button', { class: 'chip-btn', onclick: () => go(`#/cards/letters/${g.id}`) }, 'Flashcards')));
      }))),
    h('h2', { class: 'section-title' }, 'Script chart'),
    scriptChart()));
}

function scriptChart() {
  const { consonants, vowels, digits, independents, marks, combos } = db.script;
  return h('div', { class: 'chart' },
    h('p', { class: 'lead' }, 'Khmer is written left to right, usually without spaces between words. Every consonant carries an inherent vowel: a-series letters read with â [ɑː], o-series letters with ô [ɔː], and the series also changes how each vowel sign is read.'),
    h('h3', { class: 'sub-title' }, `Consonants (${consonants.length})`),
    h('div', { class: 'legend' }, h('span', { class: 'ser a' }, 'a-series'), h('span', { class: 'ser o' }, 'o-series')),
    h('div', { class: 'grid-letters' }, ...consonants.map((c) => h('div', { class: 'lt' },
      h('span', { class: 'km', lang: 'km' }, c.char), h('span', { class: 'km subform', lang: 'km' }, c.sub || ''), h('small', {}, c.name), h('span', { class: `ser ${c.series}` }, c.series)))),
    h('h3', { class: 'sub-title' }, 'Dependent vowels'),
    h('div', { class: 'table-wrap' }, h('table', { class: 'vtab' },
      h('thead', {}, h('tr', {}, h('th', {}, 'Vowel'), h('th', {}, 'a-series'), h('th', {}, 'o-series'))),
      h('tbody', {}, ...[...vowels, ...combos].map((v) => h('tr', {}, h('td', { class: 'km', lang: 'km' }, v.example || v.char), h('td', {}, `${v.rom_a} ${v.ipa_a}`), h('td', {}, `${v.rom_o} ${v.ipa_o}`)))))),
    h('h3', { class: 'sub-title' }, 'Independent vowels'),
    h('div', { class: 'grid-letters' }, ...independents.map((v) => h('div', { class: 'lt' }, h('span', { class: 'km', lang: 'km' }, v.chars.join(' ')), h('small', {}, `${v.rom} ${v.ipa}`)))),
    h('h3', { class: 'sub-title' }, 'Marks'),
    h('div', { class: 'table-wrap' }, h('table', { class: 'vtab' }, h('tbody', {}, ...marks.map((m) => h('tr', {},
      h('td', { class: 'km', lang: 'km' }, m.shown), h('td', {}, h('b', {}, m.name_rom), h('br'), m.summary)))))),
    h('h3', { class: 'sub-title' }, 'Numerals'),
    h('div', { class: 'grid-letters' }, ...digits.map((d) => h('div', { class: 'lt' },
      h('span', { class: 'km', lang: 'km' }, d.char), h('small', {}, String(d.value)), d.word ? h('small', { lang: 'km', class: 'km' }, d.word) : null))));
}

// ---------- flashcards ----------
function viewCards() {
  setTab('cards');
  const deckRow = (kind, id, title, sub, n) => h('button', { class: 'deck', onclick: () => go(`#/cards/${kind}/${id}`) },
    h('span', { class: 'deck-title' }, title), h('span', { class: 'small muted' }, `${sub} · ${n} cards`));
  app.replaceChildren(h('section', {},
    h('h1', { class: 'section-title' }, 'Flashcards'),
    h('p', { class: 'lead' }, 'Flip a card to see the answer, then say whether you knew it. Cards you miss come back first in Review.'),
    h('h2', { class: 'sub-title' }, 'Words'),
    h('div', { class: 'decks' }, ...db.course.units.map((u, i) => deckRow('unit', u.id, u.title, `Unit ${i + 1}`, deckFor(db, { kind: 'unit', id: u.id }).length))),
    h('h2', { class: 'sub-title' }, 'Letters'),
    h('div', { class: 'decks' }, ...db.letters.groups.map((g) => deckRow('letters', g.id, g.title, 'Letters', groupSymbols(db, g).length)))));
}

function cardBack(c) {
  const x = c.x;
  switch (c.kind) {
    case 'item': return [h('p', { class: 'card-rom' }, x.rom), h('p', { class: 'card-en' }, x.en), x.note ? h('p', { class: 'card-note' }, x.note) : null];
    case 'cons': return [h('p', { class: 'card-en' }, `"${x.name}" `, rom(x.ipa_name)), h('p', { class: 'card-note' }, `${x.series}-series · sound ${x.ipa}`)];
    case 'vow': case 'comb': return [h('p', { class: 'card-en' }, `${x.rom_a} ${x.ipa_a}`), h('p', { class: 'card-note' }, `after o-series: ${x.rom_o} ${x.ipa_o}`)];
    case 'ind': return [h('p', { class: 'card-en' }, `${x.rom} ${x.ipa}`)];
    case 'mark': return [h('p', { class: 'card-en' }, x.name_rom), h('p', { class: 'card-note' }, x.summary)];
    case 'sub': return [h('p', { class: 'card-en' }, 'foot of ', km(x.char), ` "${x.name}"`)];
    case 'dig': return [h('p', { class: 'card-en' }, String(x.value)), x.word ? h('p', { class: 'card-note' }, km(x.word), ' ', rom(x.word_rom)) : null];
    default: return [];
  }
}
function cardFront(c) {
  const x = c.x;
  if (c.kind === 'item') return h('div', { class: 'card-face' }, speakBtn(x.km), km(x.km, 'huge'));
  const glyph = c.kind === 'ind' ? x.chars.join(' ') : c.kind === 'mark' ? x.shown : c.kind === 'sub' ? x.sub : c.kind === 'vow' ? x.char : x.char;
  return h('p', { class: 'letter-huge', lang: 'km' }, glyph);
}

function startCards(title, cards, back) {
  document.body.classList.add('in-lesson');
  const queue = shuffle(cards);
  const total = queue.length;
  let known = 0; let seen = 0;
  const again = new Set();
  const show = () => {
    const c = queue.shift();
    if (!c) {
      document.body.classList.remove('in-lesson');
      const xp = Math.max(1, Math.round(known / 2));
      store.recordLesson(state, { lessonId: null, xp });
      refreshStats();
      app.replaceChildren(h('section', { class: 'results' }, h('div', { class: 'burst', 'aria-hidden': 'true' }, '🃏'),
        h('h1', {}, 'Deck done!'), h('p', { class: 'lead' }, `${title}: you knew ${known} of ${total} on the first try.`),
        h('div', { class: 'result-grid' }, h('div', { class: 'card' }, h('b', {}, `+${xp}`), h('span', {}, 'XP')),
          h('div', { class: 'card' }, h('b', {}, known), h('span', {}, 'Knew')), h('div', { class: 'card' }, h('b', {}, again.size), h('span', {}, 'To review'))),
        h('div', { class: 'row-actions center' }, h('button', { class: 'btn', onclick: () => go(back) }, 'Continue'))));
      return;
    }
    const back$ = h('div', { class: 'card-back', hidden: true }, ...cardBack(c));
    const flipBtn = h('button', { class: 'btn wide', onclick: () => flip() }, 'Flip');
    const row = h('div', { class: 'check-row' }, flipBtn);
    const cardEl = h('button', { class: 'flashcard', type: 'button', 'aria-label': 'Flip card', onclick: () => flip() }, cardFront(c), back$);
    function flip() {
      if (!back$.hidden) return;
      back$.hidden = false; cardEl.classList.add('flipped');
      if (c.kind === 'item' && canSpeak()) speak(c.x.km);
      row.replaceChildren(
        h('button', { class: 'btn ghost', onclick: () => answer(false) }, 'Again'),
        h('button', { class: 'btn ok-btn', onclick: () => answer(true) }, 'Got it'));
    }
    function answer(ok) {
      seen += 1;
      store.grade(state, c.key, ok);
      store.save(state);
      if (ok && !again.has(c.key)) known += 1;
      if (!ok) { again.add(c.key); queue.push(c); }
      show();
    }
    app.replaceChildren(h('div', { class: 'lesson' },
      h('div', { class: 'lesson-top' },
        h('button', { class: 'quit', 'aria-label': 'Close deck', onclick: () => { document.body.classList.remove('in-lesson'); go(back); } }, '✕'),
        h('div', { class: 'bar' }, h('i', { style: `width:${Math.round((Math.min(seen, total) / total) * 100)}%` })),
        h('span', { class: 'hearts' }, `${Math.min(seen, total)}/${total}`)),
      h('p', { class: 'lead center' }, title), cardEl, h('p', { class: 'small muted center' }, 'Tap the card to flip it.'), h('div', { class: 'spacer' }), row));
    app.focus();
  };
  show();
}

// ---------- review ----------
function viewReview() {
  setTab('review');
  const due = store.dueKeys(state, 14);
  const seen = Object.keys(state.srs).length;
  if (!due.length) {
    app.replaceChildren(h('div', { class: 'review-empty' },
      h('div', { class: 'burst', 'aria-hidden': 'true' }, '🔁'),
      h('h1', { class: 'section-title' }, seen ? 'Nothing due right now' : 'Review unlocks as you learn'),
      h('p', {}, seen ? 'Words and letters you miss, or peek at, come back here first. Everything else returns 1, 3, 7 and 16 days after you get it right.' : 'Finish a lesson and the words you meet will be scheduled for review.'),
      h('button', { class: 'btn', onclick: () => go('#/') }, 'Back to lessons')));
    return;
  }
  app.replaceChildren(h('section', {},
    h('h1', { class: 'section-title' }, 'Review'),
    h('p', { class: 'lead' }, `${due.length} card${due.length === 1 ? '' : 's'} due. Missed ones come first.`),
    h('button', { class: 'btn wide', onclick: () => startSession({ title: 'Review', questions: buildReview(db, due), isReview: true, back: '#/review' }) }, 'Start review')));
}

// ---------- about ----------
function viewAbout() {
  setTab('about');
  const counts = { items: db.items.length, sentences: db.sentences.length, lessons: allLessons().length, units: db.course.units.length, groups: db.letters.groups.length };
  const synced = cloudStatus() !== 'off';
  const sec = h('section', { class: 'prose' });
  sec.innerHTML = `
    <h1 class="section-title">About Sok Sabay</h1>
    <p><span class="km" lang="km">សុខសប្បាយ</span> <i>sok sapbaay</i> means "well and happy". It is how Cambodians ask and answer "How are you?". This is a free, bite-sized course in Khmer, the national language of Cambodia: ${counts.units} units and ${counts.lessons} lessons with ${counts.items} words and phrases and ${counts.sentences} sentences, plus ${counts.groups} sets of letters.</p>
    <h2>How it works</h2>
    <ul>
      <li>Every new word or letter appears first on a card. Then it is practised several ways, a few at a time.</li>
      <li><b>Show answer</b> flips any question to its answer. It costs no heart; the word just comes back later in Review.</li>
      <li>In sentences, tap a Khmer word to see its reading and meaning.</li>
      <li><b>Flashcards</b> drill any unit or set of letters. <b>Review</b> brings back what you missed, then each card again after 1, 3, 7 and 16 days.</li>
    </ul>
    <h2>Romanisation</h2>
    <ul>
      <li><b>Words, phrases and sentences</b> use Wiktionary's <i>WT romanisation</i>, which follows the standard Phnom Penh pronunciation. <code>ɑ</code> as in "father", <code>ə</code> a short "uh", <code>ɨ</code> like "uh" with spread lips, <code>ɔ</code> as in "law", <code>ʼ</code> a glottal stop, <code>ñ</code> like "ny" in "canyon". Doubled vowels are long.</li>
      <li><b>Letters, vowel signs and syllables</b> use the UN's <i>UNGEGN</i> transliteration with IPA, from Wikipedia's Khmer script article. Syllables in the Letters lessons are read by the spelling rule (consonant plus the vowel's a- or o-series value), so they show how the script works rather than every irregular word.</li>
    </ul>
    <h2>Politeness and address</h2>
    <p>Khmer uses family words as "you" and "I". <span class="km" lang="km">បង</span> <i>bɑɑng</i> is for someone a little older, <span class="km" lang="km">ប្អូន</span> <i>pʼoun</i> for someone younger, <span class="km" lang="km">លោក</span> <i>look</i> for a man you address respectfully. Men answer "yes" with <span class="km" lang="km">បាទ</span> <i>baat</i>, women with <span class="km" lang="km">ចាស</span> <i>caah</i>. Greetings are often made with the <span class="km" lang="km">សំពះ</span> <i>sɑmpĕəh</i>: palms pressed together in front of the chest.</p>
    <h2>Audio</h2>
    <p>${canSpeak() ? 'Your browser has a Khmer voice, so 🔊 buttons read words aloud. It is a synthetic voice: treat it as a guide, not a native speaker.' : 'Your browser has no Khmer text-to-speech voice, so audio is off. On phones you can often add a Khmer voice in the speech or accessibility settings; the 🔊 buttons appear once one is available.'}</p>
    <h2>Sources and accuracy</h2>
    <p>Every word was checked against its Wiktionary entry (spelling, meaning and romanisation), and the letters, vowels, marks and numerals against Wikipedia's <a href="https://en.wikipedia.org/wiki/Khmer_script" target="_blank" rel="noopener">Khmer script</a>, <a href="https://en.wikipedia.org/wiki/Khmer_numerals" target="_blank" rel="noopener">Khmer numerals</a> and <a href="https://en.wikipedia.org/wiki/Khmer_language" target="_blank" rel="noopener">Khmer language</a> articles. Anything that could not be confirmed was left out. The full list is in <a href="https://github.com/cveenstra/sok_sabay/blob/main/SOURCES.md" target="_blank" rel="noopener">SOURCES.md</a>. Course data is adapted from Wiktionary and Wikipedia under <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noopener">CC BY-SA 4.0</a>; the code is MIT licensed. This is a learning aid, not a substitute for a teacher or a native speaker.</p>
    <h2>Your progress</h2>
    <p>${state.xp} XP, ${Object.keys(state.done).filter((k) => !k.startsWith('L:')).length} of ${counts.lessons} lessons and ${Object.keys(state.done).filter((k) => k.startsWith('L:')).length} of ${counts.groups} letter sets finished, ${Object.keys(state.srs).length} cards in review. ${synced ? 'Progress is saved to your account, so it follows you between devices.' : 'Progress is saved in this browser.'}</p>`;
  const resetRow = h('div', { class: 'row-actions' });
  const armReset = () => resetRow.replaceChildren(
    h('span', { class: 'small' }, 'Erase all XP, lessons and review cards?'),
    h('button', { class: 'btn danger', onclick: () => { store.reset(); state = store.load(); refreshStats(); toast('Progress reset'); viewAbout(); } }, 'Yes, erase'),
    h('button', { class: 'btn ghost', onclick: () => resetRow.replaceChildren(resetBtn) }, 'Cancel'));
  const resetBtn = h('button', { class: 'btn ghost', onclick: armReset }, 'Reset progress');
  resetRow.append(resetBtn);
  sec.append(resetRow);
  app.replaceChildren(sec);
}

// ---------- routing ----------
function route() {
  if (!db) return;
  const parts = location.hash.replace(/^#\/?/, '').split('/');
  const [page, a, b] = parts;
  document.body.classList.remove('in-lesson');
  window.scrollTo(0, 0);
  if (page === 'lesson' && a) {
    const lesson = allLessons().find((l) => l.id === a);
    if (!lesson || !isUnlocked(a)) return go('#/');
    return startSession({ title: lesson.title, questions: buildLesson(db, lesson, unitOf(a)), lessonId: lesson.id, tip: lesson.tip });
  }
  if (page === 'practice' && a) {
    const unit = db.course.units.find((u) => u.id === a);
    if (!unit) return go('#/');
    return startSession({ title: `${unit.title}: practice`, questions: buildUnitPractice(db, unit), lessonId: `P:${unit.id}` });
  }
  if ((page === 'learn-letters' || page === 'practice-letters') && db.group[a]) {
    const g = db.group[a];
    const practice = page === 'practice-letters';
    return startSession({ title: g.title, questions: buildLettersLesson(db, g, { practiceOnly: practice }), lessonId: `L:${g.id}`, tip: practice ? null : g.tip, back: '#/letters' });
  }
  if (page === 'cards' && a && b) {
    const deck = { kind: a === 'unit' ? 'unit' : 'letters', id: b };
    const title = a === 'unit' ? db.course.units.find((u) => u.id === b)?.title : db.group[b]?.title;
    if (!title) return go('#/cards');
    return startCards(title, deckFor(db, deck), a === 'unit' ? '#/' : '#/letters');
  }
  if (page === 'letters') return viewLetters();
  if (page === 'cards') return viewCards();
  if (page === 'review') return viewReview();
  if (page === 'about') return viewAbout();
  return viewHome();
}

async function boot() {
  initSpeech();
  onVoiceChange(() => { if (/about/.test(location.hash)) viewAbout(); });
  onCloudStatus(renderCloud);
  const get = (f) => fetch(`data/${f}`).then((r) => { if (!r.ok) throw new Error(`${f}: ${r.status}`); return r.json(); });
  try {
    const [items, script, sentences, course, letters] = await Promise.all(['items.json', 'script.json', 'sentences.json', 'course.json', 'letters.json'].map(get));
    db = indexData({ items: items.items, script, sentences: sentences.sentences, course, letters });
  } catch (e) {
    app.replaceChildren(h('p', { class: 'loading' }, `Couldn't load the course data (${e.message}). Reload to try again.`));
    return;
  }
  refreshStats();
  window.addEventListener('hashchange', route);
  route();
  // When running as a claude.ai artifact, merge in the account copy of progress.
  startCloudSync().then((merged) => {
    if (!merged) return;
    state = store.load();
    refreshStats();
    if (!document.body.classList.contains('in-lesson')) route();
  }).catch(() => {});
}
boot();
