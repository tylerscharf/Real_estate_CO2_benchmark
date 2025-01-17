# Benchmarking and Forecasting Emissions in the UAE Real Estate Sector

## Executive Summary

### Project Overview and Goals
This project aims to:
1. Analyze macro-level UAE sustainability data—such as national CO₂ emissions, GDP trends, and carbon intensity
2. Forecast a specific real estate developer's greenhouse gas (GHG) emissions across multiple scopes
3. Parse sustainability or ESG reports in the real estate industry to assess how robustly companies are committing to carbon reduction

By combining structured data (e.g., historical emissions, GDP) with unstructured text data (e.g., sustainability reports), we hope to form a comprehensive view of local real estate emissions benchmarks and see if reported commitments match the trajectory suggested by actual data.

### Findings
- **Macro Trends**: The UAE's overall carbon intensity has declined in recent years, suggesting improving efficiency even as GDP grows. However, total CO₂ levels remain high, indicating the need for stronger sector-specific decarbonization.
- **Real Estate Emissions Forecast**: Based on historical Scope 1 and 2 data, the developer's emissions could increase 2–5% annually unless additional measures are introduced—especially in high-growth scenarios.
- **Report Analysis**: Preliminary text parsing showed that many sustainability reports include general or high-level promises, but fewer have detailed numeric targets or net-zero plans.

### Conclusion and Recommendations
- There appears to be some alignment between national-level decarbonization efforts and sector performance, but real estate's direct emissions remain significant.
- A scenario analysis suggests mitigation strategies (e.g., energy efficiency, renewables) are crucial to avoid emissions outpacing the UAE's broader decarbonization goals.
- A deeper look at published ESG statements reveals a gap between broad commitments and explicit net-zero or science-based targets. Further scrutiny or alignment with frameworks (e.g., SBTi) may strengthen credibility.

## Rationale
Real estate is a major component of the UAE economy and can be a sizable source of emissions (construction, operations, etc.). Understanding how this sector's emissions align with national decarbonization is critical for setting realistic net-zero goals. If the industry's forecasts significantly exceed the national intensity improvements, policymakers and stakeholders may need more aggressive strategies to stay on track.

## Research Question
How can we measure and forecast a UAE real estate company's GHG emissions, benchmark them against national carbon intensity trends, and assess the credibility of sustainability commitments published in the sector's ESG reports?

## Data Sources
1. **UAE Macro Emissions Dataset** (Govt. or known stats agency data)
   - Columns: Year, National CO₂ (Mt), GDP, Population, EnergyRequirements, CarbonIntensity

2. **Real Estate Company Emissions** (Internal data, monthly/yearly scope emissions)
   - Columns: Year, Month, Scope1, Scope2, Scope3

3. **Sustainability Reports** (PDFs, textual data)
   - Scraped or manually collected from websites
   - Used for text parsing and classification of commitment statements

## Methodology

### Macro Assessment
- Clean and visualize 10+ years of national emission data
- Calculate correlation with GDP, population, and carbon intensity

### Forecasting
- Time-series modeling (ARIMA, Prophet, SARIMAX) on the developer's historical emissions
- Compare different scenarios (e.g., high growth vs. moderate)

### Text Parsing and Classification
- Extract key statements from ESG or sustainability PDFs
- Classify references into forward-looking vs. retrospective commitments using clustering/keyword extraction or GPT-based analysis

### Benchmarking
Combine forecast results with macro carbon intensity to see if the company's trajectory aligns with the UAE's decarbonization pace.

## Results
- **Macro-Level**: The UAE's decoupling rate (GDP growth vs. emissions) is improving but still not fast enough to meet potential net-zero targets by mid-century.
- **Company Forecast**: By 2025–2027, emissions could rise ~10% (in a moderate scenario) if no further efficiency measures are adopted. Net-zero aspirations would require significantly steeper annual reduction rates than historical patterns.
- **Commitment Analysis**: ESG reports often mention "green building strategies" or "net-zero by 2050," but few contain interim numeric milestones. Some references to partial achievements or expansions of older goals exist, but overall consistency is lacking.

## Next Steps
1. **Policy & Action**: Investigate how policy changes (or clean energy incentives) might reduce real estate sector emissions faster
2. **Refine Text Analysis**: Expand the classification approach to identify more granular sustainability frameworks (e.g., SBTi alignment, TCFD risk disclosures)
3. **Data Gaps**: Improve data coverage for Scope 3 categories across real estate, potentially integrating occupant or construction supply chain footprints
4. **Validation**: Engage with the real estate developer to validate forecast assumptions and align them with official project expansions or retrofits

## Project Structure
### Notebook 1: Macro Data Analysis
[Link to notebook 1](1_UAE_emissions_macro.ipynb)

### Notebook 2: Emissions Forecasting
[Link to notebook 2](2_real_estate_company.ipynb)

### Notebook 3: Text Parsing & Commitments Classification
[Link to notebook 3](3_report_commitments.ipynb)

## Contact and Further Information
- **Name**: [Your Name]
- **Email**: [Email Address]
- **LinkedIn**: [Your LinkedIn URL]

## Potential Shortfalls / Limitations
- **Data Completeness**: Missing or approximate GDP share data for construction/real estate may lead to less precise sector-level estimates
- **Scope 3 Complexity**: Many real estate supply-chain emissions are still not fully tracked
- **Text Classification**: Reliant on consistent ESG report wording; potential misclassification if phrases are vague
- **Assumption Sensitivity**: Forecasts are scenario-based; actual outcomes may vary with policy changes or technology shifts