"""Sprig - a small, cute, reusable mascot for Streamlit apps.

Copy this one file next to your app.py, then:

    import sprig
    sprig.sprig(mood="happy", message="Hi! I'm Sprig.", tips=["Tip one", "Tip two"])

Moods: "happy", "excited", "worried", "sleepy".
What Sprig does: blinks and hops by itself, its eyes follow your cursor, it jumps and
says a tip when clicked, shows hearts when you hover and pet it, spins on a double
click, gets dizzy if you click too fast, tells jokes and dances (buttons in its bubble),
and falls asleep (tap to wake) after 45 seconds of quiet.
Pass reaction="cheer" or "oops" to make it celebrate or wince when it appears.
Pass lang="ar" for Arabic. Pass floating=False to draw it inside the page instead of in the bottom-right corner.
"""
import html as _html
import json

import streamlit as st

MOODS = ("happy", "excited", "worried", "sleepy")

UI = {
    "en": {
        "tip": "💡 Tip", "joke": "😄 Joke", "dance": "💃 Dance", "title": "Click me!",
        "dance_msg": "Dance party!", "spin_msg": "Wheee!",
        "dizzy_msg": "Whoa... so dizzy! Please click slower.", "sleep_msg": "Zzz... tap me to wake me up!",
        "jokes": ["Why did the solar panel go to school? To get a little brighter!",
                  "Why is recycling so happy? Everything gets a second chance!",
                  "What did the plant say to the water drop? Thanks a bunch!",
                  "Why do windows never win races? They're always stuck in a frame!"],
        "love": ["Hehe, that tickles!", "Aww, thank you!", "You're the best!", "Pets make me so happy!"],
    },
    "ar": {
        "tip": "💡 نصيحة", "joke": "😄 نكتة", "dance": "💃 ارقص", "title": "اضغط عليّ!",
        "dance_msg": "حفلة رقص!", "spin_msg": "ييي!",
        "dizzy_msg": "واو... أشعر بالدوار! اضغط ببطء من فضلك.", "sleep_msg": "زززز... المسني لأستيقظ!",
        "jokes": ["لماذا ذهب اللوح الشمسي إلى المدرسة؟ ليصبح أكثر إشراقًا!",
                  "لماذا إعادة التدوير سعيدة؟ لأن كل شيء يحصل على فرصة ثانية!",
                  "ماذا قالت النبتة لقطرة الماء؟ شكرًا من كل قلبي... وجذوري!",
                  "لماذا لا تفوز النوافذ في السباق؟ لأنها دائمًا داخل إطار!"],
        "love": ["هههه، هذا يدغدغني!", "آه، شكرًا لك!", "أنت الأفضل!", "الحنان يسعدني كثيرًا!"],
    },
}

FLOAT_CSS = """<style>
.st-key-sprig {position: fixed; right: 14px; bottom: 6px; width: 370px; z-index: 9999;}
.st-key-sprig iframe {border: 0; background: transparent;}
</style>"""

