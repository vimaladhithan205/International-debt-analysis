
# International Debt Analysis Dashboard

## Project Overview

The International Debt Analysis Dashboard is a data analytics project developed using Python, MySQL, Pandas, Plotly, and Streamlit.

The project analyzes external debt across different countries, regions, years, and debt categories.

It transforms complex debt data into interactive visualizations and understandable insights to support data exploration and comparison.

## Project Objectives

- Analyze external debt across countries.
- Identify countries with the highest external debt.
- Understand historical debt trends.
- Compare regional debt distribution.
- Analyze long-term and short-term debt.
- Measure year-over-year debt changes.
- Identify debt concentration among countries.
- Generate dynamic analytical insights.

## Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Application development |
| MySQL | Database management |
| Pandas | Data processing and analysis |
| Plotly | Interactive data visualization |
| Streamlit | Web dashboard development |
| VS Code | Development environment |

## Database Structure

Database Name: `international_debt_final`

The project uses five tables:

1. `countries` - Country information and regions.
2. `indicators` - Debt indicator information.
3. `debt_data` - External debt values across countries and years.
4. `footnotes` - Additional dataset notes.
5. `country_series` - Country-series information.

### Main Debt Indicators

| Indicator | Series Code |
|-----------|-------------|
| Total External Debt | DT.DOD.DECT.CD |
| Long-term Debt | DT.DOD.DLXF.CD |
| Short-term Debt | DT.DOD.DSTC.CD |

Debt values are displayed in US$ billions.

## Dashboard Features

The application contains two separate pages:

### 1. Dashboard

The Dashboard provides four interactive filters:

- Year
- Region
- Country
- Debt Type

### Key Performance Indicators (KPIs)

1. Total Countries
2. Total External Debt
3. Average Debt per Country
4. Selected Year

### Nine Interactive Visualizations

1. **Top 10 Countries by External Debt**
   - Identifies countries with the highest debt.

2. **External Debt Trend**
   - Analyzes historical changes in external debt.

3. **Regional Debt Distribution**
   - Compares debt contributions across regions.

4. **Debt Type Comparison**
   - Compares long-term and short-term debt.

5. **Year-over-Year Debt Change**
   - Identifies increases and decreases in debt.

6. **Country-Year Debt Heatmap**
   - Visualizes debt patterns across countries and years.

7. **Top 5 Debt Concentration**
   - Measures the share of debt held by the top five countries.

8. **Country vs Regional Average**
   - Compares a selected country's debt with its regional average.

9. **Annual Debt Growth Rate**
   - Calculates percentage changes in debt over time.

## Dynamic Analytical Insights

The dashboard generates nine data-driven insights based on the selected filters.

1. Highest External Debt Country
2. Historical Debt Trend
3. Largest Regional Debt Share
4. Long-term vs Short-term Debt
5. Year-over-Year Debt Change
6. Country-Year Debt Patterns
7. Top Five Debt Concentration
8. Country vs Regional Average
9. Annual Debt Growth Rate

These insights help users understand the results without manually calculating every value.

## SQL Queries Page

The SQL Queries page contains 30 analytical queries organized into three difficulty levels.

### Basic SQL - 10 Queries

Covers:

- SELECT
- WHERE
- DISTINCT
- COUNT
- MIN
- MAX
- ORDER BY

### Intermediate SQL - 10 Queries

Covers:

- JOIN
- GROUP BY
- HAVING
- SUM
- AVG
- Data aggregation

### Advanced SQL - 10 Queries

Covers:

- Common Table Expressions (CTEs)
- Subqueries
- CASE statements
- Window functions
- RANK
- DENSE_RANK
- ROW_NUMBER
- LAG

## Installation and Setup

### Step 1: Install Python Libraries

Open the VS Code terminal and run:

```bash
pip install streamlit pandas plotly mysql-connector-python
```

### Step 2: Prepare MySQL Database

Ensure that MySQL Server is running and the database exists.

```sql
SHOW DATABASES;

USE international_debt_final;

SHOW TABLES;
```

### Step 3: Configure MySQL Connection

Create a folder named `.streamlit`.

Inside it, create a file named `secrets.toml`.

```toml
[mysql]
host = "localhost"
user = "root"
password = "YOUR_MYSQL_PASSWORD"
database = "international_debt_final"
port = 3306
```

Replace `YOUR_MYSQL_PASSWORD` with your actual MySQL password.

Do not upload this file to GitHub.

### Step 4: Run the Application

Open the terminal in your project directory.

```bash
python -m streamlit run app.py
```

Open the local URL displayed by Streamlit.

Usually:

`http://localhost:8501`

## Project Folder Structure

```text
International-Debt-Analysis/
|
|-- app.py
|-- README.md
|
|-- .streamlit/
    |-- secrets.toml
```

## Project Workflow

1. Data Collection
2. Data Inspection
3. Data Cleaning
4. Data Validation
5. MySQL Database Integration
6. SQL Analysis
7. Data Visualization
8. Streamlit Dashboard Development
9. Insight Generation

## Data Validation

The project includes checks and calculations to improve analytical reliability.

- Detects duplicate country-year-indicator records.
- Excludes identified aggregate country groups.
- Handles missing observations in visualizations.
- Compares matched countries for yearly debt changes.
- Uses consistent country coverage for historical trend analysis.
- Avoids adding total debt to its components.

## Skills Demonstrated

- Python programming
- SQL querying
- MySQL database integration
- Pandas data analysis
- Data cleaning and validation
- Interactive data visualization
- KPI development
- Dashboard development
- Analytical problem-solving
- Data interpretation

## Project Limitations

- Requires a prepared MySQL database.
- Some comparisons depend on data availability.
- Historical data may include values filled during cleaning.
- Absolute external debt does not independently measure a country's financial health.

## Future Improvements

- Add debt-to-GDP comparisons.
- Include additional economic indicators.
- Improve data-quality reporting.
- Add automated validation tests.
- Deploy the dashboard for online access.

## Project Status

The project includes an interactive Streamlit dashboard with nine visualizations, nine dynamic insights, and 30 SQL queries.

End-to-end testing with the live MySQL database is still required before deployment.
