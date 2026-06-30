import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

DATA = Path("processed_vulns.csv")
OUT = Path("figures")
OUT.mkdir(exist_ok=True, parents=True)

df = pd.read_csv(DATA)
sns.set_style("darkgrid")

# Class distribution
plt.figure(figsize=(6,4))
df['is_misconfiguration'].value_counts().plot(kind='bar', color=['green','red'])
plt.xticks([0,1], ["Non-Misconfig", "Misconfig"])
plt.title("Class Distribution")
plt.tight_layout()
plt.savefig(OUT/"class_distribution.png")
plt.close()

# Provider vulnerability
prov = pd.crosstab(df['cloud_provider'], df['is_misconfiguration'], normalize='index')
prov.plot(kind='bar', stacked=True, figsize=(6,4))
plt.title("Provider Vulnerability Rate")
plt.tight_layout()
plt.savefig(OUT/"provider_vulnerability.png")
plt.close()

# Correlation heatmap
plt.figure(figsize=(8,5))
sns.heatmap(df.select_dtypes("number").corr(), annot=True, cmap="coolwarm")
plt.title("Correlation Heatmap")
plt.tight_layout()
plt.savefig(OUT/"correlation.png")
plt.close()