# Everything except the face parts that change with mood is static.
_SVG = """<svg id="sp" viewBox="0 -8 120 140" role="img" aria-label="Sprig, a sprout-blob mascot">
<ellipse cx="60" cy="123" rx="30" ry="6" fill="#0B1B3F" opacity=".12"/>
<path d="M60 30V14" stroke="#2E8B57" stroke-width="4" stroke-linecap="round" fill="none"/>
<g class="leaf"><path d="M60 16C44 16 36 6 38 0C52 0 62 6 60 16Z" fill="#4DAA57"/></g>
<g class="leaf r"><path d="M60 16C76 16 84 6 82 0C68 0 58 6 60 16Z" fill="#F5A623"/></g>
<ellipse cx="17" cy="93" rx="6" ry="10" transform="rotate(25 17 93)" fill="#8EE3C8" stroke="#13A08A" stroke-width="3"/>
<ellipse cx="103" cy="93" rx="6" ry="10" transform="rotate(-25 103 93)" fill="#8EE3C8" stroke="#13A08A" stroke-width="3"/>
<path d="M60 28C92 28 104 56 102 82C100 108 82 119 60 119C38 119 20 108 18 82C16 56 28 28 60 28Z" fill="#8EE3C8" stroke="#13A08A" stroke-width="4"/>
<ellipse cx="60" cy="98" rx="22" ry="15" fill="#C6F3E4"/>
<g id="eyesO">
<g id="pL"><g class="eyeO"><ellipse cx="46" cy="68" rx="7" ry="9" fill="#0B1B3F"/><circle cx="48.5" cy="64" r="2.6" fill="#fff"/></g></g>
<g id="pR"><g class="eyeO"><ellipse cx="74" cy="68" rx="7" ry="9" fill="#0B1B3F"/><circle cx="76.5" cy="64" r="2.6" fill="#fff"/></g></g>
</g>
<g id="eyesC" style="display:none" fill="none" stroke="#0B1B3F" stroke-width="3.5" stroke-linecap="round"><path d="M39 70Q46 76 53 70"/><path d="M67 70Q74 76 81 70"/></g>
<g id="eyesD" style="display:none" fill="none" stroke="#0B1B3F" stroke-width="3"><circle class="swirl" cx="46" cy="68" r="7" stroke-dasharray="14 7"/><circle class="swirl" cx="74" cy="68" r="7" stroke-dasharray="14 7"/></g>
<g id="brows" style="display:none" fill="none" stroke="#0B1B3F" stroke-width="3" stroke-linecap="round"><path d="M38 57L54 62"/><path d="M82 57L66 62"/></g>
<ellipse class="cheek" cx="34" cy="82" rx="7" ry="4.5" fill="#FF9DB0"/><ellipse class="cheek" cx="86" cy="82" rx="7" ry="4.5" fill="#FF9DB0"/>
<path id="mHappy" d="M52 81Q60 91 68 81" stroke="#0B1B3F" stroke-width="3.5" fill="none" stroke-linecap="round"/>
<g id="mExcited" style="display:none"><path d="M50 79Q60 99 70 79Z" fill="#B83A5A" stroke="#0B1B3F" stroke-width="3" stroke-linejoin="round"/><path d="M55 90Q60 86 65 90Q60 94 55 90Z" fill="#FF9DB0"/></g>
<path id="mWorried" style="display:none" d="M53 88Q60 80 67 88" stroke="#0B1B3F" stroke-width="3.5" fill="none" stroke-linecap="round"/>
<path id="mDizzy" style="display:none" d="M50 86q5-5 10 0t10 0" stroke="#0B1B3F" stroke-width="3.5" fill="none" stroke-linecap="round"/>
<path id="mSleepy" style="display:none" d="M56 84Q60 87 64 84" stroke="#0B1B3F" stroke-width="3.5" fill="none" stroke-linecap="round"/>
<path d="M60 92l2.6 5.4 5.4 2.6-5.4 2.6-2.6 5.4-2.6-5.4-5.4-2.6 5.4-2.6z" fill="#F5A623"/>
<g id="sparks" style="display:none" fill="#F5A623"><path class="tw" d="M12 40l1.6 3.4 3.4 1.6-3.4 1.6-1.6 3.4-1.6-3.4-3.4-1.6 3.4-1.6z"/><path class="tw d2" d="M108 34l1.6 3.4 3.4 1.6-3.4 1.6-1.6 3.4-1.6-3.4-3.4-1.6 3.4-1.6z"/><path class="tw d3" d="M98 8l1.2 2.6 2.6 1.2-2.6 1.2-1.2 2.6-1.2-2.6-2.6-1.2 2.6-1.2z"/></g>
<g id="zzz" style="display:none" fill="#0B7A69" font-weight="800"><text class="zz" x="88" y="40" font-size="15">z</text><text class="zz d2" x="99" y="26" font-size="11">z</text></g>
<path id="drop" style="display:none" d="M97 50q5 8 0 11q-5-3 0-11z" fill="#7CC7FF"/>
</svg>"""

