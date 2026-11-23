"""Sprig - a small, cute, reusable mascot for Streamlit apps.

Copy this one file next to your app.py, then:

    import sprig
    sprig.sprig(mood="happy", message="Hi! I'm Sprig.", tips=["Tip one", "Tip two"],
                knowledge=[{"k": ["payback"], "a": "Payback is ..."}], chips=["What is payback?"])

Moods: "happy", "excited", "worried", "sleepy".
What Sprig does:
  * blinks, sways and hops by itself; its eyes follow your cursor;
  * dances (arms, feet, spin, music notes) on first visit, now and then, and when asked;
  * click Sprig (or the chat badge) to open a small chat panel and ask questions;
  * answers come from the `knowledge` list you pass in (keyword matching, no internet needed);
  * falls asleep (tap to wake) after 45 seconds of quiet.
`knowledge` entries: {"k": [keywords or phrases], "a": "answer text", "w": weight, "x": "dance"}.
`chips` are the quick-question buttons shown under the chat. Pass floating=False to draw it
inside the page instead of in the bottom-right corner.
"""
import json

import streamlit as st

MOODS = ("happy", "excited", "worried", "sleepy")

# The floating box starts small; the script inside resizes it when the chat opens.
FLOAT_CSS = """<style>
.st-key-sprig {position: fixed; right: 12px; bottom: 6px; width: 292px; z-index: 9999;}
.st-key-sprig iframe {border: 0; background: transparent;}
</style>"""

_SVG = """<svg id="sp" viewBox="0 -8 120 140" role="img" aria-label="Sprig, a sprout-blob mascot">
<ellipse cx="60" cy="123" rx="30" ry="6" fill="#0B1B3F" opacity=".12"/>
<path d="M60 30V14" stroke="#2E8B57" stroke-width="4" stroke-linecap="round" fill="none"/>
<g class="leaf"><path d="M60 16C44 16 36 6 38 0C52 0 62 6 60 16Z" fill="#4DAA57"/></g>
<g class="leaf r"><path d="M60 16C76 16 84 6 82 0C68 0 58 6 60 16Z" fill="#F5A623"/></g>
<ellipse class="foot l" cx="45" cy="119" rx="11" ry="5.5" fill="#8EE3C8" stroke="#13A08A" stroke-width="3"/>
<ellipse class="foot r" cx="75" cy="119" rx="11" ry="5.5" fill="#8EE3C8" stroke="#13A08A" stroke-width="3"/>
<g class="arm l"><ellipse cx="17" cy="93" rx="6" ry="10" transform="rotate(25 17 93)" fill="#8EE3C8" stroke="#13A08A" stroke-width="3"/></g>
<g class="arm r"><ellipse cx="103" cy="93" rx="6" ry="10" transform="rotate(-25 103 93)" fill="#8EE3C8" stroke="#13A08A" stroke-width="3"/></g>
<path d="M60 28C92 28 104 56 102 82C100 108 82 119 60 119C38 119 20 108 18 82C16 56 28 28 60 28Z" fill="#8EE3C8" stroke="#13A08A" stroke-width="4"/>
<ellipse cx="60" cy="98" rx="22" ry="15" fill="#C6F3E4"/>
<g id="eyesO">
<g id="pL"><g class="eyeO"><ellipse cx="46" cy="68" rx="7" ry="9" fill="#0B1B3F"/><circle cx="48.5" cy="64" r="2.6" fill="#fff"/></g></g>
<g id="pR"><g class="eyeO"><ellipse cx="74" cy="68" rx="7" ry="9" fill="#0B1B3F"/><circle cx="76.5" cy="64" r="2.6" fill="#fff"/></g></g>
</g>
<g id="eyesC" style="display:none" fill="none" stroke="#0B1B3F" stroke-width="3.5" stroke-linecap="round"><path d="M39 70Q46 76 53 70"/><path d="M67 70Q74 76 81 70"/></g>
<g id="brows" style="display:none" fill="none" stroke="#0B1B3F" stroke-width="3" stroke-linecap="round"><path d="M38 57L54 62"/><path d="M82 57L66 62"/></g>
<ellipse cx="34" cy="82" rx="7" ry="4.5" fill="#FF9DB0"/><ellipse cx="86" cy="82" rx="7" ry="4.5" fill="#FF9DB0"/>
<path id="mHappy" d="M52 81Q60 91 68 81" stroke="#0B1B3F" stroke-width="3.5" fill="none" stroke-linecap="round"/>
<g id="mExcited" style="display:none"><path d="M50 79Q60 99 70 79Z" fill="#B83A5A" stroke="#0B1B3F" stroke-width="3" stroke-linejoin="round"/><path d="M55 90Q60 86 65 90Q60 94 55 90Z" fill="#FF9DB0"/></g>
<path id="mWorried" style="display:none" d="M53 88Q60 80 67 88" stroke="#0B1B3F" stroke-width="3.5" fill="none" stroke-linecap="round"/>
<path id="mSleepy" style="display:none" d="M56 84Q60 87 64 84" stroke="#0B1B3F" stroke-width="3.5" fill="none" stroke-linecap="round"/>
<path d="M60 92l2.6 5.4 5.4 2.6-5.4 2.6-2.6 5.4-2.6-5.4-5.4-2.6 5.4-2.6z" fill="#F5A623"/>
<g id="sparks" style="display:none" fill="#F5A623"><path class="tw" d="M12 40l1.6 3.4 3.4 1.6-3.4 1.6-1.6 3.4-1.6-3.4-3.4-1.6 3.4-1.6z"/><path class="tw d2" d="M108 34l1.6 3.4 3.4 1.6-3.4 1.6-1.6 3.4-1.6-3.4-3.4-1.6 3.4-1.6z"/><path class="tw d3" d="M98 8l1.2 2.6 2.6 1.2-2.6 1.2-1.2 2.6-1.2-2.6-2.6-1.2 2.6-1.2z"/></g>
<g id="notes" style="display:none" fill="#13A08A" font-weight="800"><text class="nt" x="4" y="34" font-size="20">&#9834;</text><text class="nt d2" x="100" y="26" font-size="18">&#9835;</text><text class="nt d3" x="106" y="58" font-size="15">&#9834;</text></g>
<g id="zzz" style="display:none" fill="#0B7A69" font-weight="800"><text class="zz" x="88" y="40" font-size="15">z</text><text class="zz d2" x="99" y="26" font-size="11">z</text></g>
<path id="drop" style="display:none" d="M97 50q5 8 0 11q-5-3 0-11z" fill="#7CC7FF"/>
</svg>"""

