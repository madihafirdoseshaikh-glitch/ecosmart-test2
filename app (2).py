import altair as alt
import pandas as pd
import streamlit as st

try:
    import i18n
    import models as m
    import sprig
except ImportError as _e:  # a helper file was not uploaded with the right name
    st.error(f"A file is missing or misnamed: {_e}. Upload app.py, models.py, sprig.py and i18n.py "
             "with exactly these names (no (1) or (2) in the name).")
    st.stop()

st.set_page_config(page_title="EcoSmart Smart Campus Dashboard", page_icon="🌿", layout="wide")

# ------------------------------------------------------------------ language (English / Arabic)
if "lang" not in st.session_state:
    try:  # a link ending in ?lang=ar opens the dashboard in Arabic
        _q = st.query_params.get("lang")
    except Exception:
        _q = None
    st.session_state["lang"] = _q if _q in ("en", "ar") else "en"
st.sidebar.radio("🌐 Language / اللغة", ["en", "ar"], format_func=lambda k: {"en": "English", "ar": "العربية"}[k],
                 horizontal=True, key="lang")
LANG = st.session_state["lang"]
AR = LANG == "ar"
t = i18n.make_t(LANG)


def tm(text):
    """Translate a fixed phrase produced by models.py."""
    return i18n.MODEL_AR.get(text, text) if AR else text


# ------------------------------------------------------------------ look and feel
NAVY, TEAL, AMBER = "#0B1B3F", "#13A08A", "#F5A623"
FONT = "'Cairo', 'Nunito', sans-serif" if AR else "'Nunito', sans-serif"
NAV_IDS = ["overview", "windows", "monitoring", "solar", "recycling", "irrigation", "investor"]
EMOJI = {"overview": "🏠", "windows": "🪟", "monitoring": "📡", "solar": "☀️", "recycling": "♻️",
         "irrigation": "💧", "investor": "💼"}
COLOR = {"windows": "#2F7FC1", "monitoring": "#F5A623", "solar": "#E4572E",
         "recycling": "#4DAA57", "irrigation": "#13A08A"}
TINT = {"windows": "#E8F2FB", "monitoring": "#FFF3DC", "solar": "#FDE6E0",
        "recycling": "#E7F5E9", "irrigation": "#DDF4F0"}
PREFIX = {"windows": "w_", "monitoring": "m_", "solar": "s_", "recycling": "r_", "irrigation": "i_"}


def nav_label(k):
    return f"{EMOJI[k]}  {t('nav_' + k)}"


def idea_name(key):
    return t("nav_" + key)