_TEMPLATE = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;background:transparent;font-family:'Nunito','Segoe UI',system-ui,sans-serif;overflow:hidden}
#wrap{display:flex;align-items:flex-end;justify-content:flex-end;gap:8px;height:100vh;padding:0 4px 2px 0;box-sizing:border-box}
#bubble{position:relative;background:#fff;border:2px solid #D7EFE9;color:#0B1B3F;border-radius:18px;padding:10px 14px;
 font-size:14px;line-height:1.35;max-width:230px;margin-bottom:44px;box-shadow:0 4px 14px rgba(11,27,63,.14);
 cursor:pointer;transition:opacity .25s,transform .25s}
#bubble.hide{opacity:0;transform:scale(.9);pointer-events:none}
#bubble:after{content:"";position:absolute;right:-9px;bottom:16px;border:8px solid transparent;border-left-color:#D7EFE9;border-right:0}
#char{width:112px;height:130px;flex-shrink:0;cursor:pointer;user-select:none;-webkit-tap-highlight-color:transparent;
 transform-origin:50% 100%;animation:breathe 3.2s ease-in-out infinite}
#char svg{width:100%;height:100%;overflow:visible;display:block}
#char.hop{animation:hop .7s ease-out}
@keyframes breathe{0%,100%{transform:scale(1,1)}50%{transform:scale(1.02,.98)}}
@keyframes hop{0%{transform:scale(1,1)}20%{transform:scale(1.1,.86)}45%{transform:translateY(-26px) scale(.94,1.08)}
 70%{transform:scale(1.08,.9)}100%{transform:scale(1,1)}}
.eyeO{transform-box:fill-box;transform-origin:center;transition:transform .08s}
#char.blink .eyeO{transform:scaleY(.1)}
#pL,#pR{transition:transform .12s ease-out}
.leaf{transform-box:fill-box;transform-origin:0% 100%;animation:sway 3.4s ease-in-out infinite}
.leaf.r{transform-origin:100% 100%;animation-delay:.6s}
@keyframes sway{0%,100%{transform:rotate(-5deg)}50%{transform:rotate(5deg)}}
.tw{transform-box:fill-box;transform-origin:center;animation:tw 1.4s ease-in-out infinite}
.d2{animation-delay:.45s}.d3{animation-delay:.9s}
@keyframes tw{0%,100%{opacity:0;transform:scale(.4)}50%{opacity:1;transform:scale(1.1)}}
.cheek{transform-box:fill-box;transform-origin:center;transition:transform .2s}
#char.love .cheek{transform:scale(1.45)}
.swirl{transform-box:fill-box;transform-origin:center;animation:swirl .7s linear infinite}
@keyframes swirl{to{transform:rotate(360deg)}}
#char.spin{animation:spin .85s ease-in-out}
@keyframes spin{0%{transform:translateY(0) rotate(0)}40%{transform:translateY(-30px) rotate(180deg)}100%{transform:translateY(0) rotate(360deg)}}
#char.dance{animation:dance 1.9s ease-in-out}
@keyframes dance{0%,100%{transform:rotate(0)}10%{transform:translateY(-14px) rotate(-10deg)}20%{transform:rotate(10deg)}30%{transform:translateY(-14px) rotate(-10deg)}
 40%{transform:rotate(10deg)}50%{transform:translateY(-22px) scale(1.06)}60%{transform:rotate(-8deg)}70%{transform:translateY(-14px) rotate(8deg)}85%{transform:rotate(-6deg)}}
#char.shake{animation:shake .6s ease-in-out}
@keyframes shake{0%,100%{transform:translateX(0)}20%{transform:translateX(-7px) rotate(-4deg)}40%{transform:translateX(7px) rotate(4deg)}60%{transform:translateX(-5px)}80%{transform:translateX(5px)}}
.p{position:fixed;width:8px;height:8px;border-radius:2px;pointer-events:none;z-index:5;animation:fly 1s ease-out forwards}
.p.h{width:auto;height:auto;font-size:15px;line-height:1;background:none!important}
@keyframes fly{0%{transform:translate(0,0) scale(1);opacity:1}100%{transform:translate(var(--dx),var(--dy)) scale(.6) rotate(200deg);opacity:0}}
#btns{display:flex;gap:6px;margin-top:8px}
#btns button{font:inherit;font-size:12px;font-weight:700;color:#0B1B3F;background:#E8F6F3;border:2px solid #CDE9E2;border-radius:999px;
 padding:3px 9px;cursor:pointer;transition:transform .12s,background .12s}
