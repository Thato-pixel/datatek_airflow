# DataTel Communications Pipeline - Discussion Questions

**Q1: Incremental strategy — what defines new data? What happens to late records?**
To separate already-loaded data from new data, I used the transaction_date column as the boundary. Each run only picks up records where the transaction date falls within the current processing window. If a record arrives two days late, the next pipeline run will catch it because we filter on the actual transaction date, not the time the record physically landed in the database.

**Q2: How do aggregation tables stay correct without full rebuilds?**
Instead of wiping and rebuilding everything from scratch daily, I used an upsert approach. Each run recalculates metrics only for customers who had activity that day, then updates their existing row. This keeps the pipeline fast while still keeping the numbers accurate.

**Q3: stg_customers has no timestamp — how did you handle it?**
Since there is no updated_at column to filter on, I do a full reload of the customers table every day. With only 1,000 customers it is practically instant. Newly registered customers are picked up using a created_at filter within the daily window.

**Q4: BigQuery write pattern — what breaks with a simple overwrite?**
I used a MERGE pattern — new customers get inserted, existing ones get their metrics updated in place. A simple overwrite would delete the entire table on every run, creating a dangerous window where the table is empty if anything fails mid-run.

**Q5: Billing arrives 6 hours late — what happens?**
The pipeline would run on schedule and process whatever has arrived, meaning that days numbers would be incomplete. To fix this I would add a data arrival sensor task that checks record count before allowing downstream tasks to proceed, and alerts the team if expected volume has not arrived within a timeout window.

**Q6: Customer in billing but not in customers table — what happens?**
Their billing record passes through stg_billing normally and revenue is captured in agg_user_revenue. However since dw_user_analytics joins from stg_customers as the base, this customer disappears from the final table. The right fix would be to generate a placeholder customer row so no revenue data gets silently dropped.

**Q7: Churn rule flags new customers — how do you fix it?**
The churn rule will always flag someone who joined yesterday because they have not had time to build up activity. Since dw_user_analytics already includes customer_since, I would add a condition excluding anyone registered within the last 30 days: AND DATEDIFF(CURRENT_DATE, customer_since) > 30.
