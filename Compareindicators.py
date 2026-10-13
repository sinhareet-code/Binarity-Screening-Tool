
import pandas as pd


binaries = pd.read_csv("gaiabinarity_reference_gaia.csv")
singles = pd.read_csv("gaiabinarity_singles_gaia.csv")


indicators = [
    "ruwe",
    "astrometric_excess_noise",
    "astrometric_gof_al",
    "ipd_frac_multi_peak",
    "phot_bp_rp_excess_factor"
]


for indicator in indicators:
    print(f"\nINDICATOR: {indicator}")

    print("Preliminary binaries:")
    print(binaries[indicator].describe())

    print("Likely singles:")
    print(singles[indicator].describe())

import matplotlib.pyplot as plt

summary = []

for indicator in indicators:
    summary.append({
        "Indicator": indicator,
        "Binary median": binaries[indicator].median(),
        "Likely-single median": singles[indicator].median(),
        "Binary valid N": binaries[indicator].count(),
        "Likely-single valid N": singles[indicator].count()
    })

summary_df = pd.DataFrame(summary)

print("\nCOMPARISON SUMMARY:")
print(summary_df.to_string(index=False))

summary_df.to_csv("indicator_comparison.csv", index=False)


for indicator in indicators:
    binary_values = binaries[indicator].dropna()
    single_values = singles[indicator].dropna()

    plt.figure(figsize=(8, 5))

    plt.boxplot(
        [binary_values, single_values],
        tick_labels=["Preliminary binaries", "Likely singles"],
        showfliers=False
    )

    plt.ylabel(indicator)
    plt.title(f"Gaia DR3 comparison: {indicator}")
    plt.tight_layout()
    plt.savefig(f"comparison_{indicator}.png", dpi=200)
    plt.close()

print("\nSaved comparison table and five graphs!")



def screen_stars(data):
    results = data.copy()

    
    results["high_ruwe"] = results["ruwe"] > 1.4
    results["high_noise"] = results["astrometric_excess_noise"] > 0.5
    results["high_gof"] = results["astrometric_gof_al"] > 10
    results["multiple_peaks"] = results["ipd_frac_multi_peak"] > 0

    
    flags = [
        "high_ruwe",
        "high_noise",
        "high_gof",
        "multiple_peaks"
    ]

    results["anomaly_count"] = results[flags].sum(axis=1)

    
    results["candidate"] = results["anomaly_count"] >= 2

    return results



binary_results = screen_stars(binaries)
single_results = screen_stars(singles)

print("\nGAIABINARITY PROTOTYPE RESULTS")

for name, data in [
    ("Preliminary binaries", binary_results),
    ("Likely singles", single_results)
]:
    print(f"\n{name}")
    print(f"Total sources: {len(data)}")
    print(f"Flagged candidates: {data['candidate'].sum()}")
    print(f"Flagged percentage: {data['candidate'].mean() * 100:.2f}%")


binary_results.to_csv("gaiabinarity_binary_screened.csv", index=False)
single_results.to_csv("gaiabinarity_single_screened.csv", index=False)

print("\nCOMPARISON: RUWE ONLY VS COMBINED SCREENING")

for name, data in [
    ("Preliminary binaries", binary_results),
    ("Likely singles", single_results)
]:
    ruwe_only = data["ruwe"] > 1.4
    combined = data["candidate"]

    print(f"\n{name}")
    print(f"RUWE only: {ruwe_only.sum()} stars")
    print(f"Combined method: {combined.sum()} stars")

    
    extra = combined & ~ruwe_only

    print(f"Combined-only flags: {extra.sum()} stars")
