// Progress lives in localStorage when it is available. Every access is wrapped:
// private windows, blocked storage and quota errors fall back to an in-memory copy,
// so the app keeps working (progress just won't survive a reload).
const KEY = 'soksabay.v1';
const blank = () => ({ xp: 0, streak: { count: 0, last: null }, today: { date: null, xp: 0 }, done: {}, srs: {} });
let memory = null;

export function today(d = new Date()) {
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

export function load() {
  if (memory) return memory;
  let state = blank();
  try {
    const raw = window.localStorage.getItem(KEY);
    if (raw) state = { ...blank(), ...JSON.parse(raw) };
  } catch { /* storage unavailable or corrupt: start fresh in memory */ }
  memory = state;
  return memory;
}

export function save(state) {
  memory = state;
  try { window.localStorage.setItem(KEY, JSON.stringify(state)); } catch { /* keep in memory only */ }
}

export function reset() {
  memory = blank();
  try { window.localStorage.removeItem(KEY); } catch { /* ignore */ }
}

// Streak: counts consecutive local days with at least one finished lesson.
export function currentStreak(state) {
  const { count, last } = state.streak;
  if (!last) return 0;
  const gap = Math.round((new Date(today()) - new Date(last)) / 86400000);
  return gap <= 1 ? count : 0;
}

export function recordLesson(state, { lessonId, xp }) {
  const t = today();
  const s = state.streak;
  if (s.last !== t) {
    const gap = s.last ? Math.round((new Date(t) - new Date(s.last)) / 86400000) : null;
    s.count = gap === 1 ? s.count + 1 : 1;
    s.last = t;
  }
  if (state.today.date !== t) state.today = { date: t, xp: 0 };
  state.today.xp += xp;
  state.xp += xp;
  if (lessonId) state.done[lessonId] = (state.done[lessonId] || 0) + 1;
  save(state);
}

// Leitner-style spaced repetition. Box 1 is due immediately; each correct answer
// moves a card up a box and pushes its next review further out.
const INTERVAL_DAYS = [0, 0, 1, 3, 7, 16];
export function grade(state, key, correct) {
  const card = state.srs[key] || { box: 1, due: today(), miss: 0, seen: 0 };
  card.seen += 1;
  if (correct) card.box = Math.min(card.box + 1, 5);
  else { card.box = 1; card.miss += 1; }
  const d = new Date();
  d.setDate(d.getDate() + INTERVAL_DAYS[card.box]);
  card.due = today(d);
  state.srs[key] = card;
}

export function dueKeys(state, limit = 12) {
  const t = today();
  return Object.entries(state.srs)
    .filter(([, c]) => c.due <= t && (c.miss > 0 || c.box < 5))
    .sort((a, b) => a[1].box - b[1].box || b[1].miss - a[1].miss || (a[1].due < b[1].due ? -1 : 1))
    .slice(0, limit)
    .map(([k]) => k);
}
