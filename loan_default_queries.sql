/* ============================================================
   LOAN DEFAULT RISK ANALYSIS - SQL QUERIES
   Table: loans (load Loan_default.csv into this table)
   Tool: SQLite / MySQL / PostgreSQL compatible (minor tweaks noted)
   ============================================================ */

-- Recommended schema
CREATE TABLE loans (
    loan_id           TEXT PRIMARY KEY,
    age               INTEGER,
    income            INTEGER,
    loan_amount       INTEGER,
    credit_score      INTEGER,
    months_employed   INTEGER,
    num_credit_lines  INTEGER,
    interest_rate     NUMERIC(5,2),
    loan_term         INTEGER,
    dti_ratio         NUMERIC(5,2),
    education         TEXT,
    employment_type   TEXT,
    marital_status    TEXT,
    has_mortgage      TEXT,
    has_dependents    TEXT,
    loan_purpose      TEXT,
    has_cosigner      TEXT,
    default_flag      INTEGER   -- 1 = defaulted, 0 = paid
);

/* ------------------------------------------------------------
   Q1. Overall portfolio default rate
   Business use: baseline risk level of the entire loan book
------------------------------------------------------------ */
SELECT
    COUNT(*) AS total_loans,
    SUM(default_flag) AS total_defaults,
    ROUND(100.0 * SUM(default_flag) / COUNT(*), 2) AS default_rate_pct
FROM loans;

/* ------------------------------------------------------------
   Q2. Default rate by credit score band
   Business use: informs credit-score-based approval thresholds
------------------------------------------------------------ */
SELECT
    CASE
        WHEN credit_score < 580 THEN 'Poor (<580)'
        WHEN credit_score < 670 THEN 'Fair (580-669)'
        WHEN credit_score < 740 THEN 'Good (670-739)'
        WHEN credit_score < 800 THEN 'Very Good (740-799)'
        ELSE 'Excellent (800+)'
    END AS credit_band,
    COUNT(*) AS total_loans,
    ROUND(100.0 * SUM(default_flag) / COUNT(*), 2) AS default_rate_pct
FROM loans
GROUP BY credit_band
ORDER BY default_rate_pct DESC;

/* ------------------------------------------------------------
   Q3. Default rate by income quartile
   Business use: highest-risk segment identification
------------------------------------------------------------ */
SELECT
    NTILE(4) OVER (ORDER BY income) AS income_quartile,
    COUNT(*) AS total_loans,
    ROUND(AVG(income), 0) AS avg_income,
    ROUND(100.0 * SUM(default_flag) / COUNT(*), 2) AS default_rate_pct
FROM loans
GROUP BY income_quartile
ORDER BY income_quartile;

/* ------------------------------------------------------------
   Q4. Top 5 riskiest loan purposes by default rate
------------------------------------------------------------ */
SELECT
    loan_purpose,
    COUNT(*) AS total_loans,
    ROUND(100.0 * SUM(default_flag) / COUNT(*), 2) AS default_rate_pct,
    ROUND(AVG(loan_amount), 0) AS avg_loan_amount
FROM loans
GROUP BY loan_purpose
ORDER BY default_rate_pct DESC
LIMIT 5;

/* ------------------------------------------------------------
   Q5. Average loan amount: defaulters vs non-defaulters
------------------------------------------------------------ */
SELECT
    CASE WHEN default_flag = 1 THEN 'Defaulted' ELSE 'Repaid' END AS loan_status,
    COUNT(*) AS total_loans,
    ROUND(AVG(loan_amount), 0) AS avg_loan_amount,
    ROUND(AVG(interest_rate), 2) AS avg_interest_rate,
    ROUND(AVG(dti_ratio), 2) AS avg_dti_ratio
FROM loans
GROUP BY loan_status;

/* ------------------------------------------------------------
   Q6. Default rate by employment type
------------------------------------------------------------ */
SELECT
    employment_type,
    COUNT(*) AS total_loans,
    ROUND(100.0 * SUM(default_flag) / COUNT(*), 2) AS default_rate_pct
FROM loans
GROUP BY employment_type
ORDER BY default_rate_pct DESC;

/* ------------------------------------------------------------
   Q7. Impact of having a co-signer or dependents on default rate
------------------------------------------------------------ */
SELECT
    has_cosigner,
    has_dependents,
    COUNT(*) AS total_loans,
    ROUND(100.0 * SUM(default_flag) / COUNT(*), 2) AS default_rate_pct
FROM loans
GROUP BY has_cosigner, has_dependents
ORDER BY default_rate_pct DESC;

/* ------------------------------------------------------------
   Q8. Interest rate quartile vs default rate
   Business use: check if current risk-based pricing is well calibrated
------------------------------------------------------------ */
SELECT
    NTILE(4) OVER (ORDER BY interest_rate) AS interest_rate_quartile,
    ROUND(MIN(interest_rate), 2) AS min_rate,
    ROUND(MAX(interest_rate), 2) AS max_rate,
    COUNT(*) AS total_loans,
    ROUND(100.0 * SUM(default_flag) / COUNT(*), 2) AS default_rate_pct
FROM loans
GROUP BY interest_rate_quartile
ORDER BY interest_rate_quartile;

/* ------------------------------------------------------------
   Q9. Rank loan purposes by default rate within each employment type
   (window function - shows SQL depth)
------------------------------------------------------------ */
SELECT *
FROM (
    SELECT
        employment_type,
        loan_purpose,
        COUNT(*) AS total_loans,
        ROUND(100.0 * SUM(default_flag) / COUNT(*), 2) AS default_rate_pct,
        RANK() OVER (
            PARTITION BY employment_type
            ORDER BY 100.0 * SUM(default_flag) / COUNT(*) DESC
        ) AS risk_rank
    FROM loans
    GROUP BY employment_type, loan_purpose
) ranked
WHERE risk_rank <= 2
ORDER BY employment_type, risk_rank;

/* ------------------------------------------------------------
   Q10. Estimated dollar exposure at risk by age group
   Business use: quantify potential loss, not just count of loans
------------------------------------------------------------ */
SELECT
    CASE
        WHEN age <= 25 THEN '18-25'
        WHEN age <= 35 THEN '26-35'
        WHEN age <= 45 THEN '36-45'
        WHEN age <= 55 THEN '46-55'
        ELSE '56+'
    END AS age_group,
    COUNT(*) AS total_loans,
    ROUND(100.0 * SUM(default_flag) / COUNT(*), 2) AS default_rate_pct,
    SUM(CASE WHEN default_flag = 1 THEN loan_amount ELSE 0 END) AS total_loss_exposure
FROM loans
GROUP BY age_group
ORDER BY default_rate_pct DESC;
