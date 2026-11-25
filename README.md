# PLP Data Analysis Assignment 3 — Duka Sales and Agent Cleanup

## Project overview
This repository contains two data-analysis engagements: (1) exploration of Duka Electronics sales and (2) cleaning and validation of an agent-network transaction dataset.

## Dataset-generation note
`generate_data.py` contains the Duka Electronics generator exactly as supplied. The original agent-network practical generator could not be located, so its section is a **reconstruction** based on the assignment specifications (seed 44, 20 agents, 600 transactions and the listed injected issues). Its output is deterministic for this implementation but may not match the original practical's exact row values.

## Duka Executive Summary
Duka Electronics generated **KES 71,792,500.00 in revenue** from **1,000 orders**. Customers purchased **3,012 units**, giving an average revenue of **KES 71,792.50 per order**. **Nairobi** was the highest-revenue branch, contributing **KES 26,106,100.00**. The **In-store** channel generated the most revenue at **KES 40,969,200.00**. The top revenue-generating product was **Laptop**, with **KES 41,535,000.00** in sales.

## Agent data row counts
- Agent master: **20** rows.
- Agent transactions before cleaning: **612** rows (600 base rows plus 12 appended duplicates).
- Transactions after cleaning: **600** rows.
- Transactions with unknown agent IDs retained and labelled `Unknown`: **8**.

## Repository structure
- `generate_data.py` — generates the two source datasets.
- `duka_sales_exploration.ipynb` — inspection, derived fields and Tasks 3–7.
- `agent_cleanup.ipynb` — cleaning, audit, validation, county summary and data-quality report.
- `cleaning_pipeline.py` — reusable `clean_agent_data(txns, agents)` function.
- `build_project.py` — rebuilds generated outputs, workbook and executed notebooks.
- `excel/duka_branch_summary.xlsx` — SUMIFS branch revenue, XLOOKUP region and branch/channel pivot-style summary.
- `outputs/premium_online_coast_capital.csv` — Premium, Online orders from Nairobi and Mombasa.
- `outputs/agent_transactions_clean.csv` — cleaned transaction output.

## Regenerate the data and outputs
Install requirements, then run from the repository root:

```bash
pip install -r requirements.txt
python generate_data.py
python build_project.py
```

Open either notebook and choose **Restart Kernel and Run All**. The notebooks use relative paths from the repository root.

## Excel workbook note
The workbook contains a formula-driven branch summary (`SUMIFS` and `XLOOKUP`) and a pre-aggregated branch-by-channel revenue pivot-style table with grand totals. It is a calculated summary table, not an embedded native Excel PivotTable object; use Excel's Insert → PivotTable on the `Sales Data` table if your assessor specifically requires a native PivotTable object.

## Reconciliation
Notebook revenue is calculated as `quantity × unit_price`. The branch summary and branch/channel aggregation use the same `revenue` measure and should reconcile to the total above.
