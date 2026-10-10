import { indexData, buildLesson, buildReview, isCorrect, shuffle } from './engine.js';
import * as store from './storage.js';
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

function speakBtn(text) {
  if (!canSpeak()) return null;
  return h('button', { class: 'speak', 'aria-label': 'Play Khmer audio', onclick: () => speak(text) }, '🔊');
}

function toast(msg) {
  const t = h('div', { class: 'toast', role: 'status' }, msg);
  document.body.append(t);
  setTimeout(() => t.remove(), 1800);
}

// ---------- chrome ----------
function refreshStats() {
  document.getElementById('stat-streak').textContent = store.currentStreak(state);
  document.getElementById('stat-xp').textContent = state.xp;
}
function setTab(name) {
  document.querySelectorAll('.tabbar button').forEach((b) => b.classList.toggle('on', b.dataset.nav === name));
}
document.addEventListener('click', (e) => {
  const nav = e.target.closest('[data-nav]');
  if (!nav) return;
  location.hash = nav.dataset.nav === 'home' ? '#/' : `#/${nav.dataset.nav}`;
});

// ---------- home / path ----------
function allLessons() { return db.course.units.flatMap((u) => u.lessons); }
function isUnlocked(lessonId) {
  const list = allLessons();
  const i = list.findIndex((l) => l.id === lessonId);
  return i === 0 || !!state.done[list[i - 1].id] || !!state.done[lessonId];
}

function goalRing() {
  const xp = state.today.date === store.today() ? state.today.xp : 0;
  const pct = Math.min(1, xp / DAILY_GOAL);
  const r = 24, c = 2 * Math.PI * r;
  // Parsed as markup so the SVG elements get the SVG namespace.
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
  app.replaceChildren(
    h('section', { class: 'hello' },
      goalRing(),
      h('div', {},
        h('h1', {}, 'សួស្តី! ', h('span', { class: 'rom', style: 'font-size:16px' }, 'suəsdəy, hello!')),
        h('p', {}, streak ? `${streak}-day streak. Daily goal ${DAILY_GOAL} XP.` : `Finish a lesson to start a streak. Daily goal ${DAILY_GOAL} XP.`))),
    ...db.course.units.map((u, ui) =>
      h('section', { class: `unit tone-${ui % 3}` },
        h('div', { class: 'unit-head' },
          h('div', {}, h('h2', {}, u.title), h('p', {}, u.subtitle)),
          km(u.km)),
        h('div', { class: 'path' }, ...u.lessons.map((l) => {
          const unlocked = isUnlocked(l.id);
          const done = !!state.done[l.id];
          return h('button', {
            class: `node ${done ? 'done' : ''} ${unlocked ? '' : 'locked'} ${current && current.id === l.id ? 'current' : ''}`,
            'aria-label': `${l.title}${done ? ' (completed)' : unlocked ? '' : ' (locked)'}`,
            onclick: () => unlocked ? (location.hash = `#/lesson/${l.id}`) : toast('Finish the lesson before this one first'),
          }, h('span', { class: 'disc', 'aria-hidden': 'true' }, done ? '✓' : unlocked ? l.icon : '🔒'), h('span', { class: 'label' }, l.title));
        })))));
}

// ---------- lesson player ----------
function startSession({ title, questions, lessonId, isReview, tip }) {
  document.body.classList.add('in-lesson');
  const s = { title, queue: questions.slice(), total: questions.length, done: 0, hearts: HEARTS, correct: 0, missed: new Set(), lessonId, isReview, tip, requeued: new Set() };
  nextQuestion(s);
}

function lessonChrome(s) {
  return h('div', { class: 'lesson-top' },
    h('button', { class: 'quit', 'aria-label': 'Quit lesson', onclick: () => { document.body.classList.remove('in-lesson'); location.hash = s.isReview ? '#/review' : '#/'; } }, '✕'),
    h('div', { class: 'bar', role: 'progressbar', 'aria-valuemin': 0, 'aria-valuemax': s.total, 'aria-valuenow': s.done },
      h('i', { style: `width:${Math.round((s.done / s.total) * 100)}%` })),
    h('span', { class: 'hearts', 'aria-label': `${s.hearts} hearts left` }, `❤ ${s.hearts}`));
}

