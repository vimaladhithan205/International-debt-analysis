import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector

st.set_page_config(page_title="International Debt Analysis", layout="wide")

@st.cache_data(ttl=300)
def read_sql(query, params=None):
    conn = mysql.connector.connect(
        host=st.secrets.get("mysql_host", "localhost"),
        user=st.secrets.get("mysql_user", "root"),
        password=st.secrets["mysql_password"],
        database="international_debt_final",
    )
    try:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(query, params or ())
            return pd.DataFrame(cur.fetchall(), columns=cur.column_names)
        finally:
            cur.close()
    finally:
        conn.close()

INDICATORS = {
    "Total external debt": "DT.DOD.DECT.CD",
    "Long-term debt": "DT.DOD.DLXF.CD",
    "Short-term debt": "DT.DOD.DSTC.CD",
}

COUNTRY_ONLY = "c.`Region` <> 'Unknown'"

st.sidebar.title("International Debt")
page = st.sidebar.radio("Choose a page", ["Dashboard", "SQL Queries"])

try:
    read_sql("select 1 as test")
except Exception as error:
    st.error("Database connection failed. Check MySQL and your password.")
    st.code(str(error))
    st.stop()


if page == "Dashboard":
    st.title("International Debt Analysis")
    years_df = read_sql("select distinct `Year` from debt_data order by `Year` desc")
    country_df = read_sql("select `Code`, `Short Name` from countries where `Region` <> 'Unknown' order by `Short Name`")
    region_df = read_sql("select distinct `Region` from countries where `Region` <> 'Unknown' order by `Region`")
    if years_df.empty:
        st.error("No debt records found in international_debt_final.")
        st.stop()

    country_choices = {r["Short Name"]: r["Code"] for _, r in country_df.iterrows()}
    a, b, c, d = st.columns(4)
    with a:
        year = st.selectbox("Year", years_df["Year"].tolist())
    with b:
        country = st.selectbox("Country", ["All countries"] + list(country_choices))
    with c:
        region = st.selectbox("Region", ["All regions"] + region_df["Region"].tolist())
    with d:
        indicator = st.selectbox("Debt indicator", list(INDICATORS))

    conditions = [COUNTRY_ONLY, "d.`Year` = %(year)s", "d.`Series Code` = %(code)s"]
    params = {"year": int(year), "code": INDICATORS[indicator]}
    if country != "All countries":
        conditions.append("d.`Country Code` = %(country)s")
        params["country"] = country_choices[country]
    if region != "All regions":
        conditions.append("c.`Region` = %(region)s")
        params["region"] = region

    data = read_sql(f"""
        select d.`Country Name` as Country, d.`Year` as Year,
               d.`Value` / 1000000000 as Debt_Billion,
               c.`Region` as Region
        from debt_data d
        join countries c on d.`Country Code` = c.`Code`
        where {' and '.join(conditions)}
    """, params)

    selected = data.dropna(subset=["Debt_Billion"])
    selected_total = selected["Debt_Billion"].sum()
    available_countries = selected["Country"].nunique()
    selection_label = f"{country} | {region} | {year} | {indicator}"
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Countries with data", f"{available_countries:,}")
    k2.metric("Selected debt (US$ bn)", f"{selected_total:,.2f}")
    k3.metric("Selected year", str(year))
    k4.metric("Debt type", indicator)

    if data.empty or data["Debt_Billion"].notna().sum() == 0:
        st.warning("No reported/available values for these filters. Try another year or indicator.")
        st.stop()

    country_debt = data.dropna(subset=["Debt_Billion"]).groupby("Country", as_index=False)["Debt_Billion"].sum()
    highest = country_debt.nlargest(10, "Debt_Billion")
    lowest = country_debt[country_debt["Debt_Billion"] > 0].nsmallest(10, "Debt_Billion")

    st.subheader("Country Debt Ranking")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.bar(highest.sort_values("Debt_Billion"), x="Debt_Billion", y="Country",
                               orientation="h", title="Highest values (US$ billion)"), use_container_width=True)
    with right:
        st.plotly_chart(px.bar(lowest.sort_values("Debt_Billion", ascending=False), x="Debt_Billion", y="Country",
                               orientation="h", title="Lowest positive values (US$ billion)"), use_container_width=True)

    trend_conditions = [COUNTRY_ONLY, "d.`Series Code` = %(code)s"]
    trend_params = {"code": INDICATORS[indicator]}
    if country != "All countries":
        trend_conditions.append("d.`Country Code` = %(country)s")
        trend_params["country"] = country_choices[country]
    if region != "All regions":
        trend_conditions.append("c.`Region` = %(region)s")
        trend_params["region"] = region
    trend = read_sql(f"""
        select d.`Year` as Year, sum(d.`Value`) / 1000000000 as Debt_Billion
        from debt_data d join countries c on d.`Country Code` = c.`Code`
        where {' and '.join(trend_conditions)} and d.`Value` is not null
        group by d.`Year` order by d.`Year`
    """, trend_params)

    st.subheader("Debt Trend and Region")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.line(trend, x="Year", y="Debt_Billion", markers=True,
                                title="Debt stock over time (US$ billion)"), use_container_width=True)
    with right:
        region_data = data.dropna(subset=["Debt_Billion"]).groupby("Region", as_index=False)["Debt_Billion"].sum()
        region_data = region_data[region_data["Debt_Billion"] > 0]
        if len(region_data) > 1:
            st.plotly_chart(px.pie(region_data, names="Region", values="Debt_Billion",
                                    hole=0.3, title="Regional share of selected debt stock"), use_container_width=True)
        else:
            st.info("Select All regions and All countries to compare regional shares.")

    st.subheader("Debt Types")
    compare_conditions = [COUNTRY_ONLY, "d.`Year` = %(year)s",
                          "d.`Series Code` in ('DT.DOD.DECT.CD', 'DT.DOD.DLXF.CD', 'DT.DOD.DSTC.CD')"]
    compare_params = {"year": int(year)}
    if country != "All countries":
        compare_conditions.append("d.`Country Code` = %(country)s")
        compare_params["country"] = country_choices[country]
    if region != "All regions":
        compare_conditions.append("c.`Region` = %(region)s")
        compare_params["region"] = region
    compare = read_sql(f"""
        select d.`Series Code` as Code, sum(d.`Value`) / 1000000000 as Debt_Billion
        from debt_data d join countries c on d.`Country Code` = c.`Code`
        where {' and '.join(compare_conditions)}
        group by d.`Series Code`
    """, compare_params)
    compare["Indicator"] = compare["Code"].map({v: k for k, v in INDICATORS.items()}) if not compare.empty else []
    compare = compare.dropna(subset=["Debt_Billion"])
    if not compare.empty:
        st.plotly_chart(px.bar(compare, x="Indicator", y="Debt_Billion",
                                title="External debt stocks (US$ billion)"), use_container_width=True)
    else:
        st.info("No maturity-comparison values are available for these filters.")
    st.caption("Note: Total external debt includes long-term and short-term debt. Do not add these bars together.")

    st.subheader("Key Insights")

    valid = country_debt.copy()
    positive = valid[valid["Debt_Billion"] > 0]
    scope_total = valid["Debt_Billion"].sum()
    scope_name = country if country != "All countries" else (
        region if region != "All regions" else "all individual countries"
    )

    st.markdown(f"**Selected view:** {indicator}, {year}, {scope_name}.")
    st.write(
        f"**Coverage:** {len(valid)} country/countries have available values in this selection. "
        "Missing observations are not counted as zero."
    )

    if len(valid) == 1:
        row = valid.iloc[0]
        st.write(
            f"**Country insight:** {row['Country']} has "
            f"US$ {row['Debt_Billion']:,.2f} billion in {indicator.lower()} for {year}."
        )
    elif len(valid) > 1:
        highest_row = valid.loc[valid["Debt_Billion"].idxmax()]
        st.write(
            f"**Highest debt in this selection:** {highest_row['Country']} "
            f"(US$ {highest_row['Debt_Billion']:,.2f} billion)."
        )
        if not positive.empty:
            lowest_row = positive.loc[positive["Debt_Billion"].idxmin()]
            st.write(
                f"**Lowest positive debt:** {lowest_row['Country']} "
                f"(US$ {lowest_row['Debt_Billion']:,.2f} billion)."
            )
        if scope_total > 0:
            top_count = min(3, len(valid))
            share = valid.nlargest(top_count, "Debt_Billion")["Debt_Billion"].sum() / scope_total * 100
            st.write(
                f"**Concentration:** The top {top_count} countries hold "
                f"{share:.1f}% of the selected countries' combined debt."
            )

   
    clean_trend = trend.dropna(subset=["Debt_Billion"]).sort_values("Year")
    history = clean_trend[clean_trend["Year"] <= int(year)]
    current_match = history[history["Year"] == int(year)]
    prior = history[history["Year"] < int(year)]
    if not current_match.empty and not prior.empty:
        current_value = float(current_match.iloc[-1]["Debt_Billion"])
        previous = prior.iloc[-1]
        previous_value = float(previous["Debt_Billion"])
        change = current_value - previous_value
        prev_year = int(previous["Year"])
        if prev_year == int(year) - 1:
            period = f"{prev_year} to {year}"
        else:
            period = f"{prev_year} to {year} (not consecutive years)"
        movement = "increased" if change > 0 else "decreased" if change < 0 else "was unchanged"
        if previous_value != 0:
            change_pct = change / abs(previous_value) * 100
            st.write(
                f"**Change over time:** The selected debt {movement} by "
                f"US$ {abs(change):,.2f} billion ({abs(change_pct):.1f}%) from {period}."
            )
        else:
            st.write(
                f"**Change over time:** The selected debt {movement} by "
                f"US$ {abs(change):,.2f} billion from {period}. "
                "A percentage cannot be calculated from a zero starting value."
            )
    else:
        st.info("No earlier available year was found for this selection, so a year comparison is not shown.")

    if country == "All countries" and region == "All regions" and len(region_data) > 1:
        lead = region_data.loc[region_data["Debt_Billion"].idxmax()]
        total_regions = region_data["Debt_Billion"].sum()
        if total_regions > 0:
            st.write(
                f"**Regional insight:** {lead['Region']} accounts for "
                f"{lead['Debt_Billion'] / total_regions * 100:.1f}% "
                "of the selected debt across the included regions."
            )
    elif region != "All regions":
        st.write(f"**Regional filter:** Results are restricted to {region}.")
    elif country != "All countries":
        st.write("**Regional comparison:** Choose All countries and All regions to compare regions.")

    if not compare.empty:
        component_values = dict(zip(compare["Code"], compare["Debt_Billion"]))
        long_term = component_values.get("DT.DOD.DLXF.CD")
        short_term = component_values.get("DT.DOD.DSTC.CD")
        if (
            long_term is not None and short_term is not None
            and pd.notna(long_term) and pd.notna(short_term)
            and long_term >= 0 and short_term >= 0 and long_term + short_term > 0
        ):
            long_share = long_term / (long_term + short_term) * 100
            st.write(
                f"**Maturity insight:** Long-term debt makes up {long_share:.1f}% "
                "of the long-term plus short-term values in this selection."
            )

    st.subheader("Filtered Data")
    st.dataframe(data.head(100), use_container_width=True, hide_index=True)
    st.download_button("Download filtered CSV", data.to_csv(index=False), "debt_data.csv", "text/csv")

elif page == "SQL Queries":
    st.title("SQL Queries")
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
    if st.button("Run query"):
        try:
            result = read_sql(sql)
            st.write(f"Returned {len(result):,} rows")
            st.dataframe(result, use_container_width=True, hide_index=True)
            st.download_button("Download result CSV", result.to_csv(index=False), "sql_result.csv", "text/csv")
        except mysql.connector.Error as exc:
            st.error(f"MySQL query failed: {exc}")