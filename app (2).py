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

# Sustainable Development Goals (the same three goals as the roll-up)
SDG = {
    9: {"title": "Industry, Innovation & Infrastructure", "color": "#F36D25",
        "text": "Efficient infrastructure using simulation, sensors and software."},
    11: {"title": "Sustainable Cities & Communities", "color": "#FD9D24",
         "text": "A comfortable, sustainable and resilient campus community."},
    12: {"title": "Responsible Consumption & Production", "color": "#BF8B2E",
         "text": "Less energy, water and waste through responsible use."},
}
SDG_IDEAS = {"windows": [9, 11], "monitoring": [9, 12], "solar": [11],
             "recycling": [11, 12], "irrigation": [12]}
SDG_WHY = {
    "windows": "Simulation-tested windows keep the campus comfortable and cut cooling demand.",
    "monitoring": "Sensors and software remove air-conditioning waste in empty rooms.",
    "solar": "Clean power and shade for parked cars make the campus more sustainable.",
    "recycling": "Smart bins keep waste out of landfill and the campus cleaner.",
    "irrigation": "Soil sensors use less water for the same green campus.",
}

# Team and branding (Liwa University logo is embedded so no extra file is needed)
TEAM = "Fathima Faseeha Faizoor, Madiha Firdose Shaikh"
SUPERVISOR = "Dr. Karamath Ateeq"
LOGO_SRC = "data:image/png;base64,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"
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
  .sdgrow {{display: flex; flex-wrap: wrap; gap: 10px; margin: 4px 0 14px 0;}}
  .sdgchip {{display: flex; align-items: center; gap: 10px; background: white; border-radius: 999px;
            padding: 6px 16px 6px 6px; box-shadow: 0 3px 14px rgba(11,27,63,.08); color: {NAVY};
            font-size: .9rem; font-weight: 700;}}
  .sdgnum {{display: inline-flex; align-items: center; justify-content: center; min-width: 38px; height: 38px;
           border-radius: 50%; color: white; font-weight: 800; font-size: 1rem;}}
  .sdgcard {{background: white; border-radius: 22px; padding: 16px 18px; min-height: 170px;
            box-shadow: 0 3px 14px rgba(11,27,63,.08); margin-bottom: 12px;}}
  .sdgcard .sdgnum {{width: 52px; height: 52px; font-size: 1.3rem; margin-bottom: 8px;}}
  .sdgcard h4 {{margin: 4px 0 4px 0; font-size: 1.02rem; color: {NAVY};}}
  .team {{display: flex; align-items: center; gap: 18px; flex-wrap: wrap; background: white; border-radius: 22px;
         padding: 14px 20px; margin-top: 26px; box-shadow: 0 3px 14px rgba(11,27,63,.08);
         border-top: 5px solid #13A08A; color: #0B1B3F;}}
  .team img {{height: 52px;}}
  .team .tt {{font-size: .95rem; line-height: 1.5;}}
  .team .tt b {{color: #13A08A;}}
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


SPRIG = {"mood": "happy", "message": "", "tips": []}


def mascot(mood, text, tips=None):
    """Tell Sprig how to feel and what to say; it is drawn once at the end of the script."""
    SPRIG.update(mood=mood, message=text, tips=list(tips or []))


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


def sdg_chips_html(key):
    chips = "".join(
        f'<div class="sdgchip"><span class="sdgnum" style="background:{SDG[n]["color"]}">{n}</span>'
        f'SDG {n} · {SDG[n]["title"]}</div>' for n in SDG_IDEAS[key])
    return f'<div class="sdgrow">{chips}</div>'


def sdg_cards_html(on):
    """One card per goal. A goal is bright when a switched-on idea supports it."""
    cards = []
    for n, d in SDG.items():
        mine = [k for k, _ in m.IDEAS if n in SDG_IDEAS[k] and k in on]
        dim = "" if mine else "opacity:.45;filter:grayscale(.6);"
        who = " ".join(EMOJI[k] for k in mine) or "No idea switched on for this goal"
        names = ", ".join(R_NAMES[k] for k in mine)
        cards.append(
            f'<div class="sdgcard" style="border-top:6px solid {d["color"]};{dim}">'
            f'<span class="sdgnum" style="background:{d["color"]}">{n}</span>'
            f'<h4>SDG {n} · {d["title"]}</h4>'
            f'<div class="small">{d["text"]}</div>'
            f'<div style="margin-top:8px;font-size:1.3rem">{who}</div>'
            f'<div class="small">{names}</div></div>')
    return cards


R_NAMES = {k: n.split("· ", 1)[1] for k, n in m.IDEAS}


def team_footer_html():
    return (f'<div class="team"><img src="{LOGO_SRC}" alt="Liwa University">'
            f'<div class="tt"><b>EcoSmart Innovators</b> · Smart Campus Resource Efficiency System<br>'
            f'Students: {TEAM}<br>Supervisor: {SUPERVISOR}<br>'
            f'<span class="small">5th Sustainability Competition · Fall 2026–2027 · Liwa University</span></div></div>')


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
st.sidebar.markdown(f'<img src="{LOGO_SRC}" style="width:190px;max-width:100%;margin-bottom:6px" alt="Liwa University">', unsafe_allow_html=True)
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
    if not on:
        mascot("worried", "Everything is switched off. Turn an idea on to start building your plan!", OVERVIEW_TIPS)
    elif len(on) == 5:
        mascot("excited", "All five ideas are on! This is the full Smart Campus plan.", OVERVIEW_TIPS)
    else:
        mascot("happy", f"{len(on)} of 5 ideas are on. Flip the switches below and watch the numbers change!", OVERVIEW_TIPS)

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

    st.subheader("🌍 Sustainable Development Goals")
    st.caption("Goals supported by the ideas you have switched on. Switch an idea off and its goals dim.")
    for col, card in zip(st.columns(3), sdg_cards_html(on)):
        col.markdown(card, unsafe_allow_html=True)

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
    mascot(mood, tips[key], IDEA_TIPS[key])

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

    st.markdown("**🌍 Supports these Sustainable Development Goals**")
    st.markdown(sdg_chips_html(key), unsafe_allow_html=True)
    st.caption(SDG_WHY[key])

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

st.markdown(team_footer_html(), unsafe_allow_html=True)

if st.session_state["sprig_on"]:
    sprig.sprig(**SPRIG)
