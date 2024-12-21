# Import necessary libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Streamlit app configuration
st.set_page_config(
    page_title="Middle School Data Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and header
st.title("Middle School Data Dashboard")
st.header("Analyze and Visualize Student Performance")

# Sidebar for user input
st.sidebar.header("Upload Your Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload a CSV file with student data", type=["csv"]
)

# Required columns
required_columns = [
    'Last Name', 'First Name', 'Student ID', 'Student Grade', 'Academic Year',
    'School', 'Subject', 'Enrolled', 'Sex', 'Hispanic or Latino', 'Race',
    'English Language Learner', 'Special Education', 'Economically Disadvantaged',
    'Migrant', 'Class(es)', 'Class Teacher(s)', 'Report Group(s)', 'Date Range',
    'Date Range Start', 'Date Range End', 'Total Lesson Time-on-Task (min)',
    'i-Ready Overall: Lessons Passed', 'i-Ready Overall: Lessons Completed',
    'i-Ready Overall: % Lessons Passed',
    'i-Ready Pro Overall: Lessons Completed', 'i-Ready Pro Overall: Skills Successful',
    'i-Ready Pro Overall: Skills Completed', 'i-Ready Pro Overall: % Skills Successful',
    'i-Ready Algebra and Algebraic Thinking: Lessons Passed',
    'i-Ready Algebra and Algebraic Thinking: Lessons Completed',
    'i-Ready Algebra and Algebraic Thinking: % Lessons Passed'
]

if uploaded_file:
    # Load data
    data = pd.read_csv(uploaded_file)

    # Sidebar options for visualization
    st.sidebar.header("Visualization Options")
    selected_domain = st.sidebar.selectbox(
        "Select Domain for Analysis", [
            "Algebra and Algebraic Thinking",
            "Number and Operations",
            "Measurement and Data",
            "Geometry"
        ]
    )

    domain_metrics = {
        "Algebra and Algebraic Thinking": [
            'i-Ready Algebra and Algebraic Thinking: Lessons Passed',
            'i-Ready Algebra and Algebraic Thinking: Lessons Completed',
            'i-Ready Algebra and Algebraic Thinking: % Lessons Passed'
        ],
        "Number and Operations": [
            'i-Ready Number and Operations: Lessons Passed',
            'i-Ready Number and Operations: Lessons Completed',
            'i-Ready Number and Operations: % Lessons Passed'
        ],
        "Measurement and Data": [
            'i-Ready Measurement and Data: Lessons Passed',
            'i-Ready Measurement and Data: Lessons Completed',
            'i-Ready Measurement and Data: % Lessons Passed'
        ],
        "Geometry": [
            'i-Ready Geometry: Lessons Passed',
            'i-Ready Geometry: Lessons Completed',
            'i-Ready Geometry: % Lessons Passed'
        ]
    }

    metrics = domain_metrics[selected_domain]

    # Sidebar toggle for view selection
    view_type = st.sidebar.radio(
        "Choose Data View:",
        ("Percentage", "Whole Number")
    )

    # Filter data
    class_avg = data.groupby("Class Teacher(s)")[metrics].mean().reset_index()

    if view_type == "Percentage":
        metric_to_plot = metrics[2]
        title = f"Class Progress (% Lessons Passed) - {selected_domain}"
    else:
        metric_to_plot = metrics[:2]  # Plot both 'Lessons Passed' and 'Lessons Completed'
        title = f"Class Progress (Lessons Passed & Completed) - {selected_domain}"

    # Generate bar chart
    if view_type == "Percentage":
        fig = px.bar(
            class_avg,
            x="Class Teacher(s)",
            y=metric_to_plot,
            title=title,
            labels={metric_to_plot: "% Lessons Passed"},
            color_discrete_sequence=["#1f77b4"]
        )
    else:
        melted_data = class_avg.melt(id_vars="Class Teacher(s)", value_vars=metric_to_plot, 
                                     var_name="Metric", value_name="Value")
        fig = px.bar(
            melted_data,
            x="Class Teacher(s)",
            y="Value",
            color="Metric",
            title=title,
            barmode="group"
        )

    st.plotly_chart(fig)

    st.write("### Additional Analysis")
    st.dataframe(class_avg)  # Display average data for reference

else:
    st.write("Please upload a CSV file to start analyzing data.")