_TEMPLATE = r"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;height:100%;background:transparent;font-family:'Nunito','Segoe UI',system-ui,sans-serif;overflow:hidden}
#wrap{display:flex;flex-direction:column;align-items:flex-end;justify-content:flex-end;height:100%;
 box-sizing:border-box;padding:0 8px 2px 0;gap:6px}
#row{display:flex;align-items:flex-end;justify-content:flex-end;gap:6px;flex:0 0 auto}
#bubble{position:relative;background:#fff;border:2px solid #D7EFE9;color:#0B1B3F;border-radius:14px;padding:7px 11px;
 font-size:12.5px;line-height:1.3;max-width:190px;margin-bottom:26px;box-shadow:0 4px 12px rgba(11,27,63,.14);
 cursor:pointer;transition:opacity .25s,transform .25s}
#bubble .ask{display:block;margin-top:3px;color:#13A08A;font-weight:800;font-size:11.5px}
#bubble.hide{opacity:0;transform:scale(.9);pointer-events:none}
#bubble:after{content:"";position:absolute;right:-9px;bottom:14px;border:8px solid transparent;border-left-color:#D7EFE9;border-right:0}
#cw{position:relative;width:76px;height:89px;flex:0 0 auto}
#char{width:76px;height:89px;cursor:pointer;user-select:none;-webkit-tap-highlight-color:transparent;
 transform-origin:50% 100%;animation:breathe 3.2s ease-in-out infinite}
#char svg{width:100%;height:100%;overflow:visible;display:block}
#badge{position:absolute;left:-8px;top:4px;width:24px;height:24px;border-radius:50%;background:#13A08A;color:#fff;
 font-size:12px;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 6px rgba(11,27,63,.25);
 cursor:pointer;border:2px solid #fff;animation:pulse 2.6s ease-in-out infinite}
