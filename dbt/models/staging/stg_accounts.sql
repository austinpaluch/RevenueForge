SELECT 
    account_id,
    company_name,
    industry,
    created_at
FROM {{ source('raw', 'dim_accounts') }}