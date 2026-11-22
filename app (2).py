import altair as alt
import pandas as pd
import streamlit as st

import models as m
import sprig

st.set_page_config(page_title="EcoSmart Smart Campus Dashboard", page_icon="🌿", layout="wide")

# ------------------------------------------------------------------ look and feel
NAVY, TEAL, AMBER = "#0B1B3F", "#13A08A", "#F5A623"
NAV = [
    ("overview", "🏠  Overview"),
    ("windows", "🪟  Windows & Shading"),
    ("monitoring", "📡  Energy Monitoring"),
    ("solar", "☀️  Solar Shaded Parking"),
    ("recycling", "♻️  Smart Recycling"),
    ("irrigation", "💧  Smart Irrigation"),
    ("investor", "💼  Investor comparison"),
]
NAV_LABEL = dict(NAV)
EMOJI = {"windows": "🪟", "monitoring": "📡", "solar": "☀️", "recycling": "♻️", "irrigation": "💧"}
COLOR = {"windows": "#2F7FC1", "monitoring": "#F5A623", "solar": "#E4572E",
         "recycling": "#4DAA57", "irrigation": "#13A08A"}
PREFIX = {"windows": "w_", "monitoring": "m_", "solar": "s_", "recycling": "r_", "irrigation": "i_"}
DESCRIPTIONS = {
    "windows": "Right-sized, shaded windows cut the cooling load and keep the daylight. "
               "The peak cooling numbers come from the Energy3D simulation.",
    "monitoring": "ESP32 sensors spot air-conditioning running in empty rooms and switch it off.",
    "solar": "Solar canopies over the parking lot make clean power and shade the cars.",
    "recycling": "Smart bins with fill-level sensors raise the share of waste that gets recycled.",
    "irrigation": "Soil-moisture sensors and weather-based scheduling cut irrigation water.",
}

TINT = {"windows": "#E8F2FB", "monitoring": "#FFF3DC", "solar": "#FDE6E0",
        "recycling": "#E7F5E9", "irrigation": "#DDF4F0"}
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;800&display=swap');
  .stApp, .stMarkdown, button, input, label, textarea {{font-family: 'Nunito', sans-serif;}}
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

OVERVIEW_TIPS = ["Try the Starter plan: the cheapest way to begin!", "Solar saves the most but costs the most.",
                 "Drag the time machine to peek 25 years ahead!", "Press Celebrate for balloons!"]
INVESTOR_TIPS = ["Rank by payback to find the quickest win.", "Raise the budget to unlock solar!",
                 "Fast payback plus low cost makes happy investors."]
IDEA_TIPS = {
    "windows": ["Smaller windows let less sun in.", "Try new window numbers and watch peak kW change!",
                "Shading keeps the daylight but blocks the heat."],
    "monitoring": ["Empty rooms with the AC on waste a lot of power.", "More monitored rooms means more savings.",
                   "The sensors are cheap, so this one pays back fast!"],
    "solar": ["Parked cars get shade and the campus gets power.", "More parking spaces means more solar!",
              "Solar costs the most but saves the most."],
    "recycling": ["Smart bins tell us when they are full.", "Raise the recycled share and watch landfill shrink!",
                  "Less landfill means lower fees."],
    "irrigation": ["Plants only get water when the soil is dry.", "Move the water-saving slider and watch me!",
                   "Water savings add up all year."],
}

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
if "look_years" not in st.session_state:
    st.session_state["look_years"] = 10
else:
    st.session_state["look_years"] = st.session_state["look_years"]


# ------------------------------------------------------------------ helpers
def aed(x):
    return f"AED {x:,.0f}"


def years_text(x):
    return "never" if x == float("inf") else f"{x:.1f} years"


def go(page):
    st.session_state["page"] = page


def reset(prefix):
    for k, v in m.DEFAULTS.items():
        if k.startswith(prefix):
            st.session_state[k] = v
    st.toast("Inputs reset! 🌱")


def set_plan(keys):
    for k, _ in m.IDEAS:
        st.session_state[f"on_{k}"] = k in keys


