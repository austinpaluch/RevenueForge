WITH closed_deals AS (
    SELECT *
    FROM {{ ref('stg_pipeline') }}
    WHERE stage IN ('Closed Won', 'Closed Lost')
),

stage_metrics AS (
    SELECT 
        stage,
        COUNT(*) as opportunity_count,
        SUM(amount) as total_pipeline_value,
        AVG(amount) as avg_deal_size,
        SUM(CASE WHEN is_closed_won THEN amount ELSE 0 END) as won_value,
        COUNT(CASE WHEN is_closed_won THEN 1 END) as won_count,
        COUNT(CASE WHEN stage = 'Closed Lost' THEN 1 END) as lost_count
    FROM {{ ref('stg_pipeline') }}
    GROUP BY stage
)

SELECT 
    stage,
    opportunity_count,
    total_pipeline_value,
    ROUND(avg_deal_size, 0) as avg_deal_size,
    CASE 
        WHEN stage IN ('Closed Won', 'Closed Lost') THEN 
            ROUND(100.0 * won_count / NULLIF(won_count + lost_count, 0), 1)
        ELSE NULL 
    END as win_rate_pct
FROM stage_metrics
ORDER BY 
    CASE stage 
        WHEN 'Prospecting' THEN 1 
        WHEN 'Qualification' THEN 2 
        WHEN 'Proposal' THEN 3 
        WHEN 'Negotiation' THEN 4 
        WHEN 'Closed Won' THEN 5 
        WHEN 'Closed Lost' THEN 6 
    END