#btns button:hover{background:#13A08A;border-color:#13A08A;color:#fff;transform:scale(1.06)}
.zz{animation:zz 2.2s ease-in-out infinite}
@keyframes zz{0%{opacity:0;transform:translateY(6px)}50%{opacity:1}100%{opacity:0;transform:translateY(-6px)}}
</style></head><body>
<div id="wrap"><div id="bubble" role="status"><div id="msg"></div><div id="btns"><button id="bTip">💡 Tip</button><button id="bJoke">😄 Joke</button><button id="bDance">💃 Dance</button></div></div><div id="char" title="Click me!">__SVG__</div></div>
<script>
const D = __DATA__;
const $ = id => document.getElementById(id);
const bubble = $('bubble'), msg = $('msg'), ch = $('char');
const JOKES = D.ui.jokes, LOVE = D.ui.love;
$('bTip').textContent = D.ui.tip; $('bJoke').textContent = D.ui.joke; $('bDance').textContent = D.ui.dance;
$('char').title = D.ui.title;
if (D.lang === 'ar') { bubble.style.direction = 'rtl'; bubble.style.textAlign = 'right'; }
const COLORS = ['#F5A623', '#13A08A', '#FF9DB0', '#2F7FC1', '#4DAA57'];
let mood = D.mood, base = D.mood, tipIdx = 0, jokeIdx = 0, clicks = [], petTimer = null, lastAct = Date.now();

function show(id, on){ $(id).style.display = on ? '' : 'none'; }
function setMood(m){
  mood = m;
  const eyesOpen = m !== 'sleepy' && m !== 'dizzy';
  show('eyesO', eyesOpen); show('eyesC', m === 'sleepy'); show('eyesD', m === 'dizzy');
  show('brows', m === 'worried'); show('drop', m === 'worried');
  show('mHappy', m === 'happy'); show('mExcited', m === 'excited'); show('mWorried', m === 'worried');
  show('mSleepy', m === 'sleepy'); show('mDizzy', m === 'dizzy');
  show('sparks', m === 'excited' || m === 'dizzy'); show('zzz', m === 'sleepy');
}
function say(t){
  if (!t) { bubble.classList.add('hide'); return; }
  msg.textContent = t; bubble.classList.remove('hide');
}
function play(cls, ms){
  ch.classList.remove('hop', 'spin', 'dance', 'shake'); void ch.offsetWidth; ch.classList.add(cls);
  setTimeout(() => ch.classList.remove(cls), ms);
}
function jump(){ play('hop', 720); }
function burst(n, hearts){
  const r = ch.getBoundingClientRect();
  for (let i = 0; i < n; i++) {
    const p = document.createElement('div');
    p.className = hearts ? 'p h' : 'p';
    if (hearts) p.textContent = '💚'; else p.style.background = COLORS[i % COLORS.length];
    p.style.left = (r.left + r.width / 2) + 'px'; p.style.top = (r.top + r.height * 0.35) + 'px';
    const a = Math.random() * Math.PI * 2, d = 40 + Math.random() * 55;
    p.style.setProperty('--dx', (Math.cos(a) * d).toFixed(0) + 'px');
    p.style.setProperty('--dy', (hearts ? -(35 + Math.random() * 50) : Math.sin(a) * d - 15).toFixed(0) + 'px');
    document.body.appendChild(p); setTimeout(() => p.remove(), 1100);
  }
}
function wake(){
  lastAct = Date.now();
  if (mood === 'sleepy') { setMood(base); say(D.message); }
}
function backToBase(){ setMood(base === 'sleepy' ? 'happy' : base); }
function nextTip(){ say(D.tips.length ? D.tips[tipIdx++ % D.tips.length] : D.message); }
function dance(){
  wake(); play('dance', 1900); setMood('excited'); burst(14, false); say(D.ui.dance_msg);
  setTimeout(() => { if (mood === 'excited') backToBase(); }, 2000);
}
function dizzy(){
  setMood('dizzy'); play('shake', 900); say(D.ui.dizzy_msg);
  setTimeout(() => { backToBase(); say(D.message); }, 2800);
}

