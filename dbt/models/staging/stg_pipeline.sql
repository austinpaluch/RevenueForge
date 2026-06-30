SELECT 
    opportunity_id,
    account_id,
    stage,
    amount,
    created_date,
    close_date,
    is_closed_won
FROM {{ source('raw', 'fact_pipeline') }}