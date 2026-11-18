import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector

st.set_page_config(page_title="International Debt Analysis", layout="wide")
st.title("International Debt Analysis")

INDICATORS = {
    "Total External Debt": "DT.DOD.DECT.CD",
    "Long-term Debt": "DT.DOD.DLXF.CD",
    "Short-term Debt": "DT.DOD.DSTC.CD",
}
BILLION = 1_000_000_000

@st.cache_data(ttl=300)
def get_data(query, params=None):
    """Run a parameterized SELECT query and close the connection."""
    try:
        cfg = st.secrets["mysql"] if "mysql" in st.secrets else {}
        host = cfg.get("host", st.secrets.get("mysql_host", "localhost"))
        user = cfg.get("user", st.secrets.get("mysql_user", "root"))
        password = cfg.get("password", st.secrets.get("mysql_password", ""))
        database = cfg.get("database", st.secrets.get("mysql_database", "international_debt_final"))
        port = int(cfg.get("port", st.secrets.get("mysql_port", 3306)))
    except (FileNotFoundError, KeyError):
        host, user, password, database, port = "localhost", "root", "", "international_debt_final", 3306

    connection = mysql.connector.connect(
        host=host, user=user, password=password, database=database,
        port=port, connection_timeout=10
    )
    try:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
        finally:
            cursor.close()
    finally:
        connection.close()


def one_record_per_key(frame):
    """Do not silently double-count duplicated country/year/indicator rows."""
    keys = ["Code", "Year", "Indicator"]
    duplicate_count = int(frame.duplicated(keys).sum())
    if duplicate_count:
        st.error(f"Found {duplicate_count} duplicate country-year-indicator records. "
                 "Please validate the debt_data table before analysis.")
        st.stop()
    return frame


def comparable_years(frame):
    """Yearly totals using countries with observations in every displayed year."""
    pivot = frame.pivot(index="Code", columns="Year", values="Debt")
    pivot = pivot.dropna()
    if pivot.empty:
        return pd.DataFrame(columns=["Year", "Debt"]), 0
    totals = pivot.sum(axis=0).reset_index()
    totals.columns = ["Year", "Debt"]
    return totals.sort_values("Year"), len(pivot)


with st.sidebar:
    st.header("Pages")
    page = st.radio("Navigation", ["Dashboard", "SQL Queries"],
                    label_visibility="collapsed")