ch.addEventListener('click', () => {
  wake();
  const now = Date.now();
  clicks = clicks.filter(t => now - t < 3000); clicks.push(now);
  if (mood === 'dizzy') return;
  if (clicks.length >= 7) { clicks = []; dizzy(); return; }
  if (clicks.length >= 2 && now - clicks[clicks.length - 2] < 320) {
    play('spin', 850); burst(18, false); say(D.ui.spin_msg); return;
  }
  jump();
  if (base !== 'worried') { setMood('excited'); setTimeout(() => { if (mood === 'excited') setMood(base); }, 1800); }
  nextTip();
});
ch.addEventListener('mouseenter', () => {
  petTimer = setTimeout(() => {
    if (mood === 'sleepy' || mood === 'dizzy') return;
    ch.classList.add('love'); burst(5, true); say(LOVE[Math.floor(Math.random() * LOVE.length)]);
  }, 700);
});
ch.addEventListener('mouseleave', () => { clearTimeout(petTimer); ch.classList.remove('love'); });
msg.addEventListener('click', () => bubble.classList.add('hide'));
$('bTip').addEventListener('click', () => { wake(); jump(); nextTip(); });
$('bJoke').addEventListener('click', () => { wake(); jump(); say(JOKES[jokeIdx++ % JOKES.length]); });
$('bDance').addEventListener('click', dance);

function track(e, local){
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

(function blinkLoop(){
  setTimeout(() => {
    if (mood !== 'sleepy' && mood !== 'dizzy') { ch.classList.add('blink'); setTimeout(() => ch.classList.remove('blink'), 140); }
    blinkLoop();
  }, 2200 + Math.random() * 3200);
})();
(function hopLoop(){
  setTimeout(() => { if (mood !== 'sleepy' && mood !== 'dizzy') jump(); hopLoop(); }, 7000 + Math.random() * 4000);
})();
setInterval(() => {
  if (Date.now() - lastAct > 45000 && mood !== 'sleepy') { setMood('sleepy'); say(D.ui.sleep_msg); }
}, 1000);

setMood(D.mood); say(D.message);
if (D.reaction === 'cheer') setTimeout(() => { play('spin', 850); burst(24, false); }, 300);
else if (D.reaction === 'oops') setTimeout(() => play('shake', 600), 300);
else setTimeout(jump, 350);
</script></body></html>"""


def _page(mood, message, tips, reaction=None, lang="en"):
    lang = lang if lang in UI else "en"
    data = json.dumps({"mood": mood, "message": message or "", "tips": list(tips or []),
                       "reaction": reaction or "", "lang": lang, "ui": UI[lang]})
    data = data.replace("</", "<\\/")
    page = _TEMPLATE.replace("__SVG__", _SVG).replace("__DATA__", data)
    return page.replace('<div id="msg"></div>', '<div id="msg">' + _html.escape(message or "") + "</div>")


MODE = "none"  # how Sprig was last drawn: "iframe", "components" or "still"


def _draw_html(html, height):
    """Draw the animated Sprig with whichever Streamlit command this version supports."""
    global MODE
    if hasattr(st, "iframe"):  # newer Streamlit (st.components.v1.html is being removed)
        try:
            st.iframe(html, height=height)
            MODE = "iframe"
            return True
        except Exception:
            pass
    try:  # older Streamlit
        import streamlit.components.v1 as components
        components.html(html, height=height)
        MODE = "components"
        return True
    except Exception:
        return False


def sprig(mood="happy", message="", tips=None, height=215, floating=True, reaction=None, lang="en"):
    """Draw Sprig. `message` is plain text shown in the speech bubble; `tips` cycle on each click."""
    global MODE
    mood = mood if mood in MOODS else "happy"
    html = _page(mood, message, tips, reaction, lang)

    def draw():
        global MODE
        if not _draw_html(html, height):  # animation unavailable: show a still Sprig instead
            MODE = "still"
            st.markdown(f'<div style="width:110px">{_SVG}</div>', unsafe_allow_html=True)
            if message:
                st.caption(message)

    if floating:
        st.markdown(FLOAT_CSS, unsafe_allow_html=True)
        with st.container(key="sprig"):
            draw()
    else:
        draw()
