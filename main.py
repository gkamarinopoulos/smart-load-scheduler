import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

st.set_page_config(page_title="Smart Load Scheduler", layout="wide")
st.title("⚡ Smart Load Scheduler")
st.caption("Plan device usage in cheaper hours without changing the core logic.")

with st.sidebar:
    st.header("🔌 Provider & Tariff")
    provider = st.selectbox("Choose provider:", ["ΔΕΗ (PPC)", "ΗΡΩΝ (Heron)", "Elpedison", "Protergia"])
    if provider.startswith("ΔΕΗ"):
        tariff = [0.126 if h < 8 or h >= 23 else 0.156 for h in range(24)]
        st.caption("Night: 23:00–08:00 → 0.126 €/kWh, Day: 08:00–23:00 → 0.156 €/kWh")
    elif provider.startswith("ΗΡΩΝ"):
        tariff = [0.095] * 24
        st.caption("Flat tariff: 0.095 €/kWh")
    elif provider == "Elpedison":
        tariff = [0.099] * 24
        st.caption("Flat tariff: 0.099 €/kWh")
    else:
        tariff = [0.094] * 24
        st.caption("Flat tariff: 0.094 €/kWh")

    fig_t = plt.figure(figsize=(4, 1.6))
    ax_t = fig_t.add_subplot(111)
    ax_t.bar(list(range(24)), tariff)
    ax_t.set_xlabel("Hour")
    ax_t.set_ylabel("€/kWh")
    ax_t.set_xticks(range(0, 24, 3))
    ax_t.set_title("Hourly tariff preview", fontsize=10)
    st.pyplot(fig_t, use_container_width=True)

devices_meta = [
    {"name": "Electric stove",       "emoji": "🍳", "power": 2.0},
    {"name": "Refrigerator",         "emoji": "🧊", "power": 0.15},
    {"name": "Washing machine",      "emoji": "🧺", "power": 1.0},
    {"name": "Air conditioner",      "emoji": "❄️", "power": 1.0},
    {"name": "Microwave oven",       "emoji": "🍲", "power": 1.0},
    {"name": "Television",           "emoji": "📺", "power": 0.08},
    {"name": "Dishwasher",           "emoji": "🍽️", "power": 1.3},
    {"name": "Clothes dryer",        "emoji": "🌪️", "power": 3.0},
    {"name": "Electric water heater","emoji": "🚿", "power": 4.0},
    {"name": "Vacuum cleaner",       "emoji": "🧹", "power": 1.0},
    {"name": "Electric iron",        "emoji": "👔", "power": 1.5},
    {"name": "Hair dryer",           "emoji": "💨", "power": 2.0},
    {"name": "Electric kettle",      "emoji": "🫖", "power": 2.0},
    {"name": "Toaster",              "emoji": "🍞", "power": 1.0},
    {"name": "Coffee maker",         "emoji": "☕", "power": 0.9},
    {"name": "Desktop computer",     "emoji": "🖥️", "power": 0.25},
    {"name": "Fan",                  "emoji": "🌬️", "power": 0.06},
    {"name": "Electric heater",      "emoji": "🔥", "power": 2.0},
    {"name": "Mixer/blender",        "emoji": "🥤", "power": 0.18},
    {"name": "Deep fryer",           "emoji": "🍟", "power": 1.6},
    {"name": "Electric blanket",     "emoji": "🛌", "power": 0.2},
    {"name": "Game console",         "emoji": "🎮", "power": 0.15},
    {"name": "Kitchen hood",         "emoji": "🧑‍🍳", "power": 0.24},
    {"name": "Laptop",               "emoji": "💻", "power": 0.05},
    {"name": "Phone charger",        "emoji": "🔌", "power": 0.01},
]
display_options = ["---"] + [f"{d['emoji']} {d['name']}" for d in devices_meta]
display_to_power = {f"{d['emoji']} {d['name']}": d["power"] for d in devices_meta}

if "devices" not in st.session_state:
    st.session_state.devices = []

tab_add, tab_list, tab_schedule = st.tabs(["➕ Add device", "📋 Device list", "📅 Scheduling"])

with tab_add:
    st.subheader("Add a device")
    with st.form("add_device_form", clear_on_submit=False):
        colA, colB = st.columns([2, 3])
        with colA:
            selected = st.selectbox(
                "Pick a predefined device (optional):",
                options=display_options,
                index=0,
                placeholder="e.g. Washing machine"
            )
        with colB:
            custom_device = st.text_input("Or type a custom device name:", "")

        col1, col2 = st.columns(2)
        with col1:
            power = st.number_input(
                "Power (kW)",
                min_value=0.01, step=0.01,
                value=display_to_power.get(selected, 1.0) if selected != "---" else 1.0,
                help="Typical operating power"
            )
            duration = st.number_input(
                "Operating hours (total)",
                min_value=1, max_value=24, step=1, value=2
            )
        with col2:
            with st.expander("Advanced (optional)"):
                start_hour = st.number_input("Earliest start (0–23)", min_value=0, max_value=23, value=0)
                end_hour = st.number_input("Latest end (1–24)", min_value=1, max_value=24, value=23)
                priority = st.number_input("Priority (1 = high)", min_value=1, value=1,
                                           help="Priority 1 devices are guaranteed even if max power is temporarily exceeded.")

        submitted = st.form_submit_button("Add")
        if submitted:
            name = custom_device.strip() if custom_device.strip() else selected
            if not name or name == "---":
                st.warning("Please select or type a valid device name.")
            else:
                st.session_state.devices.append({
                    "Device": name,
                    "Power (kW)": power,
                    "Operating Hours": duration,
                    "Earliest Hour": start_hour,
                    "Latest Hour": end_hour,
                    "Priority": priority
                })
                st.success(f"Added: **{name}**")

