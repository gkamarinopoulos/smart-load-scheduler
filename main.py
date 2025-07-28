import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

st.set_page_config(page_title="Smart Load Scheduler", layout="wide")
st.title("⚡ Smart Load Scheduler")

provider = st.selectbox("🔌 Select electricity provider:", ["ΔΕΗ", "ΗΡΩΝ", "Elpedison", "Protergia"])
if provider == "ΔΕΗ":
    tariff = [0.126 if h < 8 or h >= 23 else 0.156 for h in range(24)]
elif provider == "ΗΡΩΝ":
    tariff = [0.095] * 24
elif provider == "Elpedison":
    tariff = [0.099] * 24
else:
    tariff = [0.094] * 24

predefined_devices = {
    "Electric stove (oven/hob)": 2.0,
    "Refrigerator (with freezer)": 0.15,
    "Washing machine": 1.0,
    "Air conditioner (~9.000 BTU)": 1.0,
    "Microwave oven": 1.0,
    "Television (LED ~50’’)": 0.08,
    "Dishwasher": 1.3,
    "Clothes dryer": 3.0,
    "Electric water heater": 4.0,
    "Vacuum cleaner": 1.0,
    "Electric iron": 1.5,
    "Hair dryer": 2.0,
    "Electric kettle": 2.0,
    "Toaster": 1.0,
    "Coffee maker": 0.9,
    "Desktop computer": 0.25,
    "Fan (table/floor)": 0.06,
    "Electric heater": 2.0,
    "Mixer/blender": 0.18,
    "Deep fryer": 1.6,
    "Electric blanket": 0.2,
    "Game console": 0.15,
    "Kitchen hood": 0.24,
    "Laptop": 0.05,
    "Phone charger": 0.01
}

if "devices" not in st.session_state:
    st.session_state.devices = []

st.subheader("➕ Add Device")
selected = st.selectbox("🔍 Select or type a device", options=["---"] + list(predefined_devices.keys()),
                         index=0, key="select_box", placeholder="e.g. Washing Machine")
custom_device = st.text_input("✏️ Or enter custom device name:", "")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    power = st.number_input("⚡ Power (kW)", min_value=0.01, step=0.01,
                            value=predefined_devices.get(selected, 1.0) if selected != "---" else 1.0)
with col2:
    duration = st.number_input("⏱ Operating hours", min_value=1, max_value=24, step=1, value=2)
with col3:
    start_hour = st.number_input("🕒 Earliest start hour (0-23)", min_value=0, max_value=23, value=0)
with col4:
    end_hour = st.number_input("🕓 Latest end hour (0-23)", min_value=1, max_value=24, value=23)
with col5:
    priority = st.number_input("🔢 Priority (1 = highest)", min_value=1, value=1)

if st.button("➕ Add Device"):
    name = custom_device.strip() if custom_device.strip() else selected
    if not name or name == "---":
        st.warning("⚠️ Please select or enter a valid device name.")
    else:
        st.session_state.devices.append({
            "Device": name,
            "Power (kW)": power,
            "Operating Hours": duration,
            "Earliest Hour": start_hour,
            "Latest Hour": end_hour,
            "Priority": priority
        })

if st.session_state.devices:
    st.subheader("📋 Devices to be scheduled")
    edited_df = st.data_editor(pd.DataFrame(st.session_state.devices), num_rows="dynamic", use_container_width=True)

    if st.button("🧮 Calculate Schedule"):
        df = edited_df.sort_values("Priority").reset_index(drop=True)

        schedule = {h: {"Devices": [], "Power": 0.0, "Cost": 0.0} for h in range(24)}
        summary = []
        total_cost = 0.0
        max_power = 3.5

        def distance_from_range(h, start, end):
            if h < start:
                return start - h
            elif h >= end:
                return h - end + 1
            else:
                return 0

        for _, row in df.iterrows():
            name = row["Device"]
            power = float(row["Power (kW)"])
            hours_needed = int(row["Operating Hours"])
            min_hour = int(row["Earliest Hour"])
            max_hour = int(row["Latest Hour"])

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

            summary.append((name, scheduled_hours))

        st.subheader("📅 Hourly Schedule")
        result_table = [{
            "Hour": f"{h:02d}",
            "Devices": ", ".join(schedule[h]["Devices"]),
            "Power (kW)": round(schedule[h]["Power"], 2),
            "Cost (€)": round(schedule[h]["Cost"], 3)
        } for h in range(24)]

        schedule_df = pd.DataFrame(result_table)
        st.dataframe(schedule_df)
        st.success(f"💸 Total Daily Cost with {provider}: €{round(total_cost, 2)}")

        st.subheader("📌 Execution Summary")
        for name, hours in summary:
            if hours:
                label = ", ".join(f"{h:02d}" for h in hours)
                st.markdown(f"**{name}** → {label}")
            else:
                st.markdown(f"❌ **{name}** could not be scheduled.")

        st.subheader("📤 Export Schedule")
        csv_buffer = io.StringIO()
        schedule_df.to_csv(csv_buffer, index=False)
        st.download_button("📄 Download CSV", csv_buffer.getvalue(), file_name="schedule.csv", mime="text/csv")

        st.subheader("📊 Power & Cost Charts")
        st.markdown("<hr style='margin:25px 0'>", unsafe_allow_html=True)
        st.markdown("​")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3), sharey=False, layout='constrained', width_ratios=[1, 1])
        plt.tight_layout()

        ax1.bar(schedule_df["Hour"], schedule_df["Power (kW)"])
        ax1.set_ylabel("Power (kW)", fontsize=9)
        ax1.set_title("Hourly Power Consumption", fontsize=10)
        ax1.tick_params(axis='x', labelrotation=90, labelsize=8)

        ax2.bar(schedule_df["Hour"], schedule_df["Cost (€)"])
        ax2.set_ylabel("Cost (€)", fontsize=9)
        ax2.set_title("Hourly Energy Cost", fontsize=10)
        ax2.tick_params(axis='x', labelrotation=90, labelsize=8)

        st.pyplot(fig)
else:
    st.info("💡 No devices added yet.")
