-- models/marts/mart_rfm_segmentation.sql

WITH customer_metrics AS (
    SELECT 
        account_id,
        SUM(mrr) as monetary,
        COUNT(*) as frequency,
        MAX(start_date) as last_purchase_date
    FROM {{ ref('stg_subscriptions') }}
    GROUP BY account_id
),

rfm_scores AS (
    SELECT 
        *,
        NTILE(5) OVER (ORDER BY monetary DESC) as monetary_score,
        NTILE(5) OVER (ORDER BY frequency DESC) as frequency_score,
        NTILE(5) OVER (ORDER BY last_purchase_date DESC) as recency_score
    FROM customer_metrics
)

SELECT 
    account_id,
    monetary,
    frequency,
    last_purchase_date,
    monetary_score,
    frequency_score,
    recency_score,
    CASE 
        WHEN recency_score >= 4 AND frequency_score >= 4 AND monetary_score >= 4 THEN 'Champions'
        WHEN recency_score >= 4 AND frequency_score >= 3 THEN 'Loyal Recent'
        WHEN monetary_score >= 4 THEN 'Big Spenders'
        WHEN frequency_score >= 4 THEN 'Frequent Buyers'
        WHEN recency_score >= 4 THEN 'Recent Buyers'
        WHEN recency_score <= 2 AND frequency_score <= 2 THEN 'At Risk'
        ELSE 'Average'
    END as rfm_segment
FROM rfm_scores