import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------
# Page Configuration
# ---------------------------------------------------
st.set_page_config(
    page_title="Care Transition Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Care Transition Efficiency & Placement Outcome Analytics")
st.markdown("Analyze efficiency, bottlenecks, and placement outcomes in the UAC care pipeline.")

# ---------------------------------------------------
# Load Dataset
# ---------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/HHS_Unaccompanied_Alien_Children_Program.csv")

    # Rename columns
    df.columns = [
        'date',
        'cbp_apprehended',
        'cbp_custody',
        'cbp_transferred',
        'hhs_care',
        'hhs_discharged'
    ]

    # Convert date
    df['date'] = pd.to_datetime(df['date'])

    # Clean numeric columns
    numeric_cols = [
        'cbp_apprehended',
        'cbp_custody',
        'cbp_transferred',
        'hhs_care',
        'hhs_discharged'
    ]

    for col in numeric_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(',', '', regex=False)
        )

        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Create KPIs
    df['transfer_efficiency'] = (
        df['cbp_transferred'] / df['cbp_custody']
    )

    df['discharge_effectiveness'] = (
        df['hhs_discharged'] / df['hhs_care']
    )

    df['throughput_rate'] = (
        df['hhs_discharged'] / df['cbp_apprehended']
    )

    df['backlog_rate'] = (
        df['cbp_apprehended'] - df['hhs_discharged']
    )

    return df


df = load_data()

# ---------------------------------------------------
# Sidebar Filters
# ---------------------------------------------------
st.sidebar.header("Filters")

start_date = st.sidebar.date_input(
    "Start Date",
    df['date'].min()
)

end_date = st.sidebar.date_input(
    "End Date",
    df['date'].max()
)

filtered_df = df[
    (df['date'] >= pd.to_datetime(start_date)) &
    (df['date'] <= pd.to_datetime(end_date))
]

# ---------------------------------------------------
# KPI Cards
# ---------------------------------------------------
st.subheader("📌 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Transfer Efficiency",
        f"{filtered_df['transfer_efficiency'].mean():.2f}"
    )

with col2:
    st.metric(
        "Discharge Effectiveness",
        f"{filtered_df['discharge_effectiveness'].mean():.2f}"
    )

with col3:
    st.metric(
        "Throughput Rate",
        f"{filtered_df['throughput_rate'].mean():.2f}"
    )

with col4:
    st.metric(
        "Average Backlog",
        f"{filtered_df['backlog_rate'].mean():.0f}"
    )

# ---------------------------------------------------
# Pipeline Flow Chart
# ---------------------------------------------------
st.subheader("📈 Pipeline Flow Trends")

fig = px.line(
    filtered_df,
    x='date',
    y=[
        'cbp_custody',
        'cbp_transferred',
        'hhs_care',
        'hhs_discharged'
    ],
    labels={"value": "Children", "date": "Date"},
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# Transfer Efficiency Trend
# ---------------------------------------------------
st.subheader("🔄 Transfer Efficiency Trend")

fig2 = px.line(
    filtered_df,
    x='date',
    y='transfer_efficiency',
    title='Transfer Efficiency Over Time'
)

st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------
# Discharge Effectiveness Trend
# ---------------------------------------------------
st.subheader("🏠 Discharge Effectiveness Trend")

fig3 = px.line(
    filtered_df,
    x='date',
    y='discharge_effectiveness',
    title='Discharge Effectiveness Over Time'
)

st.plotly_chart(fig3, use_container_width=True)

# ---------------------------------------------------
# Backlog Analysis
# ---------------------------------------------------
st.subheader("⚠️ Backlog Accumulation")

fig4 = px.bar(
    filtered_df,
    x='date',
    y='backlog_rate',
    title='Backlog Rate'
)

st.plotly_chart(fig4, use_container_width=True)

# ---------------------------------------------------
# Bottleneck Detection
# ---------------------------------------------------
st.subheader("🚨 Bottleneck Detection")

threshold = st.slider(
    "Select Backlog Threshold",
    min_value=0,
    max_value=int(filtered_df['backlog_rate'].max()),
    value=500
)

critical_days = filtered_df[
    filtered_df['backlog_rate'] > threshold
]

st.write(f"Number of Critical Days: {len(critical_days)}")

st.dataframe(
    critical_days[
        ['date', 'backlog_rate']
    ]
)

# ---------------------------------------------------
# Raw Data
# ---------------------------------------------------
st.subheader("📄 Raw Dataset")

st.dataframe(filtered_df)

# ---------------------------------------------------
# Download Button
# ---------------------------------------------------
csv = filtered_df.to_csv(index=False)

st.download_button(
    label="📥 Download Filtered Data",
    data=csv,
    file_name="filtered_uac_data.csv",
    mime="text/csv"
)
