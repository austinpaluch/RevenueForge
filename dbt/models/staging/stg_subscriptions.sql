SELECT 
    account_id,
    subscription_id,
    plan_name,
    COALESCE(monthly_fee, mrr) as mrr,
    start_date,
    end_date,
    status
FROM {{ source('raw', 'fact_subscriptions') }}