@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.14)}}
#char.hop{animation:hop .7s ease-out}
@keyframes breathe{0%,100%{transform:scale(1,1)}50%{transform:scale(1.02,.98)}}
@keyframes hop{0%{transform:scale(1,1)}20%{transform:scale(1.1,.86)}45%{transform:translateY(-20px) scale(.94,1.08)}
 70%{transform:scale(1.08,.9)}100%{transform:scale(1,1)}}
.eyeO{transform-box:fill-box;transform-origin:center;transition:transform .08s}
#char.blink .eyeO{transform:scaleY(.1)}
#pL,#pR{transition:transform .12s ease-out}
.leaf{transform-box:fill-box;transform-origin:0% 100%;animation:sway 3.4s ease-in-out infinite}
.leaf.r{transform-origin:100% 100%;animation-delay:.6s}
@keyframes sway{0%,100%{transform:rotate(-5deg)}50%{transform:rotate(5deg)}}
.arm,.foot{transform-box:fill-box}
.arm{transform-origin:50% 8%}
.foot{transform-origin:50% 50%}
.tw{transform-box:fill-box;transform-origin:center;animation:tw 1.4s ease-in-out infinite}
.d2{animation-delay:.45s}.d3{animation-delay:.9s}
@keyframes tw{0%,100%{opacity:0;transform:scale(.4)}50%{opacity:1;transform:scale(1.1)}}
.zz{animation:zz 2.2s ease-in-out infinite}
@keyframes zz{0%{opacity:0;transform:translateY(6px)}50%{opacity:1}100%{opacity:0;transform:translateY(-6px)}}
.nt{animation:note 1.5s ease-out infinite}
@keyframes note{0%{opacity:0;transform:translateY(8px)}30%{opacity:1}100%{opacity:0;transform:translateY(-20px) rotate(14deg)}}

/* ---- the dance: sway, hop, arm waves, foot steps, a spin, a jump, then a bow ---- */
#char.dance{animation:groove 3.6s ease-in-out 1 both;perspective:300px}
@keyframes groove{
 0%{transform:translateY(0) rotate(0)}
 4%{transform:translateY(-8px) rotate(-10deg)}
 8%{transform:translateY(0) rotate(0) scale(1.07,.9)}
 12%{transform:translateY(-8px) rotate(10deg)}
 16%{transform:translateY(0) rotate(0) scale(1.07,.9)}
 20%{transform:translateY(-8px) rotate(-10deg)}
 24%{transform:translateY(0) rotate(0) scale(1.07,.9)}
 28%{transform:translateY(-8px) rotate(10deg)}
 32%{transform:translateY(0) rotate(0) scale(1.07,.9)}
 38%{transform:translateY(-22px) scale(.94,1.1)}
 44%{transform:translateY(0) scale(1.12,.84)}
 50%{transform:translateY(-18px) rotateY(0deg) scale(1,1)}
 62%{transform:translateY(-22px) rotateY(180deg)}
 74%{transform:translateY(-18px) rotateY(360deg)}
 80%{transform:translateY(0) rotateY(360deg) scale(1.1,.88)}
 86%{transform:translateY(-8px) rotate(-8deg)}
 90%{transform:translateY(0) rotate(8deg) scale(1.05,.94)}
 95%{transform:translateY(0) rotate(0) scale(1,.8)}
 100%{transform:translateY(0) rotate(0) scale(1,1)}}
#char.dance .arm.l{animation:armL .42s ease-in-out infinite alternate}
#char.dance .arm.r{animation:armR .42s ease-in-out infinite alternate}
@keyframes armL{0%{transform:rotate(0)}100%{transform:rotate(150deg)}}
@keyframes armR{0%{transform:rotate(0)}100%{transform:rotate(-150deg)}}
#char.dance .arm.r{animation-delay:-.21s}
#char.dance .foot.l{animation:stepL .42s ease-in-out infinite alternate}
#char.dance .foot.r{animation:stepL .42s ease-in-out infinite alternate-reverse}
@keyframes stepL{0%{transform:translateY(0)}100%{transform:translateY(-6px)}}
#char.dance .leaf{animation:sway .36s ease-in-out infinite}

