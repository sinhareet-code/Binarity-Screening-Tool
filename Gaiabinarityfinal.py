
import pandas as pd
from astroquery.gaia import Gaia



query = """
SELECT TOP 500
    source_id,
    ruwe,
    bp_rp,
    parallax,
    parallax_over_error,
    phot_g_mean_mag,
    astrometric_excess_noise,
    astrometric_gof_al,
    ipd_frac_multi_peak,
    phot_bp_rp_excess_factor

FROM gaiadr3.gaia_source

WHERE bp_rp BETWEEN 1.5 AND 4.5
AND parallax > 5
AND parallax_over_error > 10
AND phot_g_mean_mag < 19
AND phot_g_mean_mag + 5 * LOG10(parallax) - 10
    BETWEEN 8 AND 17
"""

print("Downloading a new Gaia M-dwarf candidate sample...")

job = Gaia.launch_job_async(query)
stars = job.get_results().to_pandas()

print(f"Retrieved {len(stars)} stars")


reference_files = [
    "gaiabinarity_reference_gaia.csv",
    "gaiabinarity_singles_gaia.csv"
]

used_ids = set()

for filename in reference_files:
    reference = pd.read_csv(filename)
    used_ids.update(reference["source_id"].astype(str))

stars = stars[
    ~stars["source_id"].astype(str).isin(used_ids)
].copy()

print(f"New stars remaining: {len(stars)}")



stars["ruwe_flag"] = stars["ruwe"] > 1.4
stars["noise_flag"] = stars["astrometric_excess_noise"] > 1
stars["gof_flag"] = stars["astrometric_gof_al"] > 3
stars["ipd_flag"] = stars["ipd_frac_multi_peak"] > 0


flag_columns = [
    "ruwe_flag",
    "noise_flag",
    "gof_flag",
    "ipd_flag"
]

stars["anomaly_count"] = stars[flag_columns].sum(axis=1)


stars["candidate"] = stars["anomaly_count"] >= 2


stars.to_csv(
    "gaiabinarity_new_sample_screened.csv",
    index=False
)

candidates = stars[stars["candidate"]].copy()

candidates.to_csv(
    "gaiabinarity_new_candidates.csv",
    index=False
)


print("\nGAIABINARITY NEW SAMPLE RESULTS")
print(f"Total new stars: {len(stars)}")
print(f"Flagged candidates: {len(candidates)}")

if len(stars) > 0:
    percentage = len(candidates) / len(stars) * 100
    print(f"Flagged percentage: {percentage:.2f}%")

print("\nFirst 10 flagged candidates:")

print(
    candidates[
        ["source_id", "ruwe", "anomaly_count"]
    ].head(10).to_string(index=False)
)

print("\nCandidate CSV files saved successfully!")
