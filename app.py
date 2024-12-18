import streamlit as st
import pandas as pd
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt

# Function to clean and normalize column names
def clean_column_names(df):
    """
    Clean and normalize column names in the dataframe.
    """
    df.columns = (
        df.columns.str.strip()  # Remove leading/trailing spaces
        .str.replace(" ", "_", regex=True)  # Replace spaces with underscores
        .str.replace(":", "", regex=True)  # Remove colons
        .str.replace("%", "Pct", regex=True)  # Replace '%' with 'Pct'
        .str.replace(r"\(", "", regex=True)  # Remove '('
        .str.replace(r"\)", "", regex=True)  # Remove ')'
        .str.replace("__", "_", regex=True)  # Replace double underscores
        .str.replace("_-_", "_", regex=True)  # Replace '_-_' patterns
        .str.replace(r"[^a-zA-Z0-9_]", "", regex=True)  # Remove other special characters
    )
    return df

# Function to validate columns in the uploaded file
def validate_columns(data, required_columns):
    """
    Ensure that the required columns are present in the uploaded dataset.
    """
    missing_columns = set(required_columns) - set(data.columns)
    if missing_columns:
        st.error(f"The following required columns are missing: {', '.join(missing_columns)}")
        return False
    return True

# Streamlit app setup
st.title("Personalized Instruction Summary (Math)")
st.write("Upload your CSV file to begin analyzing personalized instruction data.")

# File upload
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    # Read the uploaded CSV
    try:
        data = pd.read_csv(uploaded_file)
        data = clean_column_names(data)

        # Display a preview of the cleaned data
        st.subheader("Preview of Cleaned Data")
        st.dataframe(data.head())

        # Define required columns for personalized instruction summary
        required_columns = [
            "Last_Name", "First_Name", "Student_ID", "Student_Grade", "Total_Lesson_TimeonTask_min",
            "iReady_Overall_Lessons_Passed", "iReady_Overall_Lessons_Completed", "iReady_Overall_Pct_Lessons_Passed"
        ]

        if validate_columns(data, required_columns):
            # Filtering options
            st.subheader("Filter Options")
            grades = st.multiselect("Select Grade(s):", options=data["Student_Grade"].unique())
            classes = st.multiselect("Select Class(es):", options=data["Classes"].unique())
            students = st.multiselect("Select Student(s):", options=data["First_Name"].unique())

            # Pass % threshold filter
            pass_threshold = st.slider("Select Pass % Threshold:", 0, 100, 70)

            # Demographic Filter
            st.subheader("Demographic Filters")
            demographics_to_remove = st.multiselect("Remove Demographic Columns:",
                options=["Sex", "Hispanic_or_Latino", "Race", "English_Language_Learner", "Special_Education", "Economically_Disadvantaged"]
            )
            
            # Domain selection
            domain_options = [
                "iReady_Algebra_and_Algebraic_Thinking_Lessons_Passed",
                "iReady_Number_and_Operations_Lessons_Passed",
                "iReady_Measurement_and_Data_Lessons_Passed",
                "iReady_Geometry_Lessons_Passed"
            ]
            selected_domains = st.multiselect("Select Domains to Analyze:", options=domain_options)

            # Filter data based on selections
            filtered_data = data.copy()
            if grades:
                filtered_data = filtered_data[filtered_data["Student_Grade"].isin(grades)]
            if classes:
                filtered_data = filtered_data[filtered_data["Classes"].isin(classes)]
            if students:
                filtered_data = filtered_data[filtered_data["First_Name"].isin(students)]
            
            # Remove demographic columns
            if demographics_to_remove:
                filtered_data = filtered_data.drop(columns=demographics_to_remove, errors="ignore")

            # Combine Lessons Passed and Completed
            for domain in selected_domains:
                base_col = domain.replace("Lessons_Passed", "")
                passed_col = domain
                completed_col = base_col + "Lessons_Completed"
                if passed_col in filtered_data.columns and completed_col in filtered_data.columns:
                    filtered_data[base_col + "Pass_Rate"] = filtered_data.apply(
                        lambda row: row[passed_col] / row[completed_col] * 100 
                        if row[completed_col] > 0 else None, axis=1
                    )

            # Filter out rows where both Passed and Completed are 0
            for domain in selected_domains:
                base_col = domain.replace("Lessons_Passed", "")
                passed_col = domain
                completed_col = base_col + "Lessons_Completed"
                filtered_data = filtered_data[~((filtered_data[passed_col] == 0) & (filtered_data[completed_col] == 0))]

            # Display filtered data
            st.subheader("Filtered Data")
            st.dataframe(filtered_data)

            # Display failing students
            st.subheader("Students Below Pass % Threshold")
            failing_students = filtered_data[
                filtered_data["iReady_Overall_Pct_Lessons_Passed"] < pass_threshold
            ]
            st.write(f"Students with Pass % below {pass_threshold}:")
            st.dataframe(failing_students)

            # Initial Data Analysis
            st.subheader("Initial Data Analysis")
            st.write("Summary of key metrics:")
            summary = filtered_data[[
                "Total_Lesson_TimeonTask_min",
                "iReady_Overall_Lessons_Passed",
                "iReady_Overall_Lessons_Completed",
                "iReady_Overall_Pct_Lessons_Passed"
            ]].describe()
            st.dataframe(summary)

            # Scatter Plot for Relationships
            st.subheader("Scatter Plots")
            scatter_chart = alt.Chart(filtered_data).mark_circle(size=60).encode(
                x="Total_Lesson_TimeonTask_min",
                y="iReady_Overall_Lessons_Passed",
                tooltip=["First_Name", "Last_Name", "Total_Lesson_TimeonTask_min", "iReady_Overall_Lessons_Passed"]
            ).interactive()
            st.altair_chart(scatter_chart, use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