if page == "Dashboard":
    try:
        years = get_data("SELECT DISTINCT `Year` FROM debt_data ORDER BY `Year` DESC")
        countries = get_data(
            "SELECT `Code`, `Short Name`, `Region` FROM countries "
            "WHERE `Region` <> 'Unknown' AND `Region` IS NOT NULL "
            "ORDER BY `Short Name`"
        )
    except Exception:
        st.error("Cannot connect to MySQL. Check the server, database and .streamlit/secrets.toml.")
        st.stop()

    if years.empty or countries.empty:
        st.warning("No countries or years available.")
        st.stop()

    st.subheader("Filters")
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        year = int(st.selectbox("Year", years["Year"].dropna().astype(int).tolist()))
    with f2:
        region = st.selectbox("Region", ["All Regions"] + sorted(countries["Region"].unique()))
    allowed = countries if region == "All Regions" else countries[countries["Region"] == region]
    with f3:
        country = st.selectbox("Country", ["All Countries"] + allowed["Short Name"].tolist())
    with f4:
        debt_type = st.selectbox("Debt Type", list(INDICATORS))

    sql = """
        SELECT d.`Country Code` AS Code, c.`Short Name` AS Country,
               c.`Region` AS Region, d.`Year` AS Year,
               d.`Series Code` AS Indicator, d.`Value` / 1000000000 AS Debt
        FROM debt_data d
        JOIN countries c ON d.`Country Code` = c.`Code`
        WHERE c.`Region` <> 'Unknown'
          AND d.`Series Code` IN (%s, %s, %s)
          AND d.`Value` IS NOT NULL
    """
    parameters = list(INDICATORS.values())
    if region != "All Regions":
        sql += " AND c.`Region` = %s"
        parameters.append(region)
    if country != "All Countries":
        selected_code = allowed.loc[allowed["Short Name"] == country, "Code"].iloc[0]
        sql += " AND d.`Country Code` = %s"
        parameters.append(selected_code)

    try:
        df = get_data(sql, tuple(parameters))
    except Exception:
        st.error("Unable to load debt records. Verify the database tables and columns.")
        st.stop()

    if df.empty:
        st.warning("No data available for the chosen filters.")
        st.stop()

    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Debt"] = pd.to_numeric(df["Debt"], errors="coerce")
    df = df.dropna(subset=["Year", "Debt"])
    df["Year"] = df["Year"].astype(int)
    df = one_record_per_key(df)

    selected = df[df["Indicator"] == INDICATORS[debt_type]]
    current = selected[selected["Year"] == year].copy()
    if current.empty:
        st.warning("No debt data for the selected year.")
        st.stop()

    by_country = current.groupby(["Code", "Country", "Region"], as_index=False)["Debt"].sum()
    by_region = by_country.groupby("Region", as_index=False)["Debt"].sum()
    total = by_country["Debt"].sum()
    years_comp, common_count = comparable_years(selected)
    st.caption(f"Trend comparisons use {common_count} countries with data in every displayed year. "
               "Country/region charts use available observations in the selected year.")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Countries", len(by_country))
    m2.metric("Total Debt (US$ bn)", f"{total:,.2f}")
    m3.metric("Average per Country (US$ bn)", f"{by_country['Debt'].mean():,.2f}")
    m4.metric("Selected Year", year)

    st.subheader("1. Top 10 Countries")
    top10 = by_country.nlargest(10, "Debt")
    st.plotly_chart(px.bar(top10.sort_values("Debt"), x="Debt", y="Country",
                           orientation="h", labels={"Debt": "US$ billion"}),
                    use_container_width=True)

    st.subheader("2. Comparable Debt Trend")
    if len(years_comp) >= 2:
        st.plotly_chart(px.line(years_comp, x="Year", y="Debt", markers=True,
                                labels={"Debt": "US$ billion"}), use_container_width=True)
    else:
        st.info("At least two comparable years are needed.")

    left, right = st.columns(2)
    with left:
        st.subheader("3. Regional Debt Share")
        if region == "All Regions" and country == "All Countries" and len(by_region) > 1:
            st.plotly_chart(px.pie(by_region[by_region["Debt"] > 0], names="Region",
                                   values="Debt", hole=0.45), use_container_width=True)
        else:
            st.info("Select All Regions and All Countries.")
    with right:
        st.subheader("4. Debt Composition")
        component = df[df["Year"] == year].groupby("Indicator")["Debt"].sum()
        type_df = pd.DataFrame({
            "Type": ["Long-term Debt", "Short-term Debt"],
            "Debt": [component.get(INDICATORS["Long-term Debt"], float("nan")),
                     component.get(INDICATORS["Short-term Debt"], float("nan"))],
        }).dropna()
        if not type_df.empty:
            st.plotly_chart(px.bar(type_df, x="Type", y="Debt",
                                   labels={"Debt": "US$ billion"}), use_container_width=True)
        else:
            st.info("Debt components are unavailable.")

    st.subheader("5. Year-over-Year Change")
    previous = selected[selected["Year"] == year - 1][["Code", "Country", "Debt"]]
    now = current[["Code", "Country", "Debt"]]
    change = now.merge(previous, on="Code", suffixes=("_now", "_prev"))
    if not change.empty:
        change["Difference"] = change["Debt_now"] - change["Debt_prev"]
        change["Country"] = change["Country_now"]
        shown = pd.concat([change.nsmallest(8, "Difference"),
                           change.nlargest(8, "Difference")]).drop_duplicates("Code")
        st.plotly_chart(px.bar(shown.sort_values("Difference"), x="Difference",
                               y="Country", orientation="h",
                               color="Difference", color_continuous_scale="RdYlGn"),
                        use_container_width=True)
    else:
        st.info("No countries have values in both the selected and previous year.")

    st.subheader("6. Country-Year Heatmap")
    heat = selected[selected["Code"].isin(top10["Code"])].pivot(
        index="Country", columns="Year", values="Debt"
    )
    if not heat.empty:
        st.plotly_chart(px.imshow(heat, aspect="auto",
                                  labels={"color": "US$ billion"}), use_container_width=True)

    left, right = st.columns(2)
    positive = by_country[by_country["Debt"] > 0]
    with left:
        st.subheader("7. Top 5 Concentration")
        if len(positive) > 5:
            top5_sum = positive.nlargest(5, "Debt")["Debt"].sum()
            groups = pd.DataFrame({
                "Group": ["Top 5 Countries", "Other Countries"],
                "Debt": [top5_sum, positive["Debt"].sum() - top5_sum],
            })
            st.plotly_chart(px.pie(groups, names="Group", values="Debt", hole=0.45),
                            use_container_width=True)
        else:
            st.info("Choose at least six countries with positive debt.")

    region_average = None
    with right:
        st.subheader("8. Country vs Regional Average")
        if country != "All Countries":
            selected_region = current["Region"].iloc[0]
            try:
                regional = get_data("""
                    SELECT d.`Country Code` AS Code,
                           d.`Value` / 1000000000 AS Debt
                    FROM debt_data d JOIN countries c ON d.`Country Code` = c.`Code`
                    WHERE c.`Region` = %s AND d.`Year` = %s
                      AND d.`Series Code` = %s AND d.`Value` IS NOT NULL
                """, (selected_region, year, INDICATORS[debt_type]))
                if regional["Code"].duplicated().any():
                    st.warning("Duplicate regional observations: comparison unavailable.")
                elif not regional.empty:
                    region_average = regional["Debt"].mean()
                    comparison = pd.DataFrame({
                        "Category": [country, "Regional Average"],
                        "Debt": [float(current["Debt"].iloc[0]), region_average],
                    })
                    st.plotly_chart(px.bar(comparison, x="Category", y="Debt"),
                                    use_container_width=True)
            except Exception:
                st.warning("Regional average could not be loaded.")
        else:
            st.info("Select one country to see its regional comparison.")

    st.subheader("9. Annual Debt Growth Rate")
    growth = years_comp.copy()
    if len(growth) >= 2:
        growth["Growth (%)"] = growth["Debt"].pct_change(fill_method=None) * 100
        growth.loc[growth["Year"].diff() != 1, "Growth (%)"] = float("nan")
        growth.loc[growth["Debt"].shift(1) <= 0, "Growth (%)"] = float("nan")
        valid_growth = growth.dropna(subset=["Growth (%)"])
        if not valid_growth.empty:
            st.plotly_chart(px.line(valid_growth, x="Year", y="Growth (%)",
                                    markers=True), use_container_width=True)
        else:
            st.info("No consecutive years with valid growth rates.")
    else:
        valid_growth = pd.DataFrame(columns=["Year", "Growth (%)"])
        st.info("At least two comparable years are needed.")

    st.header("Data-Driven Insights")
    highest = by_country.loc[by_country["Debt"].idxmax()]
    st.write(f"**1. Highest debt:** {highest['Country']} has the largest {debt_type.lower()} "
             f"among the selected countries in {year}: US$ {highest['Debt']:,.2f} billion.")

    if len(years_comp) >= 2:
        first, last = years_comp.iloc[0], years_comp.iloc[-1]
        movement = "increased" if last["Debt"] > first["Debt"] else (
            "decreased" if last["Debt"] < first["Debt"] else "stayed unchanged")
        st.write(f"**2. Comparable trend:** Debt {movement} from US$ {first['Debt']:,.2f} "
                 f"billion ({int(first['Year'])}) to US$ {last['Debt']:,.2f} billion "
                 f"({int(last['Year'])}) across the same {common_count} countries.")
    else:
        st.write("**2. Comparable trend:** Insufficient comparable years.")

    if region == "All Regions" and country == "All Countries" and total > 0:
        biggest = by_region.loc[by_region["Debt"].idxmax()]
        st.write(f"**3. Regional share:** {biggest['Region']} contributes "
                 f"{biggest['Debt']/total*100:.2f}% of selected countries' debt.")
    else:
        st.write("**3. Regional share:** Select all regions and all countries to compare.")

    long_term = component.get(INDICATORS["Long-term Debt"])
    short_term = component.get(INDICATORS["Short-term Debt"])
    if pd.notna(long_term) and pd.notna(short_term):
        st.write(f"**4. Debt composition:** Long-term debt is US$ {long_term:,.2f} billion; "
                 f"short-term debt is US$ {short_term:,.2f} billion. "
                 "These are components, not additional amounts on top of total debt.")
    else:
        st.write("**4. Debt composition:** Both components are needed.")

    if not change.empty:
        increases = change[change["Difference"] > 0]
        decreases = change[change["Difference"] < 0]
        pieces = []
        if not increases.empty:
            rise = increases.loc[increases["Difference"].idxmax()]
            pieces.append(f"largest increase: {rise['Country']} (+US$ {rise['Difference']:,.2f} bn)")
        if not decreases.empty:
            fall = decreases.loc[decreases["Difference"].idxmin()]
            pieces.append(f"largest decrease: {fall['Country']} (US$ {fall['Difference']:,.2f} bn)")
        st.write("**5. Year-over-year change:** " + ("; ".join(pieces) if pieces else
                 "No change among matched countries.") + ".")
    else:
        st.write("**5. Year-over-year change:** No matched observations.")

    if not heat.empty and heat.notna().any().any():
        peak_country, peak_year = heat.stack().idxmax()
        peak_amount = heat.loc[peak_country, peak_year]
        st.write(f"**6. Heatmap:** Among displayed cells, {peak_country} in {int(peak_year)} "
                 f"has the highest debt (US$ {peak_amount:,.2f} bn).")
    else:
        st.write("**6. Heatmap:** No values to compare.")

    if len(positive) > 5 and positive["Debt"].sum() > 0:
        concentration = positive.nlargest(5, "Debt")["Debt"].sum() / positive["Debt"].sum() * 100
        st.write(f"**7. Debt concentration:** The top five countries account for "
                 f"{concentration:.2f}% of positive debt among the selected countries.")
    else:
        st.write("**7. Debt concentration:** Select at least six countries with positive debt.")

    if region_average is not None:
        amount = float(current["Debt"].iloc[0])
        comparison = "above" if amount > region_average else (
            "below" if amount < region_average else "equal to")
        st.write(f"**8. Regional comparison:** {country} is {comparison} its regional "
                 f"country average (US$ {amount:,.2f} bn vs US$ {region_average:,.2f} bn).")
    else:
        st.write("**8. Regional comparison:** Select one country.")

    rate_row = valid_growth[valid_growth["Year"] == year]
    if not rate_row.empty:
        rate = float(rate_row["Growth (%)"].iloc[0])
        st.write(f"**9. Annual growth:** Comparable-country debt changed "
                 f"{rate:+.2f}% from {year-1} to {year}.")
    else:
        st.write("**9. Annual growth:** No comparable growth rate for the selected year.")


