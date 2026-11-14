# International Debt Analysis

## About the Project

This is my Data Analysis project using Python, MySQL, and Streamlit.

The main objective of this project is to analyze international debt data and understand debt patterns across different countries, regions, and years.

I used Python for data cleaning, MySQL for storing and analyzing the data, and Streamlit for creating an interactive dashboard.

## Tools and Technologies

- Python
- Pandas
- Jupyter Notebook
- MySQL
- SQL
- Streamlit
- Plotly
- VS Code

## Project Files

| File | Description |
|---|---|
| `cleaning.ipynb` | Data cleaning and preparation |
| `app.py` | Streamlit dashboard |
| `README.md` | Project documentation |
| `.gitignore` | Protects private and temporary files |

## Database Information

**Database Name:** `international_debt_final`

The database contains five tables:

| Table | Description |
|---|---|
| countries | Country details |
| indicators | Debt indicator details |
| debt_data | Debt records |
| footnotes | Additional dataset information |
| country_series | Country and indicator metadata |

### Dataset Overview

| Details | Count |
|---|---:|
| Individual countries | 120 |
| Aggregate country groups | 14 |
| Indicators | 577 |
| Debt records | 1,487,450 |
| Footnotes | 1,802 |
| Country series records | 375 |

## Project Objectives

- Clean and prepare international debt data
- Store cleaned data in MySQL
- Understand database relationships
- Perform SQL analysis
- Compare debt across countries
- Analyze regional debt distribution
- Understand yearly debt trends
- Create an interactive dashboard
- Identify useful insights

## Project Workflow

### 1. Data Cleaning

I used Python and Pandas to:

- Understand the dataset
- Check missing values
- Check duplicate records
- Remove unnecessary columns
- Handle missing values
- Prepare the cleaned dataset

### 2. Database Management

I used MySQL to:

- Store the cleaned data
- Create five tables
- Create primary keys
- Create foreign key relationships
- Verify the stored data

### 3. SQL Analysis

I executed 30 SQL queries.

| Level | Queries |
|---|---:|
| Basic | 10 |
| Intermediate | 10 |
| Advanced | 10 |
| Total | 30 |

SQL concepts used:

- SELECT and WHERE
- ORDER BY
- GROUP BY
- Aggregate functions
- JOINS
- Subqueries
- Common Table Expressions (CTEs)
- Window functions
- Ranking functions

### 4. Dashboard Development

I used Streamlit and Plotly to create an interactive dashboard.

The dashboard helps users understand international debt data through charts, filters, and key insights.

## Dashboard Features

- Country-wise debt analysis
- Top 10 countries with the highest debt
- Lowest 10 countries with positive debt
- Regional debt comparison
- Year-wise debt trends
- Long-term and short-term debt analysis
- Interactive country, region, year, and indicator filters
- Dynamic key insights
- SQL analysis section
- CSV download option

## Key Insights Explored

The project helps answer the following questions:

1. Which country has the highest external debt?
2. Which country has the lowest positive external debt?
3. Which region has the highest external debt?
4. How has debt changed over the years?
5. What is India's external debt trend?
6. How is external debt distributed among countries?
7. How do long-term and short-term debt differ?

The dashboard updates its insights based on the selected filters.

## Data Limitations

- Aggregate country groups are excluded from individual-country comparisons to avoid double-counting.
- Some missing values were filled during data cleaning.
- Higher external debt does not automatically mean higher financial risk.
- Additional indicators such as GDP and debt-service payments are useful for further analysis.

## What I Learned

Through this project, I practiced:

- Data cleaning using Python and Pandas
- MySQL database management
- SQL queries and joins
- Data analysis
- Data visualization
- Building interactive dashboards
- Understanding and presenting insights

## Conclusion

This project helped me understand the complete Data Analysis workflow, from cleaning raw data to creating an interactive dashboard.

I gained practical experience using Python, MySQL, SQL, Streamlit, and Plotly to analyze data and present useful information.
