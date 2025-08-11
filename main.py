import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# ---------- ΒΑΣΙΚΑ ----------
st.set_page_config(page_title="Smart Load Scheduler", layout="wide")
st.title("⚡ Smart Load Scheduler")
st.caption("Οργάνωσε τις συσκευές σου σε ώρες με χαμηλότερη χρέωση, χωρίς να αλλάξεις τίποτα στη λογική.")

# ---------- ΠΑΡΟΧΟΣ (SIDEBAR) ----------
with st.sidebar:
    st.header("🔌 Πάροχος & Τιμολόγιο")
    provider = st.selectbox("Επέλεξε πάροχο:", ["ΔΕΗ", "ΗΡΩΝ", "Elpedison", "Protergia"])
    if provider == "ΔΕΗ":
        tariff = [0.126 if h < 8 or h >= 23 else 0.156 for h in range(24)]
        st.caption("Νυχτερινό: 23:00–08:00 → 0.126 €/kWh, Ημερήσιο: 08:00–23:00 → 0.156 €/kWh")
    elif provider == "ΗΡΩΝ":
        tariff = [0.095] * 24
        st.caption("Σταθερό τιμολόγιο: 0.095 €/kWh")
    elif provider == "Elpedison":
        tariff = [0.099] * 24
        st.caption("Σταθερό τιμολόγιο: 0.099 €/kWh")
    else:
        tariff = [0.094] * 24
        st.caption("Σταθερό τιμολόγιο: 0.094 €/kWh")

    # Μικρό preview διαγράμματος τιμολογίου
    fig_t = plt.figure(figsize=(4, 1.6))
    ax_t = fig_t.add_subplot(111)
    ax_t.bar(list(range(24)), tariff)
    ax_t.set_xlabel("Ώρα")
    ax_t.set_ylabel("€/kWh")
    ax_t.set_xticks(range(0,24,3))
    ax_t.set_title("Ωριαία χρέωση σήμερα", fontsize=10)
    st.pyplot(fig_t, use_container_width=True)

# ---------- ΔΕΔΟΜΕΝΑ ----------
predefined_devices = {
    "Electric stove": 2.0,
    "Refrigerator": 0.15,
    "Washing machine": 1.0,
    "Air conditioner": 1.0,
    "Microwave oven": 1.0,
    "Television": 0.08,
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
    "Fan": 0.06,
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

# ---------- ΔΟΜΗ ΣΕ TABS ----------
tab_add, tab_list, tab_schedule = st.tabs(["➕ Προσθήκη συσκευής", "📋 Λίστα συσκευών", "📅 Προγραμματισμός"])

# --- TAB: Προσθήκη συσκευής ---
with tab_add:
    st.subheader("Πρόσθεσε συσκευή με απλά βήματα")
    with st.form("add_device_form", clear_on_submit=False):
        colA, colB = st.columns([2,3])
        with colA:
            selected = st.selectbox(
                "🔍 Επίλεξε έτοιμη συσκευή (προαιρετικό):",
                options=["---"] + list(predefined_devices.keys()),
                index=0,
                placeholder="e.g. Washing machine"
            )
        with colB:
            custom_device = st.text_input("✏️ Ή γράψε όνομα συσκευής:", "")

        col1, col2 = st.columns(2)
        with col1:
            power = st.number_input(
                "⚡ Ισχύς (kW)",
                min_value=0.01, step=0.01,
                value=predefined_devices.get(selected, 1.0) if selected != "---" else 1.0,
                help="Τυπική ισχύς λειτουργίας"
            )
            duration = st.number_input(
                "⏱ Ώρες λειτουργίας (συνολικά)",
                min_value=1, max_value=24, step=1, value=2
            )
        with col2:
            with st.expander("Προχωρημένα (προαιρετικά)"):
                start_hour = st.number_input("🕒 Πρώιμη ώρα έναρξης (0–23)", min_value=0, max_value=23, value=0)
                end_hour = st.number_input("🕓 Αργότερη ώρα λήξης (1–24)", min_value=1, max_value=24, value=23)
                priority = st.number_input("🔢 Προτεραιότητα (1 = υψηλή)", min_value=1, value=1,
                                           help="Οι συσκευές με προτεραιότητα 1 θα μπουν οπωσδήποτε, ακόμα κι αν ξεπεραστεί προσωρινά το όριο.")

        submitted = st.form_submit_button("➕ Προσθήκη")
        if submitted:
            name = custom_device.strip() if custom_device.strip() else selected
            if not name or name == "---":
                st.warning("⚠️ Διάλεξε ή γράψε έγκυρο όνομα συσκευής.")
            else:
                st.session_state.devices.append({
                    "Device": name,
                    "Power (kW)": power,
                    "Operating Hours": duration,
                    "Earliest Hour": start_hour,
                    "Latest Hour": end_hour,
                    "Priority": priority
                })
                st.success(f"Προστέθηκε: **{name}**")

# --- TAB: Λίστα συσκευών ---
with tab_list:
    st.subheader("Οι συσκευές σου")
    if st.session_state.devices:
        edited_df = st.data_editor(
            pd.DataFrame(st.session_state.devices),
            num_rows="dynamic",
            use_container_width=True
        )
        st.caption("Μπορείς να αλλάξεις τιμές απευθείας στον πίνακα.")

        colL1, colL2 = st.columns([1,1])
        with colL1:
            if st.button("💾 Αποθήκευση αλλαγών"):
                st.session_state.devices = edited_df.to_dict(orient="records")
                st.success("Οι αλλαγές αποθηκεύτηκαν.")
        with colL2:
            if st.button("🗑️ Καθαρισμός λίστας"):
                st.session_state.devices = []
                st.info("Η λίστα άδειασε.")
    else:
        st.info("💡 Δεν έχεις προσθέσει ακόμα συσκευές.")

# --- TAB: Προγραμματισμός ---
with tab_schedule:
    st.subheader("Υπολόγισε πρόγραμμα & κόστος")
    if not st.session_state.devices:
        st.info("Πρόσθεσε πρώτα συσκευές από το παραπάνω tab.")
    else:
        # κουμπί υπολογισμού
        if st.button("🧮 Υπολογισμός Προγράμματος", type="primary"):
            # --- ιδια λογική με τον αρχικό κώδικα ---
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

            # Πίνακας προγράμματος
            result_table = [{
                "Hour": f"{h:02d}:00",
                "Devices": ", ".join(schedule[h]["Devices"]),
                "Power (kW)": round(schedule[h]["Power"], 2),
                "Cost (€)": round(schedule[h]["Cost"], 3)
            } for h in range(24)]
            schedule_df = pd.DataFrame(result_table)

            # Ειδοποιήσεις
            if forced_warnings:
                st.warning("Κάποιες συσκευές υψηλής προτεραιότητας μπήκαν αναγκαστικά εκτός ορίου ισχύος: " +
                           ", ".join(sorted(set(forced_warnings))))

            st.success(f"💸 Συνολικό ημερήσιο κόστος με {provider}: **€{round(total_cost, 2)}**")

            st.markdown("---")
            st.subheader("📅 Ωριαίο πρόγραμμα")
            st.dataframe(schedule_df, use_container_width=True)

            st.subheader("📊 Διαγράμματα")
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

            # Export
            csv_buffer = io.StringIO()
            schedule_df.to_csv(csv_buffer, index=False)
            st.download_button("📄 Λήψη CSV", csv_buffer.getvalue(), file_name="schedule.csv", mime="text/csv")
