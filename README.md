# ⚡ Smart Load Scheduler

A **Streamlit** web app that builds an **optimal daily schedule** for your household devices, minimizing electricity cost based on your provider’s hourly tariffs, device time windows, and priorities.

---

## ✅ Features
- **Provider tariffs** (GR): ΔΕΗ, ΗΡΩΝ, Elpedison, Protergia (preloaded hourly prices).
- **Clean UX**: sidebar preview chart of the day’s tariff, tabs for a tidy workflow.
- **Device management**
  - **➕ Add Device**: predefined or custom device, power (kW), operating hours, earliest start, latest end, priority.
  - **📋 Device List**: inline editing & quick clear.
  - **📅 Scheduling**: calculates a day plan obeying constraints.
- **Priority-based scheduling**
  - Priority **1** devices are guaranteed (may force schedule if needed).
  - Lower priorities fill cheapest/available slots.
- **Constraints**
  - Time windows per device.
  - **Max total power** cap (default **3.5 kW**).
- **Visualizations**
  - Hourly **Power (kW)** bar chart.
  - Hourly **Cost (€)** bar chart.
  - Sidebar mini **tariff** chart.
- **Export**: download the schedule as **CSV**.
- **Responsive layout** with forms/expanders (advanced options stay out of the way).

---

## 🌐 Live App
👉 https://gkamarinopoulos-smart-energy-schedule.streamlit.app/

---

## 🛠️ Tech Stack
- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Matplotlib](https://matplotlib.org/)

---

## 🚀 Run Locally  
Requires Python 3.10+ (tested on 3.11)  

1. **Clone**  
   git clone https://github.com/gkamarinopoulos/smart-load-scheduler.git  
   cd smart-load-scheduler  

2. **(Recommended) Create & activate a virtual env**  
   python -m venv .venv  

   **Windows:**  
   &nbsp;&nbsp;&nbsp;. .venv/Scripts/activate  

   **macOS/Linux:**  
   &nbsp;&nbsp;&nbsp;source .venv/bin/activate  

3. **Install dependencies**  
   pip install -r requirements.txt  

   **or:**  
   &nbsp;&nbsp;&nbsp;pip install streamlit pandas matplotlib  

4. **Run**  
   streamlit run main.py  