def hero(title, subtitle, pill="", tint="#D8F3EA", emojis=("🌿", "☀️", "💧")):
    badge = f'<div class="pill">{pill}</div><br>' if pill else ""
    fl = "".join(f'<span class="fl" style="right:{4 + i * 9}%;top:{14 + (i % 2) * 34}%;'
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
                mood, reaction, text = "excited", "cheer", f"Yay! The yearly saving went up by AED {d:,.0f}!"
            else:
                mood, reaction, text = "worried", "oops", f"Oops! The yearly saving dropped by AED {-d:,.0f}."
    SPRIG.update(mood=mood, message=text, tips=tips, reaction=reaction)


def fun_facts(co2, kwh, water, waste):
    items = []
    if kwh > 0:
        items.append(("💡", f"{kwh / 87.6:,.0f}", "10 W LED bulbs lit all year"))
    if co2 > 0:
        items.append(("🌳", f"{co2 * 1000 / 21:,.0f}", "trees' yearly CO₂ uptake (about)"))
    if water > 0:
        items.append(("🏊", f"{water / 2500:,.1f}", "Olympic swimming pools of water"))
    if waste > 0:
        items.append(("🐘", f"{waste / 6:,.0f}", "elephants of waste kept out of landfill (about)"))
    if items:
        for col, (e, n, t) in zip(st.columns(len(items)), items):
            col.markdown(f'<div class="fact"><div class="e">{e}</div><div class="n">{n}</div>'
                         f'<div class="t">{t}</div></div>', unsafe_allow_html=True)


def kpi_row(items):
    """items: (label, value, sub, accent colour)"""
    cols = st.columns(len(items))
    for col, (label, value, sub, accent) in zip(cols, items):
        col.markdown(
            f'<div class="kpi" style="border-left:6px solid {accent}">'
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


def sb_number(label, key, min_value, step, help=None):
    return st.sidebar.number_input(label, min_value=min_value, step=step, key=key, help=help)


# ------------------------------------------------------------------ sidebar
st.sidebar.title("🌿 EcoSmart Campus")
st.sidebar.caption("Smart Campus Resource Efficiency System 🌍")
st.sidebar.radio("Go to", [k for k, _ in NAV], format_func=lambda k: NAV_LABEL[k],
                 key="page", label_visibility="collapsed")
page = st.session_state["page"]
st.sidebar.divider()

if page == "windows":
    st.sidebar.subheader("🪟 Change the inputs")
    sb_number("Peak cooling, large windows 5×3 m (kW)", "w_peak_base", 0.0, 0.5)
    sb_number("Peak cooling, optimized windows 3×1 m (kW)", "w_peak_new", 0.0, 0.5)
    sb_number("Full-load hours per year", "w_hours", 0, 50, "Hours per year the cooling runs at full load.")
    sb_number("Extra cost of optimized windows and shading (AED)", "w_capex", 0, 1000,
              "Placeholder - replace with a real quote.")
elif page == "monitoring":
    st.sidebar.subheader("📡 Change the inputs")
    sb_number("Monitored rooms", "m_rooms", 0, 1)
    sb_number("AC power wasted in an empty room (kW)", "m_kw", 0.0, 0.1)
    sb_number("Empty-but-running hours per room per year", "m_hours", 0, 25)
    st.sidebar.slider("Waste removed by auto shut-off (%)", 0, 100, key="m_eff")
    sb_number("Sensor kit cost per room (AED)", "m_cost_room", 0, 50, "ESP32 + current + occupancy sensor.")
    sb_number("Gateway and setup cost (AED)", "m_hub", 0, 500)
elif page == "solar":
    st.sidebar.subheader("☀️ Change the inputs")
    sb_number("Parking spaces covered", "s_spaces", 0, 5)
    sb_number("Panel capacity per space (kWp)", "s_kwp_space", 0.0, 0.1)
    sb_number("Yearly yield (kWh per kWp)", "s_yield", 0, 20)
    sb_number("Installed cost per kWp (AED)", "s_cost_kwp", 0, 100, "Placeholder - replace with a real quote.")
elif page == "recycling":
    st.sidebar.subheader("♻️ Change the inputs")
    sb_number("Waste produced (tonnes per year)", "r_waste", 0.0, 10.0)
    st.sidebar.slider("Share recycled today (%)", 0.0, 100.0, step=1.0, key="r_div_base")
    st.sidebar.slider("Share recycled with smart bins (%)", 0.0, 100.0, step=1.0, key="r_div_new")
    sb_number("Smart bins", "r_bins", 0, 1)
    sb_number("Cost per smart bin (AED)", "r_cost_bin", 0, 250)
elif page == "irrigation":
    st.sidebar.subheader("💧 Change the inputs")
    sb_number("Irrigation water today (litres per day)", "i_l_day", 0, 1000)
    st.sidebar.slider("Water saved (%)", 0.0, 100.0, step=1.0, key="i_save")
    sb_number("Irrigation days per year", "i_days", 0, 5)
    sb_number("Soil-moisture sensors", "i_sensors", 0, 1)
    sb_number("Cost per sensor (AED)", "i_cost_sensor", 0, 50)
    sb_number("Controller and valves (AED)", "i_ctrl", 0, 500)
elif page == "overview":
    st.sidebar.info("👆 Pick an idea to meet its mascot, change its inputs and see only its own savings.")
elif page == "investor":
    st.sidebar.info("Use the ranking and budget boxes on the page to compare the ideas.")

if page in PREFIX:
    st.sidebar.button("↺ Reset this idea's inputs", on_click=reset, args=(PREFIX[page],))

st.sidebar.toggle("🌱 Show Sprig", key="sprig_on")

with st.sidebar.expander("⚙️ Tariff, tax and CO₂ (all ideas)"):
    st.number_input("Electricity tariff (AED/kWh)", min_value=0.0, step=0.01, key="g_elec_tariff")
    st.number_input("Water tariff (AED/m³)", min_value=0.0, step=0.5, key="g_water_tariff")
    st.number_input("Landfill fee (AED/tonne)", min_value=0.0, step=10.0, key="g_landfill_fee")
    st.number_input("Recycled material value (AED/tonne)", min_value=0.0, step=10.0, key="g_recycle_rev")
    st.slider("Tax added to bills and equipment (%)", 0.0, 20.0, step=0.5, key="g_vat")
    st.number_input("CO₂ per kWh (kg)", min_value=0.0, step=0.01, key="g_co2")
    st.slider("Yearly upkeep (% of equipment cost)", 0.0, 10.0, step=0.5, key="g_om")
    st.slider("Analysis period (years)", 1, 25, key="g_years")
    st.caption("Tariffs, costs and tax are illustrative placeholders. Use official tariffs and real quotes.")

P = {k: st.session_state[k] for k in m.DEFAULTS}
R = m.all_results(P)
YEARS = P["g_years"]


# ------------------------------------------------------------------ pages
def overview():
    hero("Smart Campus Resource Efficiency System",
         "Switch ideas on and off to build your own campus plan, then watch the savings add up.",
         "ECOSMART INNOVATORS · LIWA UNIVERSITY", "#D8F3EA", ("🌿", "☀️", "💧", "♻️"))

    on = [k for k, _ in m.IDEAS if st.session_state[f"on_{k}"]]
    plan_value = sum(R[k]["annual_saving"] for k in on)
    if not on:
        mascot("worried", "Everything is switched off. Turn an idea on to start building your plan!", OVERVIEW_TIPS, "overview", plan_value)
    elif len(on) == 5:
        mascot("excited", "All five ideas are on! This is the full Smart Campus plan.", OVERVIEW_TIPS, "overview", plan_value)
    else:
        mascot("happy", f"{len(on)} of 5 ideas are on. Flip the switches below and watch the numbers change!", OVERVIEW_TIPS, "overview", plan_value)

    st.subheader("🧩 Build your plan")
    p1, p2, p3 = st.columns(3)
    p1.button("🌱 Starter (low cost)", on_click=set_plan, args=(["monitoring", "irrigation", "recycling"],))
    p2.button("⚖️ Balanced", on_click=set_plan, args=(["windows", "monitoring", "recycling", "irrigation"],))
    p3.button("🚀 Max impact (all five)", on_click=set_plan, args=([k for k, _ in m.IDEAS],))

    cols = st.columns(5)
    for col, (key, _) in zip(cols, m.IDEAS):
        r = R[key]
        dim = "" if key in on else "opacity:.45;filter:grayscale(.6);"
        col.markdown(
            f'<div class="card" style="background:{TINT[key]};border-top:6px solid {COLOR[key]};{dim}">'
            f'<div style="font-size:1.8rem">{EMOJI[key]}</div><h4>{r["name"]}</h4>'
            f'<div class="big">{aed(r["annual_saving"])}</div>'
            f'<div class="small">saved per year · {r["headline"]}</div></div>', unsafe_allow_html=True)
        col.toggle("Include in plan", key=f"on_{key}")
        col.button("Open →", key=f"open_{key}", on_click=go, args=(key,))

    sel = {k: R[k] for k in on}
    if not sel:
        return
    tot = lambda f: sum(r[f] for r in sel.values())
    capex, net = tot("capex"), tot("net_annual")

    st.subheader("📊 Your plan together")
    kpi_row([("Energy saved or generated", f"{tot('energy_kwh'):,.0f} kWh", "every year", "#F5A623"),
             ("CO₂ avoided", f"{tot('co2_t'):,.1f} t", "every year", TEAL),
             ("Water saved", f"{tot('water_m3'):,.0f} m³", "every year", "#2F7FC1"),
             ("Less landfill waste", f"{tot('waste_t'):,.1f} t", "every year", "#4DAA57")])
    kpi_row([("Annual saving", aed(tot("annual_saving")), "after tax", TEAL),
             ("Equipment cost", aed(capex), f"{len(sel)} idea(s) switched on", NAVY),
             ("Pays for itself in", years_text(capex / net if net > 0 else float("inf")), "payback time", AMBER),
             (f"{YEARS}-year net benefit", aed(net * YEARS - capex), "saving minus cost", "#4DAA57")])

    st.subheader("🎈 What does that look like?")
    fun_facts(tot("co2_t"), tot("energy_kwh"), tot("water_m3"), tot("waste_t"))

    st.subheader("🔮 Time machine")
    look = st.slider("Jump ahead (years)", 1, 25, key="look_years")
    money = net * look - capex
    kpi_row([("Money after that time", aed(money), f"after {look} year(s)", TEAL if money >= 0 else "#E4572E"),
             ("CO₂ avoided so far", f"{tot('co2_t') * look:,.0f} t", "added up", "#13A08A"),
             ("Trees' worth of CO₂", f"{tot('co2_t') * look * 1000 / 21:,.0f}", "about", "#4DAA57")])
    df = pd.DataFrame({"Year": list(range(0, 26)), "AED": [net * t - capex for t in range(26)]})
    area = alt.Chart(df).mark_area(opacity=0.25, color=TEAL, line={"color": TEAL, "strokeWidth": 3}) \
        .encode(x=alt.X("Year:Q", title="Years from today"),
                y=alt.Y("AED:Q", title="AED, cumulative", axis=alt.Axis(format="~s")))
    zero = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color=NAVY, strokeDash=[5, 5]).encode(y="y:Q")
    now = alt.Chart(pd.DataFrame({"x": [look]})).mark_rule(color=AMBER, strokeWidth=3).encode(x="x:Q")
    show((area + zero + now).properties(height=280))

    if st.button("🎉 Celebrate!"):
        st.balloons()
    st.caption("The Windows result is confirmed by Energy3D. All other figures use illustrative inputs, "
               "not measured campus data. Fun comparisons are rough approximations.")


def idea_page(key):
    r, color = R[key], COLOR[key]
    hero(f"{EMOJI[key]} {r['name']}", DESCRIPTIONS[key], "ONE IDEA · ITS OWN SAVINGS", TINT[key], (EMOJI[key], "✨", "🌿"))

    tips = {
        "windows": f"Smaller, shaded windows cut peak cooling by {(P['w_peak_base'] - P['w_peak_new']) / P['w_peak_base'] * 100 if P['w_peak_base'] else 0:.0f}%! Try new window numbers on the left.",
        "monitoring": f"I watch {P['m_rooms']:.0f} rooms and switch off AC nobody is using. Add more rooms on the left!",
        "solar": f"My canopy makes {r['energy_kwh']:,.0f} kWh a year and shades the cars. Try more parking spaces!",
        "recycling": f"With smart bins, {P['r_div_new']:.0f}% of waste gets recycled instead of {P['r_div_base']:.0f}%. Slide it on the left!",
        "irrigation": f"I save {r['water_m3']:,.0f} m³ of water a year. Move the water-saving slider and watch me!",
    }
    mood = "excited" if r["payback"] <= 3 else "happy" if r["payback"] <= 10 else "worried"
    mascot(mood, tips[key], IDEA_TIPS[key], key, r["annual_saving"])

    kpi_row([("Annual saving", aed(r["annual_saving"]), "after tax", color),
             ("Equipment cost", aed(r["capex"]), "including tax", NAVY),
             ("Pays for itself in", years_text(r["payback"]), "payback time", AMBER),
             (f"{YEARS}-year net benefit", aed(r["net_period"]), "saving minus cost", "#4DAA57")])

    impacts = [("Energy saved or generated", f"{r['energy_kwh']:,.0f} kWh", "every year", r["energy_kwh"]),
               ("CO₂ avoided", f"{r['co2_t']:,.1f} t", "every year", r["co2_t"]),
               ("Water saved", f"{r['water_m3']:,.0f} m³", "every year", r["water_m3"]),
               ("Waste kept out of landfill", f"{r['waste_t']:,.1f} t", "every year", r["waste_t"])]
    kpi_row([(a, b, c, color) for a, b, c, v in impacts if v > 0] or [("Impact", "–", "", color)])

    st.markdown(
        f'<div class="plain">💡 <b>In plain words:</b> this idea saves <b>{aed(r["annual_saving"])}</b> a year '
        f'after tax. The equipment costs <b>{aed(r["capex"])}</b> and pays for itself in '
        f'<b>{years_text(r["payback"])}</b>.</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Before and after", "🎈 Fun facts", "🧾 Tariff, tax and cost", "💼 Investor view"])
    with tab1:
        ch = r["chart"]
        st.subheader(ch["title"])
        bars(ch["labels"], ch["values"], ["#B8C4DA", color])
    with tab2:
        st.subheader("What does that look like?")
        fun_facts(r["co2_t"], r["energy_kwh"], r["water_m3"], r["waste_t"])
        st.caption("Rough comparisons to make the numbers easier to picture.")
    with tab3:
        left, right = st.columns(2)
        with left:
            st.markdown("**What is saved**")
            st.dataframe(pd.DataFrame([{
                "Item": x["Item"],
                "Quantity": f"{x['Quantity']:,.1f} {x['Unit']}",
                "Rate": f"{x['Rate']:,.2f} {x['Rate unit']}",
                "Amount (AED)": f"{x['Amount (AED)']:,.0f}",
            } for x in r["rows"]]), hide_index=True)
        with right:
            st.markdown("**From saving to net saving**")
            st.dataframe(pd.DataFrame([
                {"Line": "Saving before tax", "AED per year": f"{r['subtotal']:,.0f}"},
                {"Line": f"Tax ({P['g_vat']:.1f}%)", "AED per year": f"{r['tax']:,.0f}"},
                {"Line": "Annual saving", "AED per year": f"{r['annual_saving']:,.0f}"},
                {"Line": "Yearly upkeep", "AED per year": f"−{r['upkeep']:,.0f}"},
                {"Line": "Net annual saving", "AED per year": f"{r['net_annual']:,.0f}"},
            ]), hide_index=True)
    with tab4:
        if r["payback"] <= 3:
            st.success(f"Fast payback: {years_text(r['payback'])}. Yearly return {r['yearly_return']:.0f}% "
                       "on the money invested.")
        elif r["payback"] <= 7:
            st.info(f"Moderate payback: {years_text(r['payback'])}. Yearly return {r['yearly_return']:.0f}%.")
        else:
            st.warning(f"Slow payback: {years_text(r['payback'])}. Its value may be mainly environmental.")
        st.markdown("**Money over time** (the line crosses zero when the idea has paid for itself)")
        df = pd.DataFrame({"Year": list(range(YEARS + 1)),
                           "AED": [-r["capex"] + r["net_annual"] * t for t in range(YEARS + 1)]})
        area = alt.Chart(df).mark_area(opacity=0.25, color=color, line={"color": color, "strokeWidth": 3}) \
            .encode(x=alt.X("Year:Q", title="Years from today"),
                    y=alt.Y("AED:Q", title="AED, cumulative", axis=alt.Axis(format="~s")))
        zero = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color=NAVY, strokeDash=[5, 5]).encode(y="y:Q")
        show((area + zero).properties(height=300))


def investor():
    hero("💼 Investor comparison",
         "Which idea gives the most saving for the money? Compare all five side by side.",
         "FOR INVESTORS", "#FFF1D6", ("💰", "📈", "🌍"))
    c1, c2 = st.columns(2)
    c1.selectbox("Rank the ideas by", list(m.RANKINGS), key="c_rank")
    c2.number_input("Budget to invest (AED)", min_value=0, step=50000, key="c_budget")
    field, ascending = m.RANKINGS[st.session_state["c_rank"]]
    ranked = sorted(R.values(), key=lambda r: r[field], reverse=not ascending)
    key_of = {r["name"]: k for k, r in R.items()}

    best = ranked[0]
    mascot("happy", f"Psst! For this ranking, {best['name']} is the top pick. "
                    "Change the ranking or the budget to see who wins!", INVESTOR_TIPS)
    st.markdown(f'<div class="best">🏆 <b>Top pick: {best["name"]}</b> · pays back in '
                f'{years_text(best["payback"])} · net saving {aed(best["net_annual"])} a year · '
                f'{best["co2_t"]:,.1f} t CO₂ avoided.</div>', unsafe_allow_html=True)

    medals = ["🥇", "🥈", "🥉", "4", "5"]
    st.dataframe(pd.DataFrame([{
        "Rank": medals[i],
        "Idea": f"{EMOJI[key_of[r['name']]]} {r['name']}",
        "Equipment cost (AED)": f"{r['capex']:,.0f}",
        "Net annual saving (AED)": f"{r['net_annual']:,.0f}",
        "Payback": years_text(r["payback"]),
        f"{YEARS}-year net benefit (AED)": f"{r['net_period']:,.0f}",
        "Yearly return": f"{r['yearly_return']:.0f}%",
        "CO₂ avoided (t/yr)": f"{r['co2_t']:,.1f}",
    } for i, r in enumerate(ranked)]), hide_index=True)

    names = [r["name"] for r in ranked]
    colors = [COLOR[key_of[n]] for n in names]
    a, b = st.columns(2)
    with a:
        st.subheader("Net annual saving (AED)")
        bars(names, [r["net_annual"] for r in ranked], colors, horizontal=True, height=260)
    with b:
        st.subheader("Payback (years)")
        bars(names, [round(min(r["payback"], 99), 1) for r in ranked], colors, fmt=".1f",
             horizontal=True, height=260)

    st.subheader("🎯 Where the budget does the most good")
    chosen, left = m.pick_portfolio(R, st.session_state["c_budget"])
    if not chosen:
        st.warning("No single idea fits this budget. Increase it or lower an idea's cost.")
    else:
        st.write("Ideas funded, best yearly return per dirham first: "
                 + ", ".join(f"{EMOJI[key_of[r['name']]]} {r['name']}" for r in chosen) + ".")
        kpi_row([("Invested", aed(sum(r["capex"] for r in chosen)), "equipment cost", NAVY),
                 ("Net annual saving", aed(sum(r["net_annual"] for r in chosen)), "after upkeep", TEAL),
                 ("Budget left", aed(left), "not spent", AMBER)])
        if st.button("🎉 Celebrate this plan!"):
            st.balloons()
    st.caption("Illustrative figures from the project's assumptions - not financial advice.")


if page == "overview":
    overview()
elif page == "investor":
    investor()
else:
    idea_page(page)

if st.session_state["sprig_on"]:
    sprig.sprig(**SPRIG)