/* ---- chat panel ---- */
#panel{display:none;flex-direction:column;width:100%;flex:1 1 auto;min-height:0;background:#fff;border:2px solid #D7EFE9;
 border-radius:18px;box-shadow:0 8px 28px rgba(11,27,63,.22);overflow:hidden}
body.open #panel{display:flex}
body.open #bubble{display:none}
#phead{display:flex;align-items:center;justify-content:space-between;background:linear-gradient(120deg,#D8F3EA,#fff);
 padding:8px 12px;font-weight:800;color:#0B1B3F;font-size:14px;border-bottom:1px solid #E1F1EC}
#phead small{font-weight:600;color:#5B6B8C;font-size:11px;margin-left:6px}
#pclose{border:0;background:transparent;font-size:17px;line-height:1;cursor:pointer;color:#0B1B3F;padding:2px 6px;border-radius:8px}
#pclose:hover{background:#E8F6F3}
#msgs{flex:1 1 auto;min-height:0;overflow-y:auto;padding:10px;display:flex;flex-direction:column;gap:7px;
 font-size:13px;line-height:1.42;color:#0B1B3F}
.m{max-width:90%;padding:7px 10px;border-radius:14px;word-wrap:break-word;overflow-wrap:anywhere}
.m.s{align-self:flex-start;background:#E8F6F3;border-bottom-left-radius:4px}
.m.u{align-self:flex-end;background:#13A08A;color:#fff;border-bottom-right-radius:4px}
.m.t{align-self:flex-start;background:#E8F6F3;color:#5B6B8C;letter-spacing:2px}
#chips{display:flex;gap:6px;overflow-x:auto;padding:7px 10px;border-top:1px solid #EEF5F3;white-space:nowrap;
 scrollbar-width:thin;flex:0 0 auto}
.chip{flex:0 0 auto;border:1.5px solid #13A08A;background:#fff;color:#0B1B3F;border-radius:999px;padding:4px 10px;
 font-size:12px;font-weight:700;cursor:pointer;font-family:inherit}
.chip:hover{background:#13A08A;color:#fff}
#pform{display:flex;gap:6px;padding:8px 10px;border-top:1px solid #EEF5F3;flex:0 0 auto;margin:0}
#q{flex:1;min-width:0;border:1.5px solid #CDE9E2;border-radius:999px;padding:7px 12px;font-size:13px;
 font-family:inherit;outline:none;color:#0B1B3F;background:#fff}
#q:focus{border-color:#13A08A}
#send{border:0;background:#13A08A;color:#fff;border-radius:50%;width:34px;height:34px;font-size:15px;cursor:pointer;flex:0 0 auto}
@media (pointer:coarse){#q{font-size:16px}}
@media (prefers-reduced-motion:reduce){#char,.leaf,#badge{animation:none}}
</style></head><body>
<div id="wrap">
 <div id="panel" aria-label="Ask Sprig">
  <div id="phead"><span>&#127793; Ask Sprig<small>dashboard helper</small></span><button id="pclose" title="Close" aria-label="Close chat">&#10005;</button></div>
  <div id="msgs" aria-live="polite"></div>
  <div id="chips"></div>
  <form id="pform" autocomplete="off"><input id="q" type="text" maxlength="200" placeholder="Ask about the dashboard..." aria-label="Your question"><button id="send" type="submit" title="Send" aria-label="Send">&#10148;</button></form>
 </div>
 <div id="row">
  <div id="bubble" role="status"></div>
  <div id="cw"><div id="char" title="Click me to ask a question!">__SVG__</div><div id="badge" title="Ask me!">&#128172;</div></div>
 </div>
</div>
<script>
const D = __DATA__;
const $ = id => document.getElementById(id);
const bubble = $('bubble'), ch = $('char'), msgs = $('msgs'), chipsEl = $('chips'), input = $('q');
let mood = D.mood, base = D.mood, tipIdx = 0, lastAct = Date.now(), dancing = false, isOpen = false, bubbleOn = false;
const REDUCED = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
const TOUCH = window.matchMedia && matchMedia('(pointer: coarse)').matches;

/* ---------- remember the chat while the app reruns ---------- */
let store = {open: false, msgs: [], seen: false};
try { const raw = window.parent.sessionStorage.getItem('sprigState'); if (raw) store = Object.assign(store, JSON.parse(raw)); } catch (_) {}
function save() { try { window.parent.sessionStorage.setItem('sprigState', JSON.stringify(store)); } catch (_) {} }

/* ---------- resize the floating box (small, bubble-only, or chat) ---------- */
function layout() {
  try {
    const fe = window.frameElement; if (!fe) return;
    const P = window.parent, vw = P.innerWidth, vh = P.innerHeight;
    let w, h;
    if (isOpen) { w = Math.min(340, vw - 16); h = Math.min(500, vh - 16); }
    else if (bubbleOn) { w = Math.min(292, vw - 16); h = 136; }
    else { w = 96; h = 104; }
    const box = fe.closest('.st-key-sprig');
    if (box) { box.style.width = w + 'px'; box.style.height = h + 'px'; }
    for (let n = fe.parentElement; n && n !== box && n !== P.document.body; n = n.parentElement) {
      n.style.height = h + 'px'; n.style.width = w + 'px'; n.style.overflow = 'visible';
    }
    fe.style.width = w + 'px'; fe.style.height = h + 'px'; fe.setAttribute('height', h);
  } catch (_) {}
}

/* ---------- face and speech ---------- */
function show(id, on) { $(id).style.display = on ? '' : 'none'; }
function setMood(m) {
  mood = m;
  show('eyesO', m !== 'sleepy'); show('eyesC', m === 'sleepy');
  show('brows', m === 'worried'); show('drop', m === 'worried');
  show('mHappy', m === 'happy'); show('mExcited', m === 'excited');
  show('mWorried', m === 'worried'); show('mSleepy', m === 'sleepy');
  show('sparks', m === 'excited'); show('zzz', m === 'sleepy');
}
let bubbleT = null;
function short(t) {
  if (t.length <= 92) return t;
  const m = t.slice(0, 92).match(/^(.*[.!?])\s/);
  return m ? m[1] : t.slice(0, 90).replace(/\s+\S*$/, '') + '\u2026';
}
function say(t, keep) {
  clearTimeout(bubbleT);
  if (!t || isOpen) { bubble.classList.add('hide'); bubbleOn = false; layout(); return; }
  bubble.innerHTML = '';
  bubble.appendChild(document.createTextNode(short(t)));
  const a = document.createElement('span'); a.className = 'ask'; a.textContent = 'Ask me a question \u203A';
  bubble.appendChild(a);
  bubble.classList.remove('hide'); bubbleOn = true; layout();
  if (!keep) bubbleT = setTimeout(() => { bubble.classList.add('hide'); bubbleOn = false; layout(); }, 11000);
}
function jump() {
  ch.classList.remove('hop'); void ch.offsetWidth; ch.classList.add('hop');
  setTimeout(() => ch.classList.remove('hop'), 720);
}
function dance(ms) {
  if (dancing) return;
  dancing = true; lastAct = Date.now();
  const prev = mood === 'sleepy' ? base : mood;
  setMood('excited'); show('notes', true);
  ch.classList.remove('hop'); ch.classList.add('dance');
  setTimeout(() => {
    ch.classList.remove('dance'); show('notes', false); dancing = false;
    setMood(prev);
  }, ms || 3600);
}
function wake() {
  lastAct = Date.now();
  if (mood === 'sleepy') { setMood(base); if (!isOpen) say(D.message); }
}

/* ---------- chat ---------- */
function esc(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
function fmt(s) { return esc(s).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/\n/g, '<br>'); }
function addMsg(role, text, persist) {
  const d = document.createElement('div'); d.className = 'm ' + role; d.innerHTML = fmt(text);
  msgs.appendChild(d); msgs.scrollTop = msgs.scrollHeight;
  if (persist !== false) {
    store.msgs.push({r: role, t: text});
    if (store.msgs.length > 40) store.msgs.splice(0, store.msgs.length - 40);
    save();
  }
  return d;
}
const STOP = new Set(('the a an is are was were be been to of in on at it its this that these those and or for with can could ' +
  'would should you your me my i we our us do does did please tell about so as if then than there here has have had will ' +
  'just also any some very much many from by not no yes what how why when who which where').split(' '));
function stem(w) {
  if (w.length > 4 && w.endsWith('ies')) w = w.slice(0, -3) + 'y';
  else if (w.length > 3 && w.endsWith('s') && !w.endsWith('ss')) w = w.slice(0, -1);
  if (w.length > 5 && w.endsWith('ing')) w = w.slice(0, -3);
  else if (w.length > 4 && w.endsWith('ed')) w = w.slice(0, -2);
  if (w.length > 3 && w.endsWith('e')) w = w.slice(0, -1);
  return w;
}
function words(s) { return s.toLowerCase().replace(/[^a-z0-9\u0600-\u06ff ]+/g, ' ').split(/\s+/).filter(Boolean); }
function lev1(a, b) {
  if (Math.abs(a.length - b.length) > 1) return false;
  let i = 0, j = 0, miss = 0;
  while (i < a.length && j < b.length) {
    if (a[i] === b[j]) { i++; j++; continue; }
    if (++miss > 1) return false;
    if (a.length > b.length) i++; else if (a.length < b.length) j++; else { i++; j++; }
  }
  return miss + (a.length - i) + (b.length - j) <= 1;
}
const KB = (D.kb || []).map(e => ({
  a: e.a, w: e.w || 1, x: e.x || '',
  words: (e.k || []).filter(k => k.indexOf(' ') < 0 && !/[^a-z0-9]/i.test(k)).map(k => stem(k.toLowerCase())),
  phrases: (e.k || []).filter(k => /[^a-z0-9]/i.test(k)).map(k => ' ' + words(k).map(stem).join(' ') + ' ')
}));
function answer(q) {
  const all = words(q).map(stem);
  const joined = ' ' + all.join(' ') + ' ';
  const toks = words(q).filter(t => !STOP.has(t)).map(stem);
  let best = null, bestScore = 0;
  for (const e of KB) {
    let s = 0;
    for (const p of e.phrases) if (joined.indexOf(p) >= 0) s += 3;
    for (const k of e.words) {
      if (toks.some(t => t === k || (t.length >= 6 && k.length >= 6 && lev1(t, k)))) s += 1;
    }
    s *= e.w;
    if (s > bestScore) { bestScore = s; best = e; }
  }
  return bestScore > 0 ? best : null;
}
function ask(text) {
  text = (text || '').trim(); if (!text) return;
  lastAct = Date.now(); wake();
  addMsg('u', text);
  const typing = addMsg('t', '\u2022\u2022\u2022', false);
  setTimeout(() => {
    typing.remove();
    const hit = answer(text);
    if (hit) {
      addMsg('s', hit.a);
      if (hit.x === 'dance') dance(3600); else jump();
    } else {
      addMsg('s', "Hmm, I'm not sure about that one \uD83E\uDD14 I know about the five ideas, savings, payback, CO\u2082, the SDGs, the investor page and the team. Try one of the buttons below, or ask in other words!");
    }
  }, 380);
}
function buildChips() {
  chipsEl.innerHTML = '';
  (D.chips || []).forEach(c => {
    const b = document.createElement('button'); b.type = 'button'; b.className = 'chip'; b.textContent = c;
    b.addEventListener('click', () => ask(c)); chipsEl.appendChild(b);
  });
}
function setOpen(o) {
  isOpen = o; store.open = o; save();
  document.body.classList.toggle('open', o);
  if (o) {
    clearTimeout(bubbleT); bubble.classList.add('hide'); bubbleOn = false;
    if (!store.msgs.length) addMsg('s', D.greeting || "Hi, I'm Sprig! Ask me anything about this dashboard.");
    msgs.scrollTop = msgs.scrollHeight;
    layout();
    if (!TOUCH) setTimeout(() => input.focus(), 60);
  } else { layout(); }
}
function toggle() { wake(); jump(); setOpen(!isOpen); }
ch.addEventListener('click', toggle);
$('badge').addEventListener('click', toggle);
bubble.addEventListener('click', () => { wake(); setOpen(true); });
$('pclose').addEventListener('click', () => setOpen(false));
$('pform').addEventListener('submit', e => { e.preventDefault(); const v = input.value; input.value = ''; ask(v); });
document.addEventListener('keydown', e => { lastAct = Date.now(); if (e.key === 'Escape' && isOpen) setOpen(false); });

/* ---------- eyes follow the cursor ---------- */
function track(e, local) {
  let ox = 0, oy = 0;
  if (!local) { try { const f = window.frameElement.getBoundingClientRect(); ox = f.left; oy = f.top; } catch (_) {} }
  const r = $('sp').getBoundingClientRect();
  const dx = Math.max(-1, Math.min(1, (e.clientX - ox - (r.left + r.width / 2)) / 160));
  const dy = Math.max(-1, Math.min(1, (e.clientY - oy - (r.top + r.height * 0.55)) / 160));
  const t = 'translate(' + (dx * 3.4).toFixed(2) + 'px,' + (dy * 2.6).toFixed(2) + 'px)';
  $('pL').style.transform = t; $('pR').style.transform = t;
  lastAct = Date.now();
  if (mood === 'sleepy') wake();
}
document.addEventListener('mousemove', e => track(e, true));
try {
  const P = window.parent;
  if (P.__sprigOff) P.__sprigOff();
  const h = e => track(e, false);
  P.document.addEventListener('mousemove', h);
  P.__sprigOff = () => P.document.removeEventListener('mousemove', h);
} catch (_) {}

/* ---------- life: blink, hop, occasional dance, nap ---------- */
(function blinkLoop() {
  setTimeout(() => {
    if (mood !== 'sleepy') { ch.classList.add('blink'); setTimeout(() => ch.classList.remove('blink'), 140); }
    blinkLoop();
  }, 2200 + Math.random() * 3200);
})();
if (!REDUCED) {
  (function hopLoop() {
    setTimeout(() => { if (mood !== 'sleepy' && !dancing && !isOpen) jump(); hopLoop(); }, 8000 + Math.random() * 4000);
  })();
  (function danceLoop() {
    setTimeout(() => { if (mood !== 'sleepy' && !isOpen && (base === 'excited' || Math.random() < .6)) dance(3600); danceLoop(); }, 38000 + Math.random() * 22000);
  })();
}
setInterval(() => {
  if (!isOpen && Date.now() - lastAct > 45000 && mood !== 'sleepy' && !dancing) {
    setMood('sleepy'); say('Zzz... tap me to wake me up!', true);
  }
}, 1000);

/* ---------- start ---------- */
buildChips();
setMood(D.mood);
store.msgs.forEach(m => addMsg(m.r, m.t, false));
if (store.open) setOpen(true); else { say(D.message); layout(); }
if (!store.seen) { store.seen = true; save(); setTimeout(() => dance(3600), 700); }
else if (!REDUCED) setTimeout(jump, 350);
</script></body></html>"""


def _page(mood, message, tips, knowledge, chips, greeting):
    data = json.dumps({"mood": mood, "message": message or "", "tips": list(tips or []),
                       "kb": list(knowledge or []), "chips": list(chips or []),
                       "greeting": greeting or ""})
    data = data.replace("</", "<\\/")
    return _TEMPLATE.replace("__SVG__", _SVG).replace("__DATA__", data)


def sprig(mood="happy", message="", tips=None, height=136, floating=True,
          knowledge=None, chips=None, greeting=""):
    """Draw Sprig. `message` shows in the speech bubble; click Sprig to open the chat.

    knowledge: list of {"k": [keywords/phrases], "a": answer, "w": weight, "x": "dance"} entries.
    chips: quick-question buttons shown under the chat. greeting: Sprig's first chat message.
    """
    mood = mood if mood in MOODS else "happy"
    html = _page(mood, message, tips, knowledge, chips, greeting)

    def draw():
        try:
            import streamlit.components.v1 as components
            components.html(html, height=height)
        except Exception:  # animation unavailable: show a still Sprig instead
            st.markdown(f'<div style="width:90px">{_SVG}</div>', unsafe_allow_html=True)
            if message:
                st.caption(message)

    if floating:
        st.markdown(FLOAT_CSS, unsafe_allow_html=True)
        with st.container(key="sprig"):
            draw()
    else:
        draw()
