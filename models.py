"""Calculation models for the five EcoSmart ideas.

Every function takes a plain dict `p` of inputs and returns a result dict, so
each idea is calculated on its own. The defaults reproduce the roll-up numbers
(568,500 kWh, 227.4 t CO2, 8,760 m3, 109.5 t). Costs, tariffs and tax rates are
ILLUSTRATIVE placeholders - replace them with real quotes and official tariffs.
"""

DEFAULTS = {
    # ---- global assumptions (tariff, tax, CO2 factor) ----
    "g_elec_tariff": 0.30,    # AED per kWh
    "g_water_tariff": 8.00,   # AED per m3
    "g_landfill_fee": 120.0,  # AED per tonne to landfill
    "g_recycle_rev": 0.0,     # AED per tonne diverted (material value)
    "g_vat": 5.0,             # % tax added to avoided bills and to equipment cost
    "g_co2": 0.40,            # kg CO2 per kWh (568,500 kWh -> 227.4 t)
    "g_om": 2.0,              # % of equipment cost per year for upkeep
    "g_years": 10,            # analysis period, years
    # ---- 1 Windows & Shading ----
    "w_peak_base": 18.0,      # kW peak cooling, large windows (Energy3D)
    "w_peak_new": 13.0,       # kW peak cooling, optimized windows (Energy3D)
    "w_hours": 1500,          # equivalent full-load hours per kW of peak reduction
    "w_capex": 15000,         # AED extra cost of optimized windows + shading (placeholder)
    # ---- 2 Energy Monitoring ----
    "m_rooms": 20,            # monitored rooms
    "m_kw": 1.5,              # kW of AC wasted in an empty room
    "m_hours": 700,           # empty-but-running hours per room per year
    "m_eff": 100,             # % of that waste removed by auto shut-off
    "m_cost_room": 600,       # AED per room (ESP32 + current + occupancy sensor)
    "m_hub": 2000,            # AED gateway / setup
    # ---- 3 Solar Shaded Parking ----
    "s_spaces": 150,
    "s_kwp_space": 2.5,       # kWp per parking space (150 x 2.5 = 375 kWp)
    "s_yield": 1440,          # kWh per kWp per year
    "s_cost_kwp": 4000,       # AED per kWp installed (placeholder)
    # ---- 4 Smart Recycling ----
    "r_waste": 365.0,         # tonnes of waste per year
    "r_div_base": 15.0,       # % diverted today
    "r_div_new": 45.0,        # % diverted with smart bins
    "r_bins": 12,
    "r_cost_bin": 3500,       # AED per smart bin (placeholder)
    # ---- 5 Smart Irrigation ----
    "i_l_day": 80000,         # litres per day today
    "i_save": 30.0,           # % water saved
    "i_days": 365,
    "i_sensors": 25,
    "i_cost_sensor": 800,     # AED per soil-moisture sensor
    "i_ctrl": 15000,          # AED controller and valves
    # ---- investor comparison ----
    "c_budget": 2000000,      # AED available to invest
    "c_rank": "Payback (fastest first)",
}

IDEAS = [
    ("windows", "1 · Windows & Shading"),
    ("monitoring", "2 · Energy Monitoring"),
    ("solar", "3 · Solar Shaded Parking"),
    ("recycling", "4 · Smart Recycling"),
    ("irrigation", "5 · Smart Irrigation"),
]


def _finish(p, name, capex, energy_kwh, water_m3, waste_t, lines, chart):
    """Add tax, CO2, payback and ROI. `lines` = (item, qty, unit, rate, rate_unit)."""
    vat = p["g_vat"] / 100.0
    rows = []
    subtotal = 0.0
    for item, qty, unit, rate, rate_unit in lines:
        amount = qty * rate
        subtotal += amount
        rows.append({"Item": item, "Quantity": qty, "Unit": unit,
                     "Rate": rate, "Rate unit": rate_unit, "Amount (AED)": amount})
    tax = subtotal * vat
    annual_saving = subtotal + tax
    capex_total = capex * (1 + vat)
    upkeep = capex_total * p["g_om"] / 100.0
    net = annual_saving - upkeep
    years = p["g_years"]
    payback = capex_total / net if net > 0 else float("inf")
    net_period = net * years - capex_total
    roi = net_period / capex_total * 100 if capex_total else 0.0
    return {
        "name": name,
        "energy_kwh": energy_kwh,
        "water_m3": water_m3,
        "waste_t": waste_t,
        "co2_t": energy_kwh * p["g_co2"] / 1000.0,
        "rows": rows,
        "subtotal": subtotal,
        "tax": tax,
        "annual_saving": annual_saving,
        "capex": capex_total,
        "upkeep": upkeep,
        "net_annual": net,
        "payback": payback,
        "net_period": net_period,
        "roi": roi,
        "yearly_return": net / capex_total * 100 if capex_total else 0.0,
        "chart": chart,
    }


