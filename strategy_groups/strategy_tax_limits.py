"""
Shared tax year limits for all strategy group files.
All strategy lambdas should call get_lim(s) to get the correct year's limits.
"""

TAX_YEAR_LIMITS = {
    2023: {
        "defined_contribution_limit": 66000,
        "elective_deferral_limit": 22500,
        "hsa_family_limit": 7750,
        "educational_assistance_limit": 5250,
        "qbi_sstb_phaseout_mfj": 364200,
        "llc_phaseout_mfj": 180000,
        "salt_cap": 10000,
        "child_standard_deduction": 13850,
        "sep_contribution_pct": 0.25,
        "catch_up_contribution": 7500,
        "gift_tax_annual_exclusion": 17000,
    },
    2024: {
        "defined_contribution_limit": 69000,
        "elective_deferral_limit": 23000,
        "hsa_family_limit": 8300,
        "educational_assistance_limit": 5250,
        "qbi_sstb_phaseout_mfj": 383900,
        "llc_phaseout_mfj": 180000,
        "salt_cap": 10000,
        "child_standard_deduction": 14600,
        "sep_contribution_pct": 0.25,
        "catch_up_contribution": 7500,
        "gift_tax_annual_exclusion": 18000,
    },
    2025: {
        "defined_contribution_limit": 70000,
        "elective_deferral_limit": 23500,
        "hsa_family_limit": 8550,
        "educational_assistance_limit": 5250,
        "qbi_sstb_phaseout_mfj": 394600,
        "llc_phaseout_mfj": 180000,
        "salt_cap": 10000,
        "child_standard_deduction": 15000,
        "sep_contribution_pct": 0.25,
        "catch_up_contribution": 7500,
        "gift_tax_annual_exclusion": 19000,
    },
}

_DEFAULT_LIM = TAX_YEAR_LIMITS[2024]


def get_lim(signals: dict) -> dict:
    """Return the correct tax year limits from the signals dict.
    
    Usage inside a lambda:
        "fed_savings_fn": lambda s: get_lim(s)["defined_contribution_limit"] * s.get("_fed_marginal_rate", 0)
    """
    year = int(signals.get("_tax_year", 2024))
    return TAX_YEAR_LIMITS.get(year, _DEFAULT_LIM)
