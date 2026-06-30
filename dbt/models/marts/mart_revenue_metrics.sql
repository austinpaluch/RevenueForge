WITH monthly AS (
    SELECT 
        DATE_TRUNC('month', start_date) as month,
        SUM(mrr) as total_mrr,
        COUNT(DISTINCT account_id) as active_customers
    FROM {{ ref('stg_subscriptions') }}
    GROUP BY 1
)
SELECT 
    month,
    total_mrr,
    active_customers,
    LAG(total_mrr) OVER (ORDER BY month) as prev_mrr,
    ROUND(
        (total_mrr - LAG(total_mrr) OVER (ORDER BY month)) 
        / NULLIF(LAG(total_mrr) OVER (ORDER BY month), 0) * 100, 2
    ) as mom_growth_pct
FROM monthly
ORDER BY month