if page == "SQL Queries":
    st.header("SQL Queries")
    st.caption("30 practice queries: Basic, Intermediate and Advanced")
    base = """from debt_data d join countries c on d.`Country Code`=c.`Code`
where d.`Year`=2024 and d.`Series Code`='DT.DOD.DECT.CD' and c.`Region`<>'Unknown'"""
    by_country = f"select d.`Country Name` as Country, d.`Value` as Debt_USD {base}"
    by_region = f"select c.`Region` as Region, sum(d.`Value`) as Debt_USD {base} group by c.`Region`"
    questions = {
        "Basic": [
            ("1. First 10 debt records", "select * from debt_data limit 10"),
            ("2. Count individual countries", "select count(*) as total_countries from countries where `Region` <> 'Unknown'"),
            ("3. Count indicator definitions", "select count(*) as total_indicators from indicators"),
            ("4. Count debt records", "select count(*) as total_records from debt_data"),
            ("5. First and last years", "select min(`Year`) as first_year, max(`Year`) as last_year from debt_data"),
            ("6. Unique regions", "select distinct `Region` from countries where `Region` <> 'Unknown' order by `Region`"),
            ("7. Income groups", "select distinct `Income Group` from countries order by `Income Group`"),
            ("8. India debt records in 2024", "select `Country Name`, `Series Name`, `Year`, `Value` from debt_data where `Country Code`='IND' and `Year`=2024 limit 20"),
            ("9. Count used indicators", "select count(distinct `Series Code`) as used_indicators from debt_data"),
            ("10. Records per year", "select `Year`, count(*) as total_records from debt_data group by `Year` order by `Year`"),
        ],
        "Intermediate": [
            ("11. Countries and regions", "select `Short Name` as Country, `Region` from countries where `Region` <> 'Unknown' order by Country"),
            ("12. Country external debt", by_country + " order by Debt_USD desc"),
            ("13. Top 10 countries", by_country + " order by Debt_USD desc limit 10"),
            ("14. Lowest 10 positive debt countries", by_country + " and d.`Value`>0 order by Debt_USD limit 10"),
            ("15. Total debt by region", by_region + " order by Debt_USD desc"),
            ("16. Average debt by region", f"select c.`Region`, avg(d.`Value`) as Average_USD {base} group by c.`Region` order by Average_USD desc"),
            ("17. Country count per region", "select `Region`, count(*) as Countries from countries where `Region` <> 'Unknown' group by `Region` order by Countries desc"),
            ("18. India's debt over time", "select `Year`, `Value` as Debt_USD from debt_data where `Country Code`='IND' and `Series Code`='DT.DOD.DECT.CD' order by `Year`"),
            ("19. India's 3 debt indicators", "select `Series Name`, `Value` as Debt_USD from debt_data where `Country Code`='IND' and `Year`=2024 and `Series Code` in ('DT.DOD.DECT.CD','DT.DOD.DLXF.CD','DT.DOD.DSTC.CD')"),
            ("20. Regions above $1 trillion", f"select c.`Region`, sum(d.`Value`) as Debt_USD {base} group by c.`Region` having sum(d.`Value`)>1000000000000 order by Debt_USD desc"),
        ],
        "Advanced": [
            ("21. Country debt ranking", f"select d.`Country Name` as Country, d.`Value` as Debt_USD, rank() over(order by d.`Value` desc) as Debt_Rank {base} order by Debt_Rank"),
            ("22. Debt categories", f"select d.`Country Name` as Country, d.`Value` as Debt_USD, case when d.`Value`>=1000000000000 then 'High' when d.`Value`>=100000000000 then 'Medium' else 'Low' end as Debt_Category {base} order by Debt_USD desc"),
            ("23. Above-average debt countries", f"select * from ({by_country}) t where Debt_USD>(select avg(Debt_USD) from ({by_country}) a) order by Debt_USD desc"),
            ("24. Country debt share", f"select Country, round(100*Debt_USD/nullif(sum(Debt_USD) over(),0),2) as Share_Percent from ({by_country}) t order by Share_Percent desc"),
            ("25. India's previous-year debt", "select `Year`, `Value` as Debt_USD, lag(`Value`) over(order by `Year`) as Previous_Year_USD from debt_data where `Country Code`='IND' and `Series Code`='DT.DOD.DECT.CD' order by `Year`"),
            ("26. India's annual debt change", "with yearly as (select `Year`, `Value`, lag(`Value`) over(order by `Year`) as prev from debt_data where `Country Code`='IND' and `Series Code`='DT.DOD.DECT.CD') select `Year`, (`Value`-prev) as Change_USD from yearly order by `Year`"),
            ("27. Region debt ranking", f"select Region, Debt_USD, dense_rank() over(order by Debt_USD desc) as Region_Rank from ({by_region}) t"),
            ("28. Highest-debt country per region", f"with ranked as (select c.`Region`, d.`Country Name` as Country, d.`Value` as Debt_USD, row_number() over(partition by c.`Region` order by d.`Value` desc) as pos {base}) select `Region`, Country, Debt_USD from ranked where pos=1 order by Debt_USD desc"),
            ("29. Top 3 debt countries per region", f"with ranked as (select c.`Region`, d.`Country Name` as Country, d.`Value` as Debt_USD, dense_rank() over(partition by c.`Region` order by d.`Value` desc) as Debt_Rank {base}) select `Region`, Country, Debt_USD, Debt_Rank from ranked where Debt_Rank<=3 order by `Region`, Debt_Rank"),
            ("30. Countries with >5% debt share", f"with shares as (select Country, round(100*Debt_USD/nullif(sum(Debt_USD) over(),0),2) as Share_Percent from ({by_country}) t) select * from shares where Share_Percent>5 order by Share_Percent desc"),
        ],
    }
    level = st.selectbox("Level", list(questions))
    question = st.selectbox("Question", [title for title, _ in questions[level]])
    sql = dict(questions[level])[question]
    st.code(sql, language="sql")
    if st.button("Run Query"):
        try:
            result = get_data(sql)
            st.write(f"Returned {len(result):,} rows")
            st.dataframe(result, use_container_width=True, hide_index=True)
        except Exception as error:
            st.error("Query failed")
            st.code(str(error))
