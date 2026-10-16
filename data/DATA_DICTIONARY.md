# Data dictionary

| Field | Type | Description |
|---|---|---|
| Date | datetime with India timezone | Timestamp for a five-minute observation |
| Open | numeric | Opening price in INR |
| High | numeric | High price in INR |
| Low | numeric | Low price in INR |
| Close | numeric | Closing price in INR |
| Volume | integer-like numeric | Recorded volume |

The cleaned dataset has 1,351 rows and 6 columns. Derived fields are created inside the Streamlit app and are not written back to the cleaned source CSV.