def windows(p):
    cut = max(p["w_peak_base"] - p["w_peak_new"], 0.0)
    kwh = cut * p["w_hours"]
    pct = cut / p["w_peak_base"] * 100 if p["w_peak_base"] else 0.0
    r = _finish(
        p, "Windows & Shading", p["w_capex"], kwh, 0.0, 0.0,
        [("Electricity not bought", kwh, "kWh", p["g_elec_tariff"], "AED/kWh")],
        {"title": "Peak cooling demand (kW)",
         "labels": ["Large windows (5×3 m)", "Optimized (3×1 m)"],
         "values": [p["w_peak_base"], p["w_peak_new"]]})
    r["headline"] = f"−{pct:.0f}% peak cooling"
    return r


def monitoring(p):
    base = p["m_rooms"] * p["m_kw"] * p["m_hours"]
    kwh = base * p["m_eff"] / 100.0
    capex = p["m_rooms"] * p["m_cost_room"] + p["m_hub"]
    r = _finish(
        p, "Energy Monitoring", capex, kwh, 0.0, 0.0,
        [("Electricity not bought", kwh, "kWh", p["g_elec_tariff"], "AED/kWh")],
        {"title": "AC energy used in empty rooms (kWh/yr)",
         "labels": ["Today", "With auto shut-off"],
         "values": [base, base - kwh]})
    r["headline"] = f"{p['m_rooms']:.0f} rooms monitored"
    return r


def solar(p):
    kwp = p["s_spaces"] * p["s_kwp_space"]
    kwh = kwp * p["s_yield"]
    r = _finish(
        p, "Solar Shaded Parking", kwp * p["s_cost_kwp"], kwh, 0.0, 0.0,
        [("Electricity not bought", kwh, "kWh", p["g_elec_tariff"], "AED/kWh")],
        {"title": "Solar energy produced (kWh/yr)",
         "labels": ["Today", "With solar canopy"],
         "values": [0.0, kwh]})
    r["headline"] = f"{kwp:,.0f} kWp on {p['s_spaces']:.0f} spaces"
    return r


def recycling(p):
    base_landfill = p["r_waste"] * (1 - p["r_div_base"] / 100.0)
    new_landfill = p["r_waste"] * (1 - p["r_div_new"] / 100.0)
    diverted = max(base_landfill - new_landfill, 0.0)
    capex = p["r_bins"] * p["r_cost_bin"]
    r = _finish(
        p, "Smart Recycling", capex, 0.0, 0.0, diverted,
        [("Landfill fees avoided", diverted, "t", p["g_landfill_fee"], "AED/t"),
         ("Recycled material value", diverted, "t", p["g_recycle_rev"], "AED/t")],
        {"title": "Waste sent to landfill (t/yr)",
         "labels": ["Today", "With smart bins"],
         "values": [base_landfill, new_landfill]})
    r["headline"] = f"+{p['r_div_new'] - p['r_div_base']:.0f} pts diversion"
    return r


def irrigation(p):
    base = p["i_l_day"] * p["i_days"] / 1000.0
    saved = base * p["i_save"] / 100.0
    capex = p["i_sensors"] * p["i_cost_sensor"] + p["i_ctrl"]
    r = _finish(
        p, "Smart Irrigation", capex, 0.0, saved, 0.0,
        [("Water not bought", saved, "m³", p["g_water_tariff"], "AED/m³")],
        {"title": "Irrigation water (m³/yr)",
         "labels": ["Today", "With soil sensors"],
         "values": [base, base - saved]})
    r["headline"] = f"−{p['i_save']:.0f}% irrigation water"
    return r


MODELS = {"windows": windows, "monitoring": monitoring, "solar": solar,
          "recycling": recycling, "irrigation": irrigation}


def all_results(p):
    out = {}
    for key, _ in IDEAS:
        out[key] = MODELS[key](p)
        out[key]["key"] = key
    return out


RANKINGS = {
    "Payback (fastest first)": ("payback", True),
    "10-year net benefit (highest first)": ("net_period", False),
    "Annual net saving (highest first)": ("net_annual", False),
    "Yearly return on money (highest first)": ("yearly_return", False),
    "Cheapest to start (lowest cost first)": ("capex", True),
}


def pick_portfolio(results, budget):
    """Greedy: fund ideas in order of yearly return per dirham until the budget runs out."""
    chosen, left = [], budget
    for r in sorted(results.values(), key=lambda r: r["yearly_return"], reverse=True):
        if r["net_annual"] > 0 and r["capex"] <= left:
            chosen.append(r)
            left -= r["capex"]
    return chosen, left
