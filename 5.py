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

    st.write("### Preview of Uploaded Data")
    st.dataframe(data.head())

    # Sidebar filters
    st.sidebar.header("Filters")
    grade_filter = st.sidebar.multiselect(
        "Select Student Grades",
        options=sorted(data['Student Grade'].unique()),
        default=sorted(data['Student Grade'].unique())
    )
    teacher_filter = st.sidebar.multiselect(
        "Select Class Teachers",
        options=sorted(data['Class Teacher(s)'].dropna().unique()),
        default=sorted(data['Class Teacher(s)'].dropna().unique())
    )

    filtered_data = data[
        (data['Student Grade'].isin(grade_filter)) &
        (data['Class Teacher(s)'].isin(teacher_filter))
    ]

    st.write("### Filtered Data")
    st.dataframe(filtered_data)

    # Key Metrics Analysis
    st.write("### Key Metrics Analysis: i-Ready")
    fig, ax = plt.subplots()
    sns.scatterplot(
        data=filtered_data,
        x='Total Lesson Time-on-Task (min)',
        y='Total Lesson Time-on-Task (min)',
        ax=ax
    )
    ax.set_title("Scatter Plot: Total Lesson Time-on-Task (min) vs Total Lesson Time-on-Task (min)")
    st.pyplot(fig)

    # Domain Analysis
    st.subheader("Domain Analysis")
    domains = {
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

    selected_domain = st.selectbox("Select Domain for Analysis", options=list(domains.keys()))
    domain_columns = domains[selected_domain]

    # Filter out students who haven't started any lessons in the selected domain
    def filter_non_started_students(df, columns):
        return df[(df[columns].sum(axis=1) > 0) & (~df[columns].isna().all(axis=1))]

    filtered_comparison_data = filter_non_started_students(filtered_data, domain_columns)

    st.write(f"### Students with {selected_domain} % Passed Below 50%")
    failing_students = filtered_comparison_data[filtered_comparison_data[domain_columns[2]] < 50]
    st.dataframe(failing_students[['Last Name', 'First Name', 'Student ID'] + domain_columns])

    # Class vs Other Classes Comparison - Grouped Bar Chart
    st.write("### Class Progress vs Other Selected Classes")
    class_avg = filtered_comparison_data.groupby("Class Teacher(s)")[domain_columns].mean().reset_index()
    melted_data = class_avg.melt(id_vars="Class Teacher(s)", var_name="Metric", value_name="Value")
    fig = px.bar(
        melted_data, 
        x="Class Teacher(s)", 
        y="Value", 
        color="Metric", 
        title=f"{selected_domain} - Class Progress vs Selected Classes",
        barmode="group"
    )
    st.plotly_chart(fig)

    # Student Progress Distribution
    st.write("### Student Progress Distribution")
    fig, ax = plt.subplots()
    sns.histplot(filtered_comparison_data[domain_columns[2]], bins=10, kde=True, ax=ax)
    ax.set_title(f"Distribution of % Lessons Passed in {selected_domain}")
    st.pyplot(fig)

    # Correlation within Domain
    st.write("### Correlation Analysis for Domain Metrics")
    fig, ax = plt.subplots()
    sns.heatmap(filtered_comparison_data[domain_columns].corr(), annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

else:
    st.write("Please upload a CSV file to start analyzing data.")