function nextQuestion(s) {
  if (s.hearts <= 0) return finish(s, false);
  const qn = s.queue.shift();
  if (!qn) return finish(s, true);
  renderQuestion(s, qn);
}

function renderQuestion(s, qn) {
  let answer = null;
  const checkBtn = h('button', { class: 'btn wide', disabled: true }, 'Check');
  const setAnswer = (a, ready = true) => { answer = a; checkBtn.disabled = !ready; };
  const body = questionBody(qn, setAnswer, () => grade());
  const row = h('div', { class: 'check-row' }, checkBtn);

  function grade() {
    const ok = isCorrect(qn, answer);
    if (qn.key) store.grade(state, qn.key, ok);
    if (ok) s.correct += 1;
    else {
      s.hearts -= 1;
      if (qn.key) s.missed.add(qn.key);
      if (!s.requeued.has(qn) && qn.type !== 'match') { s.requeued.add(qn); s.queue.push(qn); s.total += 1; }
    }
    s.done += 1;
    store.save(state);
    body.querySelectorAll('button.choice, button.word, button.tile').forEach((b) => { b.disabled = true; });
    markChoices(body, qn, answer);
    const cont = h('button', { class: `btn wide ${ok ? 'ok-btn' : ''}`, onclick: () => nextQuestion(s) }, 'Continue');
    row.replaceChildren(feedback(qn, ok), cont);
    cont.focus();
  }
  checkBtn.addEventListener('click', grade);
  app.replaceChildren(h('div', { class: 'lesson' }, lessonChrome(s), s.done === 0 && s.tip ? h('p', { class: 'tip' }, s.tip) : null, body, h('div', { class: 'spacer' }), row));
  if (qn.type === 'match') row.hidden = true;
  app.focus();
}

function markChoices(body, qn, answer) {
  const rightId = qn.item?.id ?? qn.letter?.id ?? qn.vowel?.id ?? qn.digit?.id;
  body.querySelectorAll('button.choice').forEach((b) => {
    const id = b.dataset.id;
    if (qn.type === 'series') {
      if (id === qn.letter.series) b.classList.add('right');
      else if (id === answer) b.classList.add('wrong');
      return;
    }
    if (id === rightId) b.classList.add('right');
    else if (id === answer) b.classList.add('wrong');
    else b.classList.add('faded');
  });
}

function feedback(qn, ok) {
  const sheet = h('div', { class: `sheet ${ok ? 'ok' : 'no'}`, role: 'status' }, h('h3', {}, ok ? pick(['Nice!', 'Correct!', 'Great job!', 'ល្អណាស់! Very good!']) : 'Not quite'));
  const line = (...k) => h('p', {}, ...k);
  switch (qn.type) {
    case 'k2e': case 'e2k': case 'rom':
      sheet.append(line(km(qn.item.km), ' ', rom(qn.item.rom), ` = ${qn.item.en}`));
      if (qn.item.note) sheet.append(line(h('small', {}, qn.item.note)));
      break;
    case 'build':
      sheet.append(line(km(sentenceKm(qn.words))), line(rom(sentenceRom(qn.words))), line(qn.sentence.en));
      break;
    case 'letterSound': case 'letterPick': case 'series':
      sheet.append(line(km(qn.letter.char), ` is "${qn.letter.name}" ${qn.letter.ipa_name}, an ${qn.letter.series}-series consonant.`));
      break;
    case 'vowel':
      sheet.append(line(km(qn.vowel.example), ` sounds ${qn.vowel.ipa_a} after an a-series consonant, ${qn.vowel.ipa_o} after an o-series one.`));
      break;
    case 'digit':
      sheet.append(line(km(qn.digit.char), ` is ${qn.digit.value}`, qn.digit.word ? [' (', km(qn.digit.word), ' ', rom(qn.digit.word_rom), ')'] : ''));
      break;
    case 'match':
      sheet.append(line(ok ? 'All pairs matched.' : 'Some pairs were mismatched; they will come back in Review.'));
      break;
  }
  return sheet;
}
const pick = (a) => a[Math.floor(Math.random() * a.length)];