with tab_list:
    st.subheader("Your devices")
    if st.session_state.devices:
        edited_df = st.data_editor(
            pd.DataFrame(st.session_state.devices),
            num_rows="dynamic",
            use_container_width=True
        )
        st.caption("You can edit values directly in the table.")

        colL1, colL2 = st.columns([1, 1])
        with colL1:
            if st.button("Save changes"):
                st.session_state.devices = edited_df.to_dict(orient="records")
                st.success("Changes saved.")
        with colL2:
            if st.button("Clear list"):
                st.session_state.devices = []
                st.info("List cleared.")
    else:
        st.info("No devices added yet.")

with tab_schedule:
    st.subheader("Compute schedule & cost")
    if not st.session_state.devices:
        st.info("Add devices first from the tab above.")
    else:
        if st.button("Calculate schedule", type="primary"):
            df = pd.DataFrame(st.session_state.devices).sort_values("Priority").reset_index(drop=True)

            schedule = {h: {"Devices": [], "Power": 0.0, "Cost": 0.0} for h in range(24)}
            total_cost = 0.0
            max_power = 3.5
            forced_warnings = []

            def distance_from_range(h, start, end):
                if h < start:
                    return start - h
                elif h >= end:
                    return h - end + 1
                else:
                    return 0

            summary = []
            for _, row in df.iterrows():
                name = row["Device"]
                power = float(row["Power (kW)"])
                hours_needed = int(row["Operating Hours"])
                min_hour = int(row["Earliest Hour"])
                max_hour = int(row["Latest Hour"])
                priority = int(row["Priority"])

                inside = list(range(min_hour, max_hour))
                outside = [h for h in range(24) if h not in inside]
                outside_sorted = sorted(outside, key=lambda h: (distance_from_range(h, min_hour, max_hour), tariff[h]))
                all_ranked_hours = inside + outside_sorted

                scheduled_hours = []

                for h in all_ranked_hours:
                    if hours_needed == 0:
                        break
                    if schedule[h]["Power"] + power <= max_power:
                        schedule[h]["Devices"].append(name)
                        schedule[h]["Power"] += power
                        cost = power * tariff[h]
                        schedule[h]["Cost"] += cost
                        total_cost += cost
                        scheduled_hours.append(h)
                        hours_needed -= 1

                if hours_needed > 0 and priority == 1:
                    for h in all_ranked_hours:
                        if hours_needed == 0:
                            break
                        schedule[h]["Devices"].append(name)
                        schedule[h]["Power"] += power
                        cost = power * tariff[h]
                        schedule[h]["Cost"] += cost
                        total_cost += cost
                        scheduled_hours.append(h)
                        hours_needed -= 1
                    forced_warnings.append(name)

                summary.append((name, scheduled_hours))

            result_table = [{
                "Hour": f"{h:02d}:00",
                "Devices": ", ".join(schedule[h]["Devices"]),
                "Power (kW)": round(schedule[h]["Power"], 2),
                "Cost (€)": round(schedule[h]["Cost"], 3)
            } for h in range(24)]
            schedule_df = pd.DataFrame(result_table)

            if forced_warnings:
                st.warning(
                    "Some high-priority devices were forced in even when the max power limit was reached: "
                    + ", ".join(sorted(set(forced_warnings)))
                )

            st.success(f"💸 Total daily cost with {provider}: **€{round(total_cost, 2)}**")

            st.markdown("---")
            st.subheader("📅 Hourly schedule")
            st.dataframe(schedule_df, use_container_width=True)

            st.subheader("📊 Charts")
            fig = plt.figure(figsize=(11, 3))
            gs = GridSpec(1, 3, width_ratios=[1, 0.05, 1], wspace=0.5)

            hours_numeric = [f"{int(h):02d}" for h in schedule_df["Hour"].str.split(":").str[0]]

            ax1 = fig.add_subplot(gs[0])
            ax1.bar(hours_numeric, schedule_df["Power (kW)"])
            ax1.set_ylabel("Power (kW)", fontsize=9)
            ax1.set_title("Hourly Power Consumption", fontsize=10)
            ax1.tick_params(axis='x', labelrotation=90, labelsize=8)

            ax2 = fig.add_subplot(gs[2])
            ax2.bar(hours_numeric, schedule_df["Cost (€)"])
            ax2.set_ylabel("Cost (€)", fontsize=9)
            ax2.set_title("Hourly Energy Cost", fontsize=10)
            ax2.tick_params(axis='x', labelrotation=90, labelsize=8)

            st.pyplot(fig, use_container_width=True)

            csv_buffer = io.StringIO()
            schedule_df.to_csv(csv_buffer, index=False)
            st.download_button("📄 Download CSV", csv_buffer.getvalue(), file_name="schedule.csv", mime="text/csv")
