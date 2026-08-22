"""
Loan Default Risk Analysis
===========================
Business Problem:
A financial institution wants to reduce losses from loan defaults.
This analysis identifies which borrower characteristics are most strongly
associated with default risk, in order to help the credit team improve
loan approval decisions and pricing.

Dataset: Loan_default.csv (255,347 loan records, 18 features)
Author: Ajit Pal
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 120

# ------------------------------------------------------------
# 1. Load and inspect data
# ------------------------------------------------------------
df = pd.read_csv("Loan_default.csv")
print("Shape:", df.shape)
print(df.info())
print("Missing values:\n", df.isnull().sum())

# No missing values in this dataset - it's already clean.
# Basic sanity checks on ranges:
print(df[["Age", "Income", "LoanAmount", "CreditScore", "InterestRate", "DTIRatio"]].describe())

# ------------------------------------------------------------
# 2. Overall default rate
# ------------------------------------------------------------
overall_default_rate = df["Default"].mean() * 100
print(f"Overall default rate: {overall_default_rate:.2f}%")

# ------------------------------------------------------------
# 3. Feature engineering - create readable buckets for analysis
# ------------------------------------------------------------
df["AgeBucket"] = pd.cut(
    df["Age"], bins=[17, 25, 35, 45, 55, 70],
    labels=["18-25", "26-35", "36-45", "46-55", "56+"]
)

df["CreditBucket"] = pd.cut(
    df["CreditScore"], bins=[0, 580, 670, 740, 800, 900],
    labels=["Poor (<580)", "Fair (580-669)", "Good (670-739)",
            "Very Good (740-799)", "Excellent (800+)"]
)

df["IncomeBucket"] = pd.qcut(
    df["Income"], 4, labels=["Low", "Mid-Low", "Mid-High", "High"]
)

df["InterestRateBucket"] = pd.qcut(
    df["InterestRate"], 4, labels=["Low", "Mid-Low", "Mid-High", "High"]
)

df["DTIBucket"] = pd.cut(
    df["DTIRatio"], bins=[0, 0.2, 0.4, 0.6, 1.0],
    labels=["<0.2", "0.2-0.4", "0.4-0.6", "0.6+"]
)

# ------------------------------------------------------------
# 4. Default rate by segment
# ------------------------------------------------------------
segments = {
    "Age Group": "AgeBucket",
    "Credit Score Band": "CreditBucket",
    "Income Quartile": "IncomeBucket",
    "Interest Rate Quartile": "InterestRateBucket",
    "DTI Ratio Band": "DTIBucket",
    "Employment Type": "EmploymentType",
    "Loan Purpose": "LoanPurpose",
    "Education": "Education",
    "Has Co-Signer": "HasCoSigner",
    "Has Dependents": "HasDependents",
}

for label, col in segments.items():
    rate = df.groupby(col, observed=True)["Default"].mean().sort_values(ascending=False) * 100
    print(f"\nDefault rate by {label}:\n{rate.round(2)}")

# ------------------------------------------------------------
# 5. Correlation of numeric features with Default
# ------------------------------------------------------------
num_cols = ["Age", "Income", "LoanAmount", "CreditScore", "MonthsEmployed",
            "NumCreditLines", "InterestRate", "LoanTerm", "DTIRatio", "Default"]
corr = df[num_cols].corr()["Default"].sort_values()
print("\nCorrelation with Default:\n", corr)

# ------------------------------------------------------------
# 6. Visualizations
# ------------------------------------------------------------

# Chart 1: Default rate by Age Group
plt.figure(figsize=(7, 4.5))
age_rate = df.groupby("AgeBucket", observed=True)["Default"].mean() * 100
sns.barplot(x=age_rate.index, y=age_rate.values, color="#1F3864")
plt.title("Default Rate by Age Group")
plt.ylabel("Default Rate (%)")
plt.xlabel("Age Group")
plt.tight_layout()
plt.savefig("charts/chart1_default_rate_by_age.png")
plt.close()

# Chart 2: Default rate by Income Quartile
plt.figure(figsize=(7, 4.5))
income_rate = df.groupby("IncomeBucket", observed=True)["Default"].mean() * 100
sns.barplot(x=income_rate.index, y=income_rate.values, color="#2E75B6")
plt.title("Default Rate by Income Quartile")
plt.ylabel("Default Rate (%)")
plt.xlabel("Income Quartile")
plt.tight_layout()
plt.savefig("charts/chart2_default_rate_by_income.png")
plt.close()

# Chart 3: Default rate by Interest Rate Quartile
plt.figure(figsize=(7, 4.5))
ir_rate = df.groupby("InterestRateBucket", observed=True)["Default"].mean() * 100
sns.barplot(x=ir_rate.index, y=ir_rate.values, color="#C00000")
plt.title("Default Rate by Interest Rate Quartile")
plt.ylabel("Default Rate (%)")
plt.xlabel("Interest Rate Quartile")
plt.tight_layout()
plt.savefig("charts/chart3_default_rate_by_interest_rate.png")
plt.close()

# Chart 4: Default rate by Credit Score Band
plt.figure(figsize=(7, 4.5))
credit_rate = df.groupby("CreditBucket", observed=True)["Default"].mean() * 100
sns.barplot(x=credit_rate.index, y=credit_rate.values, color="#548235")
plt.title("Default Rate by Credit Score Band")
plt.ylabel("Default Rate (%)")
plt.xlabel("Credit Score Band")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig("charts/chart4_default_rate_by_credit_score.png")
plt.close()

# Chart 5: Default rate by Employment Type
plt.figure(figsize=(7, 4.5))
emp_rate = df.groupby("EmploymentType", observed=True)["Default"].mean().sort_values(ascending=False) * 100
sns.barplot(x=emp_rate.index, y=emp_rate.values, color="#7030A0")
plt.title("Default Rate by Employment Type")
plt.ylabel("Default Rate (%)")
plt.xlabel("Employment Type")
plt.tight_layout()
plt.savefig("charts/chart5_default_rate_by_employment.png")
plt.close()

# Chart 6: Correlation heatmap
plt.figure(figsize=(7, 5.5))
sns.heatmap(df[num_cols].corr(), annot=True, fmt=".2f", cmap="coolwarm", center=0)
plt.title("Correlation Heatmap - Numeric Features vs Default")
plt.tight_layout()
plt.savefig("charts/chart6_correlation_heatmap.png")
plt.close()

# Chart 7: Co-signer and dependents impact
plt.figure(figsize=(7, 4.5))
cosign_dep = pd.DataFrame({
    "Has Co-Signer": df.groupby("HasCoSigner")["Default"].mean() * 100,
    "Has Dependents": df.groupby("HasDependents")["Default"].mean() * 100,
})
cosign_dep.plot(kind="bar", ax=plt.gca())
plt.title("Default Rate: Co-Signer vs Dependents")
plt.ylabel("Default Rate (%)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("charts/chart7_cosigner_dependents.png")
plt.close()

print("\nAll charts saved to /charts folder.")

# ------------------------------------------------------------
# 7. Export cleaned + feature-engineered data for SQL / Power BI
# ------------------------------------------------------------
df.to_csv("Loan_default_cleaned.csv", index=False)
print("\nCleaned dataset exported as Loan_default_cleaned.csv")
