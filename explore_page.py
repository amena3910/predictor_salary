import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Function to shorten categories based on a cutoff value
def shorten_categories(categories, cutoff):
    categorical_map = {}
    for i in range(len(categories)):
        if categories.values[i] >= cutoff:
            categorical_map[categories.index[i]] = categories.index[i]
        else:
            categorical_map[categories.index[i]] = 'Other'
    return categorical_map

# Clean the 'YearsCodePro' experience data
def clean_experience(x):
    if x == 'More than 50 years':
        return 50
    if x == 'Less than 1 year':
        return 0.5
    return float(x)

# Clean the 'EdLevel' education data
def clean_education(x):
    if 'Bachelor’s degree' in x:
        return 'Bachelor’s degree'
    if 'Master’s degree' in x:
        return 'Master’s degree'
    if 'Professional degree' in x or 'Other doctoral degree' in x:
        return 'Post grad'
    return 'Less than a bachelor'

# Load and clean data using Streamlit's caching mechanism
@st.cache_data
def load_data():
    # Ensure the correct file path and format
    survey = pd.read_csv('survey_results_public.zip', compression='zip', header=0, sep=',', quotechar='"')

    # Select relevant columns and rename for clarity
    survey = survey[['Country', 'EdLevel', 'YearsCodePro', 'Employment', 'ConvertedComp']]
    survey = survey.rename({'ConvertedComp': 'Salary'}, axis=1)
    survey = survey[survey['Salary'].notnull()]
    survey = survey.dropna()
    survey = survey.drop('Employment', axis=1)

    # Shorten country categories
    country_map = shorten_categories(survey.Country.value_counts(), 400)
    survey['Country'] = survey['Country'].map(country_map)

    # Remove salary outliers
    survey = survey[survey['Salary'] <= 250000]
    survey = survey[survey['Salary'] >= 10000]
    survey = survey[survey['Salary'] != 'Others']

    # Clean 'YearsCodePro' and 'EdLevel'
    survey['YearsCodePro'] = survey['YearsCodePro'].apply(clean_experience)
    survey['EdLevel'] = survey['EdLevel'].apply(clean_education)

    return survey

# Load the cleaned survey data
survey = load_data()

# Main page for exploring data
def show_explore_page():
    st.title("Annual  Salary Prediction of AI Jobs")

    st.write("""
    ### Stack Overflow Developer Survey 2022
    """)

    # Visualize the number of data points from different countries
    data = survey['Country'].value_counts()
    fig1, ax1 = plt.subplots()
    ax1.pie(data, labels=data.index, shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle

    st.write("#### Number of Data from Different Countries")
    st.pyplot(fig1)

    # Mean salary by country
    st.write("#### Mean Salary Based on Country")
    country_salary = survey.groupby(['Country'])['Salary'].mean().sort_values(ascending=True)
    st.bar_chart(country_salary)

    # Mean salary based on experience
    st.write("#### Mean Salary Based on Experience")
    experience_salary = survey.groupby(['YearsCodePro'])['Salary'].mean().sort_values(ascending=True)
    st.line_chart(experience_salary)
