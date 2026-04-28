# EU New Passenger Cars CO2 Dashboard

Interactive Streamlit dashboard analysing average CO2 emissions per kilometre from newly registered passenger cars across European countries (2000-2024).

**Module:** 5DATA004W Data Science Project Lifecycle  
**Author:** Mazin Al-Busaidy (w2115071)  
**Data source:** European Environment Agency, EU SDG indicator 13.31

## Live links

- **Streamlit app:** https://eu-co2-dashboard-zm6yawvzeodmpd2w4jwgjl.streamlit.app
- **GitHub repository:** https://github.com/MazinAl-Busaidy/eu-co2-dashboard
- **Video demo:** https://westminster.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=e746b5d0-01f0-418a-9278-b43a00a873ae
- **Report:** [report/w2115071_5DATA004W_Data_Science_Project_Lifecycle.pdf](report/w2115071_5DATA004W_Data_Science_Project_Lifecycle.pdf)

## What the dashboard does

The dashboard provides four views of the dataset:

- **Overview** — KPIs (EU average, change since 2000, lowest and highest emitter), choropleth map of Europe and a ranked bar chart of all countries for the latest year.
- **Trends** — multi-country line chart with adjustable year range and country picker. The 2021 NEDC to WLTP test procedure change is annotated to keep readers from misreading the step in the data as a real spike.
- **Country deep-dive** — a single-country view showing latest value, net change since 2000, EU rank, and gap to the EU average, plus a country-vs-EU-average line chart and a year-on-year change bar chart.
- **Data** — filterable table of the underlying observations with a CSV download.

## Run locally

\`\`\`
git clone https://github.com/MazinAl-Busaidy/eu-co2-dashboard.git
cd eu-co2-dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
\`\`\`