function choiceList(options, render, setAnswer, cls = '') {
  const list = h('div', { class: `choices ${cls}` });
  options.forEach((opt, i) => {
    const b = h('button', { class: 'choice', 'data-id': opt.id ?? opt, onclick: () => {
      list.querySelectorAll('.choice').forEach((x) => x.classList.remove('sel'));
      b.classList.add('sel');
      setAnswer(opt.id ?? opt);
    } }, render(opt, i));
    list.append(b);
  });
  return list;
}

function questionBody(qn, setAnswer, autoGrade) {
  const wrap = h('div', {});
  const label = (t) => h('h2', { class: 'prompt-label' }, t);
  switch (qn.type) {
    case 'k2e':
      wrap.append(label('What does this mean?'),
        h('div', { class: 'prompt' }, speakBtn(qn.item.km), km(qn.item.km, 'big'), rom(qn.item.rom)),
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
    case 'letterSound':
      wrap.append(label('What is this letter called?'),
        h('p', { class: 'letter-big', lang: 'km' }, qn.letter.char),
        choiceList(qn.options, (o) => [h('b', {}, o.name), ' ', h('span', { class: 'rom' }, o.ipa_name)], setAnswer, 'two'));
      break;
    case 'letterPick':
      wrap.append(label(`Which letter is "${qn.letter.name}" ${qn.letter.ipa_name}?`),
        choiceList(qn.options, (o) => [km(o.char, 'big')], setAnswer, 'two'));
      wrap.querySelectorAll('.choice').forEach((b) => { b.style.textAlign = 'center'; b.querySelector('.km').style.fontSize = '44px'; });
      break;
    case 'series':
      wrap.append(label('Which series is this consonant?'),
        h('p', { class: 'letter-big', lang: 'km' }, qn.letter.char),
        choiceList(['a', 'o'], (o) => [h('b', {}, `${o}-series`), ' ', h('span', { class: 'rom' }, o === 'a' ? 'inherent vowel â [ɑː]' : 'inherent vowel ô [ɔː]')], setAnswer, 'two'));
      break;
    case 'vowel':
      wrap.append(label('How does this vowel sound after an a-series consonant?'),
        h('p', { class: 'letter-big', lang: 'km' }, qn.vowel.example),
        h('p', { class: 'lead', style: 'text-align:center' }, 'Shown on អ, an a-series consonant.'),
        choiceList(qn.options, (o) => [h('b', {}, o.ipa_a), ' ', h('span', { class: 'rom' }, `UNGEGN ${o.rom_a}`)], setAnswer, 'two'));
      break;
    case 'digit':
      wrap.append(label('Which number is this?'),
        h('p', { class: 'letter-big', lang: 'km' }, qn.digit.char),
        choiceList(qn.options, (o) => h('b', { style: 'font-size:24px' }, String(o.value)), setAnswer, 'two'));
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
  qn.bank.forEach((w) => {
    const tileIn = h('button', { class: 'word', onclick: () => {
      tileIn.classList.add('used');
      const tileOut = h('button', { class: 'word', onclick: () => {
        tileOut.remove(); tileIn.classList.remove('used');
        chosen.splice(chosen.findIndex((c) => c.el === tileOut), 1); sync();
      } }, km(w.km), h('small', {}, w.rom));
      chosen.push({ word: w, el: tileOut }); line.append(tileOut); sync();
    } }, km(w.km), h('small', {}, w.rom));
    bank.append(tileIn);
  });
  return [h('h2', { class: 'prompt-label' }, 'Write this in Khmer'),
    h('div', { class: 'prompt' }, h('span', { class: 'en-big' }, qn.sentence.en)), line, bank];
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
    if (left === 0) { setAnswer(mistakes === 0); setTimeout(() => { document.querySelector('.check-row').hidden = false; autoGrade(); }, 250); }
  };
  shuffle(qn.pairs).forEach((it) => { const b = h('button', { class: 'tile', onclick: () => onPick(b, 'km', it) }, km(it.km)); leftCol.append(b); });
  shuffle(qn.pairs).forEach((it) => { const b = h('button', { class: 'tile', onclick: () => onPick(b, 'en', it) }, it.en); rightCol.append(b); });
  return [h('h2', { class: 'prompt-label' }, 'Match the pairs'), h('div', { class: 'match' }, leftCol, rightCol)];
}

function finish(s, completed) {
  document.body.classList.remove('in-lesson');
  const accuracy = s.done ? Math.round((s.correct / s.done) * 100) : 0;
  let xp = 0;
  if (completed) {
    xp = (s.isReview ? 5 : 10) + Math.min(s.correct, 15);
    store.recordLesson(state, { lessonId: s.isReview ? null : s.lessonId, xp });
  } else store.save(state);
  refreshStats();
  app.replaceChildren(h('section', { class: 'results' },
    h('div', { class: 'burst', 'aria-hidden': 'true' }, completed ? '🪷' : '💔'),
    h('h1', {}, completed ? (s.isReview ? 'Review done!' : 'Lesson complete!') : 'Out of hearts'),
    h('p', { class: 'lead' }, completed ? s.title : 'Missed words are saved for Review. Try the lesson again.'),
    h('div', { class: 'result-grid' },
      h('div', { class: 'card' }, h('b', {}, `+${xp}`), h('span', {}, 'XP')),
      h('div', { class: 'card' }, h('b', {}, `${accuracy}%`), h('span', {}, 'Accuracy')),
      h('div', { class: 'card' }, h('b', {}, store.currentStreak(state)), h('span', {}, 'Day streak'))),
    h('div', { class: 'row-actions', style: 'justify-content:center' },
      completed ? null : h('button', { class: 'btn', onclick: () => route() }, 'Try again'),
      h('button', { class: `btn ${completed ? '' : 'ghost'}`, onclick: () => { location.hash = '#/'; } }, 'Continue'))));
}

// ---------- review ----------
function viewReview() {
  setTab('review');
  const due = store.dueKeys(state, 14);
  const seen = Object.keys(state.srs).length;
  if (!due.length) {
    app.replaceChildren(h('div', { class: 'review-empty' },
      h('div', { style: 'font-size:48px' }, '🔁'),
      h('h1', { class: 'section-title' }, seen ? 'Nothing due right now' : 'Review unlocks as you learn'),
      h('p', {}, seen ? 'Words you miss come back here first. Everything else returns on a schedule: 1, 3, 7 and 16 days after you get it right.' : 'Finish a lesson and the words you meet will be scheduled for review.'),
      h('button', { class: 'btn', onclick: () => { location.hash = '#/'; } }, 'Back to lessons')));
    return;
  }
  const questions = buildReview(db, due);
  app.replaceChildren(h('section', {},
    h('h1', { class: 'section-title' }, 'Review'),
    h('p', { class: 'lead' }, `${due.length} card${due.length === 1 ? '' : 's'} due. Missed words come first.`),
    h('button', { class: 'btn wide', onclick: () => startSession({ title: 'Review', questions, isReview: true }) }, 'Start review')));
}

// ---------- script reference ----------
function viewScript() {
  setTab('script');
  const { consonants, vowels, digits } = db.script;
  app.replaceChildren(h('section', {},
    h('h1', { class: 'section-title' }, 'The Khmer script'),
    h('p', { class: 'lead' }, 'Khmer is written left to right, usually without spaces between words. Every consonant carries an inherent vowel: a-series letters read with â [ɑː], o-series letters with ô [ɔː], and that series also changes how each vowel sign is pronounced.'),
    h('h2', { class: 'section-title', style: 'font-size:18px' }, `Consonants (${consonants.length})`),
    h('div', { class: 'legend' }, h('span', { class: 'ser a' }, 'a-series'), h('span', { class: 'ser o' }, 'o-series')),
    h('div', { class: 'grid-letters' }, ...consonants.map((c) => h('div', { class: 'lt' },
      h('span', { class: 'km', lang: 'km' }, c.char), h('small', {}, c.name), h('span', { class: `ser ${c.series}` }, c.series)))),
    h('h2', { class: 'section-title', style: 'font-size:18px' }, 'Dependent vowels'),
    h('p', { class: 'lead' }, 'Written on, above, below or around a consonant (shown here on អ). The same sign is read two ways, depending on the series of the consonant it sits on.'),
    h('div', { class: 'table-wrap' }, h('table', { class: 'vtab' },
      h('thead', {}, h('tr', {}, h('th', {}, 'Vowel'), h('th', {}, 'a-series'), h('th', {}, 'o-series'))),
      h('tbody', {}, ...vowels.map((v) => h('tr', {}, h('td', { class: 'km', lang: 'km' }, v.example), h('td', {}, `${v.ipa_a} · ${v.rom_a}`), h('td', {}, `${v.ipa_o} · ${v.rom_o}`)))))),
    h('h2', { class: 'section-title', style: 'font-size:18px' }, 'Numerals'),
    h('div', { class: 'grid-letters' }, ...digits.map((d) => h('div', { class: 'lt' },
      h('span', { class: 'km', lang: 'km' }, d.char), h('small', {}, String(d.value)), d.word ? h('small', { lang: 'km', class: 'km' }, d.word) : null)))));
}

// ---------- about ----------
function viewAbout() {
  setTab('about');
  const counts = { items: db.items.length, sentences: db.sentences.length, lessons: allLessons().length, units: db.course.units.length };
  const sec = h('section', { class: 'prose' });
  sec.innerHTML = `
    <h1 class="section-title">About Sok Sabay</h1>
    <p><span class="km" lang="km">សុខសប្បាយ</span> <i>sok sapbaay</i> means "well and happy". It is how Cambodians ask and answer "How are you?". This is a free, bite-sized course in Khmer, the national language of Cambodia: ${counts.units} units, ${counts.lessons} lessons, ${counts.items} words and phrases, and ${counts.sentences} sentences to build. Your progress stays in this browser; there is no account.</p>
    <h2>Romanisation</h2>
    <p>Khmer spelling doesn't map neatly onto English letters, so every word also shows a romanisation. This course uses two published schemes and doesn't make up its own:</p>
    <ul>
      <li><b>Words, phrases and sentences</b>: Wiktionary's <i>WT romanisation</i>, a phonemic system that follows the standard (Phnom Penh) pronunciation. A few symbols to know: <code>ɑ</code> as in "father", <code>ə</code> a short "uh", <code>ɨ</code> like "uh" with spread lips, <code>ɔ</code> as in "law", <code>ŏə</code>/<code>ĕə</code> short gliding vowels, <code>ʼ</code> a glottal stop, and <code>ñ</code> like "ny" in "canyon". Doubled vowels (<code>aa</code>, <code>ii</code>) are long.</li>
      <li><b>Letters and vowel signs</b>: the UN-recommended <i>UNGEGN</i> transliteration with IPA, as in Wikipedia's Khmer script article. Letter names ending in <i>â</i> are a-series, those in <i>ô</i> are o-series.</li>
    </ul>
    <h2>Politeness and address</h2>
    <p>Khmer uses kinship words as "you" and "I". <span class="km" lang="km">បង</span> <i>bɑɑng</i> is for someone a little older, <span class="km" lang="km">ប្អូន</span> <i>pʼoun</i> for someone younger, <span class="km" lang="km">លោក</span> <i>look</i> for a man you address respectfully, <span class="km" lang="km">លោកស្រី</span> <i>look srəy</i> for a woman of standing. Men answer "yes" with <span class="km" lang="km">បាទ</span> <i>baat</i>, women with <span class="km" lang="km">ចាស</span> <i>caah</i>. Greetings are often made with the <span class="km" lang="km">សំពះ</span> <i>sɑmpĕəh</i>: palms pressed together in front of the chest, fingers pointing up, as a gesture of respect when meeting someone or leaving.</p>
    <h2>Audio</h2>
    <p>${canSpeak() ? 'Your browser has a Khmer voice, so 🔊 buttons read words aloud. It is a synthetic voice, so treat it as a guide, not a native speaker.' : 'Your browser has no Khmer text-to-speech voice, so audio is turned off. On phones and some systems you can add a Khmer voice in the accessibility or speech settings; the 🔊 buttons appear once one is available.'}</p>
    <h2>Sources and accuracy</h2>
    <p>Every word was checked against its Wiktionary entry (spelling, meaning and romanisation), and the alphabet, vowels and numerals against Wikipedia's <a href="https://en.wikipedia.org/wiki/Khmer_script">Khmer script</a>, <a href="https://en.wikipedia.org/wiki/Khmer_numerals">Khmer numerals</a> and <a href="https://en.wikipedia.org/wiki/Khmer_language">Khmer language</a> articles. Sentence patterns follow the grammar examples in the Khmer language article. Anything that could not be confirmed was left out. The full list is in <a href="https://github.com/cveenstra/sok_sabay/blob/main/SOURCES.md">SOURCES.md</a>.</p>
    <p>The course data is adapted from Wiktionary and Wikipedia and shared under <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>; the code is MIT licensed. This is a learning aid, not a substitute for a teacher or a native speaker. Corrections are welcome on <a href="https://github.com/cveenstra/sok_sabay/issues">GitHub</a>.</p>
    <h2>Your progress</h2>
    <p>${state.xp} XP, ${Object.keys(state.done).length} of ${counts.lessons} lessons finished, ${Object.keys(state.srs).length} cards in review.</p>`;
  sec.append(h('div', { class: 'row-actions' }, h('button', { class: 'btn ghost', onclick: () => {
    if (!confirmReset()) return;
    store.reset(); state = store.load(); refreshStats(); toast('Progress reset'); viewAbout();
  } }, 'Reset progress')));
  app.replaceChildren(sec);
}
// Two-step reset without a blocking browser dialog.
let resetArmed = 0;
function confirmReset() {
  if (Date.now() - resetArmed < 4000) { resetArmed = 0; return true; }
  resetArmed = Date.now(); toast('Tap again to erase all progress'); return false;
}

// ---------- routing ----------
function route() {
  if (!db) return;
  const [, page, id] = location.hash.replace(/^#\/?/, '#').split(/[#/]/);
  document.body.classList.remove('in-lesson');
  window.scrollTo(0, 0);
  if (page === 'lesson' && id) {
    const lesson = allLessons().find((l) => l.id === id);
    if (!lesson || !isUnlocked(id)) { location.hash = '#/'; return; }
    return startSession({ title: lesson.title, questions: buildLesson(db, lesson), lessonId: lesson.id, tip: lesson.tip });
  }
  if (page === 'review') return viewReview();
  if (page === 'script') return viewScript();
  if (page === 'about') return viewAbout();
  return viewHome();
}

async function boot() {
  initSpeech();
  onVoiceChange(() => { if (/about/.test(location.hash)) viewAbout(); });
  const get = (f) => fetch(`data/${f}`).then((r) => { if (!r.ok) throw new Error(`${f}: ${r.status}`); return r.json(); });
  try {
    const [items, script, sentences, course] = await Promise.all(['items.json', 'script.json', 'sentences.json', 'course.json'].map(get));
    db = indexData({ items: items.items, script, sentences: sentences.sentences, course });
  } catch (e) {
    app.replaceChildren(h('p', { class: 'loading' }, `Couldn't load the course data (${e.message}). Reload to try again.`));
    return;
  }
  refreshStats();
  window.addEventListener('hashchange', route);
  route();
}
boot();