st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;800&family=Cairo:wght@400;700;800&display=swap');
  .stApp, .stMarkdown, button, input, label, textarea {{font-family: {FONT};}}
  #MainMenu, footer {{visibility: hidden;}}
  .block-container {{padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1280px;}}
  section[data-testid="stSidebar"] {{border-right: 2px dashed #CDE9E2;}}
  section[data-testid="stSidebar"] h1 {{font-size: 1.4rem; color: {NAVY};}}
  @keyframes floaty {{0%,100% {{transform: translateY(0) rotate(-4deg);}} 50% {{transform: translateY(-10px) rotate(6deg);}}}}
  @keyframes bounce {{0%,100% {{transform: translateY(0);}} 50% {{transform: translateY(-8px);}}}}
  @keyframes pop {{0% {{transform: scale(.92); opacity: 0;}} 100% {{transform: scale(1); opacity: 1;}}}}
  .hero {{position: relative; overflow: hidden; border-radius: 28px; padding: 26px 34px; margin-bottom: 14px;
          color: {NAVY}; border: 3px solid white; box-shadow: 0 6px 24px rgba(19,160,138,.18);
          animation: pop .4s ease-out;}}
  .hero h1 {{margin: 0; font-size: 2.1rem; font-weight: 800; color: {NAVY}; padding: 0;}}
  .hero p {{margin: 6px 0 0 0; font-size: 1.08rem; color: #34466E; max-width: 70%;}}
  .hero .pill {{display: inline-block; padding: 3px 14px; border-radius: 999px; font-size: .78rem; font-weight: 800;
               background: white; color: {TEAL}; margin-bottom: 10px; letter-spacing: .05em;}}
  .hero .fl {{position: absolute; font-size: 2.2rem; animation: floaty 4s ease-in-out infinite; opacity: .9;}}
  .mascot {{display: flex; align-items: center; gap: 14px; margin: 4px 0 18px 0;}}
  .mascot .face {{font-size: 2.6rem; background: white; border-radius: 50%; width: 74px; height: 74px;
                 display: flex; align-items: center; justify-content: center; flex-shrink: 0;
                 box-shadow: 0 4px 14px rgba(11,27,63,.12); animation: bounce 2.4s ease-in-out infinite;}}
  .mascot .bubble {{position: relative; background: white; border-radius: 20px; padding: 12px 18px; color: {NAVY};
                   box-shadow: 0 4px 14px rgba(11,27,63,.10); font-size: 1.02rem; border: 2px solid #D7EFE9;}}
  .mascot .bubble:before {{content: ""; position: absolute; left: -10px; top: 24px; border: 8px solid transparent;
                          border-right-color: #D7EFE9; border-left: 0;}}
  .mascot .name {{font-weight: 800; color: {TEAL};}}
  .kpi, .card, .step, .fact {{transition: transform .18s ease, box-shadow .18s ease;}}
  .kpi:hover, .card:hover, .step:hover, .fact:hover {{transform: translateY(-4px); box-shadow: 0 10px 22px rgba(11,27,63,.14);}}
  .kpi {{background: white; border-radius: 20px; padding: 14px 18px; min-height: 108px;
         box-shadow: 0 3px 14px rgba(11,27,63,.08); margin-bottom: 12px;}}
  .kpi-label {{font-size: .8rem; color: #5B6B8C; text-transform: uppercase; letter-spacing: .05em; font-weight: 700;}}
  .kpi-value {{font-size: 1.65rem; font-weight: 800; color: {NAVY}; line-height: 1.25; margin-top: 4px;}}
  .kpi-sub {{font-size: .85rem; color: #5B6B8C; margin-top: 2px;}}
  .plain {{background: #E8F6F3; border: 2px solid #CDE9E2; border-radius: 20px;
          padding: 14px 20px; font-size: 1.05rem; color: {NAVY}; margin: 6px 0 14px 0;}}
  .best {{background: #FFF6E3; border: 2px solid #FBE3B0; border-radius: 20px;
         padding: 14px 20px; font-size: 1.05rem; color: {NAVY}; margin: 6px 0 14px 0;}}
  .card {{background: white; border-radius: 22px; padding: 16px 18px; min-height: 140px;
         box-shadow: 0 3px 14px rgba(11,27,63,.08); margin-bottom: 8px;}}
  .card h4 {{margin: 4px 0 2px 0; font-size: 1.02rem; color: {NAVY};}}
  .card .big {{font-size: 1.4rem; font-weight: 800; color: {NAVY};}}
  .card .small {{font-size: .85rem; color: #5B6B8C;}}
  .fact {{background: white; border-radius: 22px; padding: 14px 10px; text-align: center;
         box-shadow: 0 3px 14px rgba(11,27,63,.08); margin-bottom: 12px;}}
  .fact .e {{font-size: 2.1rem;}} .fact .n {{font-size: 1.5rem; font-weight: 800; color: {NAVY};}}
  .fact .t {{font-size: .82rem; color: #5B6B8C;}}
  .step {{background: white; border-radius: 20px; padding: 14px 18px; box-shadow: 0 3px 14px rgba(11,27,63,.08);}}
  .step b {{color: {TEAL};}}
  .small {{font-size: .85rem; color: #5B6B8C;}}
  .stButton > button {{border-radius: 999px; border: 2px solid {TEAL}; background: white; color: {NAVY};
                      font-weight: 800; transition: all .15s ease;}}
  .stButton > button:hover {{background: {TEAL}; color: white; border-color: {TEAL}; transform: scale(1.04);}}
  div[data-testid="stTabs"] button {{font-size: 1rem; font-weight: 700;}}
</style>
""", unsafe_allow_html=True)

if AR:
    st.markdown("""<style>
  .stApp, section[data-testid="stSidebar"] {direction: rtl;}
  section[data-testid="stSidebar"] {border-right: none; border-left: 2px dashed #CDE9E2;}
  div[data-testid="stTabs"] [role="tablist"] {direction: rtl;}
</style>""", unsafe_allow_html=True)

# Keep every input alive when the user switches panels (Streamlit drops widgets that are not shown).
for _k, _v in m.DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v
    else:
        st.session_state[_k] = st.session_state[_k]
if "page" not in st.session_state:
    st.session_state["page"] = "overview"
for _key, _ in m.IDEAS:
    if f"on_{_key}" not in st.session_state:
        st.session_state[f"on_{_key}"] = True
    else:
        st.session_state[f"on_{_key}"] = st.session_state[f"on_{_key}"]
if "sprig_on" not in st.session_state:
    st.session_state["sprig_on"] = True
else:
    st.session_state["sprig_on"] = st.session_state["sprig_on"]
if "sprig_corner" not in st.session_state:
    st.session_state["sprig_corner"] = "br"
else:
    st.session_state["sprig_corner"] = st.session_state["sprig_corner"]
if "look_years" not in st.session_state:
    st.session_state["look_years"] = 10
else:
    st.session_state["look_years"] = st.session_state["look_years"]


# ------------------------------------------------------------------ helpers
def aed(x):
    return f"{x:,.0f} درهم" if AR else f"AED {x:,.0f}"


def years_text(x):
    return t("never") if x == float("inf") else f"{x:.1f} {t('u_years')}"


def go(page):
    st.session_state["page"] = page


def reset(prefix):
    for k, v in m.DEFAULTS.items():
        if k.startswith(prefix):
            st.session_state[k] = v
    st.toast(t("toast_reset"))


def set_plan(keys):
    for k, _ in m.IDEAS:
        st.session_state[f"on_{k}"] = k in keys


def hero(title, subtitle, pill="", tint="#D8F3EA", emojis=("🌿", "☀️", "💧")):
    badge = f'<div class="pill">{pill}</div><br>' if pill else ""
    side = "left" if AR else "right"
    fl = "".join(f'<span class="fl" style="{side}:{4 + i * 9}%;top:{14 + (i % 2) * 34}%;'
                 f'animation-delay:{i * .7}s">{e}</span>' for i, e in enumerate(emojis))
    st.markdown(f'<div class="hero" style="background:linear-gradient(120deg,{tint} 0%,#FFFFFF 120%)">'
                f'{fl}{badge}<h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


SPRIG = {"mood": "happy", "message": "", "tips": [], "reaction": None}


def mascot(mood, text, tips=None, page=None, value=None):
    """Tell Sprig how to feel and what to say; it is drawn once at the end of the script.
    If `value` changes since the last run on this page, Sprig cheers (up) or winces (down)."""
    tips, reaction = list(tips or []), None
    if page is not None and value is not None:
        last = st.session_state.setdefault("_last_val", {})
        prev = last.get(page)
        last[page] = value
        if prev is not None and abs(value - prev) >= 1:
            d = value - prev
            tips = [text] + tips
            if d > 0:
                mood, reaction, text = "excited", "cheer", t("rx_up", d=f"{d:,.0f}")
            else:
                mood, reaction, text = "worried", "oops", t("rx_down", d=f"{-d:,.0f}")
    SPRIG.update(mood=mood, message=text, tips=tips, reaction=reaction)


def fun_facts(co2, kwh, water, waste):
    items = []
    if kwh > 0:
        items.append(("💡", f"{kwh / 87.6:,.0f}", t("f_bulbs")))
    if co2 > 0:
        items.append(("🌳", f"{co2 * 1000 / 21:,.0f}", t("f_trees")))
    if water > 0:
        items.append(("🏊", f"{water / 2500:,.1f}", t("f_pools")))
    if waste > 0:
        items.append(("🐘", f"{waste / 6:,.0f}", t("f_elephants")))
    if items:
        for col, (e, n, text) in zip(st.columns(len(items)), items):
            col.markdown(f'<div class="fact"><div class="e">{e}</div><div class="n">{n}</div>'
                         f'<div class="t">{text}</div></div>', unsafe_allow_html=True)


def kpi_row(items):
    """items: (label, value, sub, accent colour)"""
    cols = st.columns(len(items))
    for col, (label, value, sub, accent) in zip(cols, items):
        col.markdown(
            f'<div class="kpi" style="border-inline-start:6px solid {accent}">'
            f'<div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>'
            f'<div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)


def show(chart):
    try:
        st.altair_chart(chart, width="stretch")
    except TypeError:  # older Streamlit versions
        st.altair_chart(chart, use_container_width=True)


def bars(labels, values, colors, fmt=",.0f", horizontal=False, height=300):
    df = pd.DataFrame({"label": labels, "value": values})
    colour = alt.Color("label:N", scale=alt.Scale(domain=labels, range=colors), legend=None)
    if horizontal:
        base = alt.Chart(df).encode(
            y=alt.Y("label:N", sort=None, title=None, axis=alt.Axis(labelLimit=220)),
            x=alt.X("value:Q", title=None))
        bar = base.mark_bar(cornerRadiusTopRight=8, cornerRadiusBottomRight=8, size=26).encode(color=colour)
        text = base.mark_text(align="left", dx=6, fontWeight="bold", color=NAVY) \
            .encode(text=alt.Text("value:Q", format=fmt))
    else:
        base = alt.Chart(df).encode(
            x=alt.X("label:N", sort=None, title=None, axis=alt.Axis(labelAngle=0, labelLimit=180)),
            y=alt.Y("value:Q", title=None))
        bar = base.mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8, size=70).encode(color=colour)
        text = base.mark_text(dy=-9, fontWeight="bold", color=NAVY) \
            .encode(text=alt.Text("value:Q", format=fmt))
    show((bar + text).properties(height=height))


def money_chart(values, color, look=None):
    """Cumulative money over time; `values` has one number per year starting at year 0."""
    df = pd.DataFrame({"Year": list(range(len(values))), "AED": values})
    area = alt.Chart(df).mark_area(opacity=0.25, color=color, line={"color": color, "strokeWidth": 3}) \
        .encode(x=alt.X("Year:Q", title=t("ax_years")),
                y=alt.Y("AED:Q", title=t("ax_aed_cum"), axis=alt.Axis(format="~s")))
    zero = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color=NAVY, strokeDash=[5, 5]).encode(y="y:Q")
    layers = area + zero
    if look is not None:
        layers = layers + alt.Chart(pd.DataFrame({"x": [look]})).mark_rule(color=AMBER, strokeWidth=3).encode(x="x:Q")
    show(layers.properties(height=280))


def sb_number(label, key, min_value, step, help=None):
    return st.sidebar.number_input(label, min_value=min_value, step=step, key=key, help=help)


def headline(key):
    p = P
    if key == "windows":
        pct = (p["w_peak_base"] - p["w_peak_new"]) / p["w_peak_base"] * 100 if p["w_peak_base"] else 0
        return t("hl_windows", pct=f"{max(pct, 0):.0f}")
    if key == "monitoring":
        return t("hl_monitoring", n=f"{p['m_rooms']:.0f}")
    if key == "solar":
        return t("hl_solar", kwp=f"{p['s_spaces'] * p['s_kwp_space']:,.0f}", n=f"{p['s_spaces']:.0f}")
    if key == "recycling":
        return t("hl_recycling", n=f"{p['r_div_new'] - p['r_div_base']:.0f}")
    return t("hl_irrigation", n=f"{p['i_save']:.0f}")


# ------------------------------------------------------------------ sidebar
st.sidebar.title("🌿 " + t("app_name"))
st.sidebar.caption(t("app_caption"))
st.sidebar.radio("Go to", NAV_IDS, format_func=nav_label, key="page", label_visibility="collapsed")
page = st.session_state["page"]
st.sidebar.divider()

if page in PREFIX:
    st.sidebar.subheader(f"{EMOJI[page]} {t('sb_inputs')}")
if page == "windows":
    sb_number(t("in_w_base"), "w_peak_base", 0.0, 0.5)
    sb_number(t("in_w_new"), "w_peak_new", 0.0, 0.5)
    sb_number(t("in_w_hours"), "w_hours", 0, 50, t("help_w_hours"))
    sb_number(t("in_w_capex"), "w_capex", 0, 1000, t("help_placeholder"))
elif page == "monitoring":
    sb_number(t("in_m_rooms"), "m_rooms", 0, 1)
    sb_number(t("in_m_kw"), "m_kw", 0.0, 0.1)
    sb_number(t("in_m_hours"), "m_hours", 0, 25)
    st.sidebar.slider(t("in_m_eff"), 0, 100, key="m_eff")
    sb_number(t("in_m_cost"), "m_cost_room", 0, 50, t("help_m_cost"))
    sb_number(t("in_m_hub"), "m_hub", 0, 500)
elif page == "solar":
    sb_number(t("in_s_spaces"), "s_spaces", 0, 5)
    sb_number(t("in_s_kwp"), "s_kwp_space", 0.0, 0.1)
    sb_number(t("in_s_yield"), "s_yield", 0, 20)
    sb_number(t("in_s_cost"), "s_cost_kwp", 0, 100, t("help_placeholder"))
elif page == "recycling":
    sb_number(t("in_r_waste"), "r_waste", 0.0, 10.0)
    st.sidebar.slider(t("in_r_base"), 0.0, 100.0, step=1.0, key="r_div_base")
    st.sidebar.slider(t("in_r_new"), 0.0, 100.0, step=1.0, key="r_div_new")
    sb_number(t("in_r_bins"), "r_bins", 0, 1)
    sb_number(t("in_r_cost"), "r_cost_bin", 0, 250)
elif page == "irrigation":
    sb_number(t("in_i_l"), "i_l_day", 0, 1000)
    st.sidebar.slider(t("in_i_save"), 0.0, 100.0, step=1.0, key="i_save")
    sb_number(t("in_i_days"), "i_days", 0, 5)
    sb_number(t("in_i_sensors"), "i_sensors", 0, 1)
    sb_number(t("in_i_cost"), "i_cost_sensor", 0, 50)
    sb_number(t("in_i_ctrl"), "i_ctrl", 0, 500)
elif page == "overview":
    st.sidebar.info(t("info_overview"))
elif page == "investor":
    st.sidebar.info(t("info_investor"))

if page in PREFIX:
    st.sidebar.button(t("btn_reset"), on_click=reset, args=(PREFIX[page],))

st.sidebar.toggle(t("tg_sprig"), key="sprig_on")
if st.session_state["sprig_on"]:
    st.sidebar.radio(t("sprig_pos"), ["br", "bl", "tr", "tl"], horizontal=True, key="sprig_corner",
                     format_func=lambda k: {"br": "↘", "bl": "↙", "tr": "↗", "tl": "↖"}[k])

with st.sidebar.expander(t("exp_global")):
    st.number_input(t("g_elec"), min_value=0.0, step=0.01, key="g_elec_tariff")
    st.number_input(t("g_water"), min_value=0.0, step=0.5, key="g_water_tariff")
    st.number_input(t("g_landfill"), min_value=0.0, step=10.0, key="g_landfill_fee")
    st.number_input(t("g_recycle"), min_value=0.0, step=10.0, key="g_recycle_rev")
    st.slider(t("g_vat"), 0.0, 20.0, step=0.5, key="g_vat")
    st.number_input(t("g_co2"), min_value=0.0, step=0.01, key="g_co2")
    st.slider(t("g_om"), 0.0, 10.0, step=0.5, key="g_om")
    st.slider(t("g_years"), 1, 25, key="g_years")
    st.caption(t("g_note"))

P = {k: st.session_state[k] for k in m.DEFAULTS}
R = m.all_results(P)
for _k, _r in R.items():
    _r.setdefault("key", _k)
YEARS = P["g_years"]


# ------------------------------------------------------------------ pages
def overview():
    hero(t("app_title"), t("ov_sub"), t("ov_pill"), "#D8F3EA", ("🌿", "☀️", "💧", "♻️"))

    on = [k for k, _ in m.IDEAS if st.session_state[f"on_{k}"]]
    plan_value = sum(R[k]["annual_saving"] for k in on)
    tips = i18n.pick(i18n.OVERVIEW_TIPS, LANG)
    if not on:
        mascot("worried", t("ov_msg_none"), tips, "overview", plan_value)
    elif len(on) == 5:
        mascot("excited", t("ov_msg_all"), tips, "overview", plan_value)
    else:
        mascot("happy", t("ov_msg_some", n=len(on)), tips, "overview", plan_value)

    st.subheader(t("ov_build"))
    p1, p2, p3 = st.columns(3)
    p1.button(t("preset_starter"), on_click=set_plan, args=(["monitoring", "irrigation", "recycling"],))
    p2.button(t("preset_balanced"), on_click=set_plan, args=(["windows", "monitoring", "recycling", "irrigation"],))
    p3.button(t("preset_max"), on_click=set_plan, args=([k for k, _ in m.IDEAS],))

    cols = st.columns(5)
    for col, (key, _) in zip(cols, m.IDEAS):
        r = R[key]
        dim = "" if key in on else "opacity:.45;filter:grayscale(.6);"
        col.markdown(
            f'<div class="card" style="background:{TINT[key]};border-top:6px solid {COLOR[key]};{dim}">'
            f'<div style="font-size:1.8rem">{EMOJI[key]}</div><h4>{idea_name(key)}</h4>'
            f'<div class="big">{aed(r["annual_saving"])}</div>'
            f'<div class="small">{t("card_saved", hl=headline(key))}</div></div>', unsafe_allow_html=True)
        col.toggle(t("include"), key=f"on_{key}")
        col.button(t("open_btn"), key=f"open_{key}", on_click=go, args=(key,))

    sel = {k: R[k] for k in on}
    if not sel:
        return
    tot = lambda f: sum(r[f] for r in sel.values())
    capex, net = tot("capex"), tot("net_annual")
    ky = t("k_every_year")

    st.subheader(t("ov_together"))
    kpi_row([(t("k_energy"), f"{tot('energy_kwh'):,.0f} {t('u_kwh')}", ky, "#F5A623"),
             (t("k_co2"), f"{tot('co2_t'):,.1f} {t('u_t')}", ky, TEAL),
             (t("k_water"), f"{tot('water_m3'):,.0f} {t('u_m3')}", ky, "#2F7FC1"),
             (t("k_waste"), f"{tot('waste_t'):,.1f} {t('u_t')}", ky, "#4DAA57")])
    kpi_row([(t("k_annual"), aed(tot("annual_saving")), t("k_after_tax"), TEAL),
             (t("k_equip"), aed(capex), t("k_ideas_on", n=len(sel)), NAVY),
             (t("k_payback"), years_text(capex / net if net > 0 else float("inf")), t("k_payback_sub"), AMBER),
             (t("k_netn", y=YEARS), aed(net * YEARS - capex), t("k_netn_sub"), "#4DAA57")])

    st.subheader(t("ov_facts"))
    fun_facts(tot("co2_t"), tot("energy_kwh"), tot("water_m3"), tot("waste_t"))

    st.subheader(t("ov_time"))
    look = st.slider(t("time_slider"), 1, 25, key="look_years")
    money = net * look - capex
    kpi_row([(t("k_money_after"), aed(money), t("k_after_years", n=look), TEAL if money >= 0 else "#E4572E"),
             (t("k_co2_sofar"), f"{tot('co2_t') * look:,.0f} {t('u_t')}", t("k_added"), "#13A08A"),
             (t("k_trees_worth"), f"{tot('co2_t') * look * 1000 / 21:,.0f}", t("k_about"), "#4DAA57")])
    money_chart([net * y - capex for y in range(26)], TEAL, look)

    if st.button(t("btn_celebrate")):
        st.balloons()
    st.caption(t("ov_caption"))


def idea_page(key):
    r, color = R[key], COLOR[key]
    hero(f"{EMOJI[key]} {idea_name(key)}", t("desc_" + key), t("idea_pill"), TINT[key], (EMOJI[key], "✨", "🌿"))

    tip_args = {
        "windows": dict(pct=f"{(P['w_peak_base'] - P['w_peak_new']) / P['w_peak_base'] * 100 if P['w_peak_base'] else 0:.0f}"),
        "monitoring": dict(n=f"{P['m_rooms']:.0f}"),
        "solar": dict(kwh=f"{r['energy_kwh']:,.0f}"),
        "recycling": dict(new=f"{P['r_div_new']:.0f}", base=f"{P['r_div_base']:.0f}"),
        "irrigation": dict(m3=f"{r['water_m3']:,.0f}"),
    }
    mood = "excited" if r["payback"] <= 3 else "happy" if r["payback"] <= 10 else "worried"
    mascot(mood, t("tip_" + key, **tip_args[key]), i18n.pick(i18n.IDEA_TIPS[key], LANG), key, r["annual_saving"])

    kpi_row([(t("k_annual"), aed(r["annual_saving"]), t("k_after_tax"), color),
             (t("k_equip"), aed(r["capex"]), t("k_incl_tax"), NAVY),
             (t("k_payback"), years_text(r["payback"]), t("k_payback_sub"), AMBER),
             (t("k_netn", y=YEARS), aed(r["net_period"]), t("k_netn_sub"), "#4DAA57")])

    ky = t("k_every_year")
    impacts = [(t("k_energy"), f"{r['energy_kwh']:,.0f} {t('u_kwh')}", ky, r["energy_kwh"]),
               (t("k_co2"), f"{r['co2_t']:,.1f} {t('u_t')}", ky, r["co2_t"]),
               (t("k_water"), f"{r['water_m3']:,.0f} {t('u_m3')}", ky, r["water_m3"]),
               (t("k_waste_kept"), f"{r['waste_t']:,.1f} {t('u_t')}", ky, r["waste_t"])]
    kpi_row([(a, b, c, color) for a, b, c, v in impacts if v > 0] or [("–", "–", "", color)])

    st.markdown(f'<div class="plain">{t("plain", saving=aed(r["annual_saving"]), capex=aed(r["capex"]), payback=years_text(r["payback"]))}</div>',
                unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([t("tab_before"), t("tab_facts"), t("tab_cost"), t("tab_investor")])
    with tab1:
        ch = r["chart"]
        st.subheader(tm(ch["title"]))
        bars([tm(x) for x in ch["labels"]], ch["values"], ["#B8C4DA", color])
    with tab2:
        st.subheader(t("facts_hdr"))
        fun_facts(r["co2_t"], r["energy_kwh"], r["water_m3"], r["waste_t"])
        st.caption(t("facts_cap"))
    with tab3:
        left, right = st.columns(2)
        with left:
            st.markdown("**" + t("tbl_saved") + "**")
            st.dataframe(pd.DataFrame([{
                t("col_item"): tm(x["Item"]),
                t("col_qty"): f"{x['Quantity']:,.1f} {tm(x['Unit'])}",
                t("col_rate"): f"{x['Rate']:,.2f} {tm(x['Rate unit'])}",
                t("col_amount"): f"{x['Amount (AED)']:,.0f}",
            } for x in r["rows"]]), hide_index=True)
        with right:
            st.markdown("**" + t("tbl_net") + "**")
            st.dataframe(pd.DataFrame([
                {t("col_line"): t("ln_before"), t("col_aed_year"): f"{r['subtotal']:,.0f}"},
                {t("col_line"): t("ln_tax", p=f"{P['g_vat']:.1f}"), t("col_aed_year"): f"{r['tax']:,.0f}"},
                {t("col_line"): t("ln_annual"), t("col_aed_year"): f"{r['annual_saving']:,.0f}"},
                {t("col_line"): t("ln_upkeep"), t("col_aed_year"): f"−{r['upkeep']:,.0f}"},
                {t("col_line"): t("ln_net"), t("col_aed_year"): f"{r['net_annual']:,.0f}"},
            ]), hide_index=True)
    with tab4:
        pb, yr = years_text(r["payback"]), f"{r['yearly_return']:.0f}"
        if r["payback"] <= 3:
            st.success(t("v_fast", pb=pb, yr=yr))
        elif r["payback"] <= 7:
            st.info(t("v_mod", pb=pb, yr=yr))
        else:
            st.warning(t("v_slow", pb=pb))
        st.markdown(t("money_over"))
        money_chart([-r["capex"] + r["net_annual"] * y for y in range(YEARS + 1)], color)


def investor():
    hero(t("inv_title"), t("inv_sub"), t("inv_pill"), "#FFF1D6", ("💰", "📈", "🌍"))
    c1, c2 = st.columns(2)
    c1.selectbox(t("rank_by"), list(m.RANKINGS), key="c_rank",
                 format_func=lambda k: i18n.RANK_AR.get(k, k) if AR else k)
    c2.number_input(t("budget"), min_value=0, step=50000, key="c_budget")
    field, ascending = m.RANKINGS[st.session_state["c_rank"]]
    ranked = sorted(R.values(), key=lambda r: r[field], reverse=not ascending)

    best = ranked[0]
    mascot("happy", t("inv_msg", name=idea_name(best["key"])), i18n.pick(i18n.INVESTOR_TIPS, LANG))
    co2_txt = f"{best['co2_t']:,.1f}"
    st.markdown(f'<div class="best">{t("inv_best", name=idea_name(best["key"]), pb=years_text(best["payback"]), net=aed(best["net_annual"]), co2=co2_txt)}</div>',
                unsafe_allow_html=True)

    medals = ["🥇", "🥈", "🥉", "4", "5"]
    st.dataframe(pd.DataFrame([{
        t("col_rank"): medals[i],
        t("col_idea"): f"{EMOJI[r['key']]} {idea_name(r['key'])}",
        t("col_equip"): f"{r['capex']:,.0f}",
        t("col_net"): f"{r['net_annual']:,.0f}",
        t("col_payback"): years_text(r["payback"]),
        t("col_netn", y=YEARS): f"{r['net_period']:,.0f}",
        t("col_yret"): f"{r['yearly_return']:.0f}%",
        t("col_co2"): f"{r['co2_t']:,.1f}",
    } for i, r in enumerate(ranked)]), hide_index=True)

    names = [idea_name(r["key"]) for r in ranked]
    colors = [COLOR[r["key"]] for r in ranked]
    a, b = st.columns(2)
    with a:
        st.subheader(t("ch_net"))
        bars(names, [r["net_annual"] for r in ranked], colors, horizontal=True, height=260)
    with b:
        st.subheader(t("ch_payback"))
        bars(names, [round(min(r["payback"], 99), 1) for r in ranked], colors, fmt=".1f",
             horizontal=True, height=260)

    st.subheader(t("inv_budget_hdr"))
    chosen, left = m.pick_portfolio(R, st.session_state["c_budget"])
    if not chosen:
        st.warning(t("inv_none"))
    else:
        st.write(t("inv_funded", names=("، " if AR else ", ").join(f"{EMOJI[r['key']]} {idea_name(r['key'])}" for r in chosen)))
        kpi_row([(t("k_invested"), aed(sum(r["capex"] for r in chosen)), t("k_equip_sub"), NAVY),
                 (t("ln_net"), aed(sum(r["net_annual"] for r in chosen)), t("k_net_sub"), TEAL),
                 (t("k_left"), aed(left), t("k_notspent"), AMBER)])
        if st.button(t("btn_celebrate_plan")):
            st.balloons()
    st.caption(t("inv_caption"))


def toggle_lang():
    st.session_state["lang"] = "en" if st.session_state["lang"] == "ar" else "ar"


# A language button at the top of every page, so phone visitors (sidebar hidden) can find it too.
_top = st.columns([1, 5]) if AR else st.columns([5, 1])
_top[0 if AR else 1].button("English" if AR else "العربية", key="lang_btn", on_click=toggle_lang)

if page == "overview":
    overview()
elif page == "investor":
    investor()
else:
    idea_page(page)

def sprig_qa():
    fast = min(R.values(), key=lambda r: r["payback"])
    big = max(R.values(), key=lambda r: r["net_annual"])
    vals = dict(
        fast=idea_name(fast["key"]), fast_pb=years_text(fast["payback"]),
        big=idea_name(big["key"]), big_net=aed(big["net_annual"]),
        capex=aed(sum(r["capex"] for r in R.values())), saving=aed(sum(r["annual_saving"] for r in R.values())),
        co2f=f"{P['g_co2']:.2f}", tax=f"{P['g_vat']:.1f}",
        names=("، " if AR else ", ").join(idea_name(k) for k, _ in m.IDEAS))
    return i18n.build_qa(LANG, vals)


if st.session_state["sprig_on"]:
    try:
        sprig.sprig(**SPRIG, lang=LANG, qa=sprig_qa(), corner=st.session_state["sprig_corner"])
    except TypeError:  # an older sprig.py: still show Sprig, in English
        sprig.sprig(**{k: v for k, v in SPRIG.items() if k != "reaction"})
        st.sidebar.warning("Old sprig.py found. Upload the new sprig.py so Sprig can speak Arabic.")
    if getattr(sprig, "MODE", "") == "still":
        st.sidebar.caption("Sprig is in still mode: this Streamlit version blocked its animation.")
