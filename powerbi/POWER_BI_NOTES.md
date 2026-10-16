# Power BI report notes

Open `HDFCBANK_Stock_Analytics_Dashboard.pbix` in Power BI Desktop.

- The report is based on the uploaded HDFCBANK five-minute dataset.
- Main fields: Date, Open, High, Low, Close, Volume, and SessionDate.
- The report includes KPI cards, closing price trend, high-vs-low chart, return chart, daily high-low range, volume chart, and a date slicer.
- If you move the project folder and Power BI requests the source file, reconnect it to `../data/HDFCBANK_Stock_Data.csv` (or the equivalent absolute path on your computer) and refresh.
- Check visual aggregations after refresh: prices should use suitable aggregations (Average for a time-series line, Maximum High and Minimum Low for session ranges, Sum for volume).
- `Latest Close` may be defined to ignore date slicer filters if it uses `ALL()` in DAX. That is intentional only if you want the latest value in the full dataset rather than the selected period.
