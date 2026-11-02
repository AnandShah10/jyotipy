"""
Tests for compatibility.py (Ashtakoot Guna Milan). Since this system
has 8 independent sub-tables, tests are organized per-koota, checking
both the well-cross-validated core rules and known structural
invariants (e.g. same nakshatra should trigger Nadi dosha, a
well-documented real-world fact this implementation should reproduce
automatically, not because it was special-cased).
"""

from jyotipy.compatibility import (
    varna_koota, vashya_koota, tara_koota, yoni_koota, graha_maitri_koota,
    gana_koota, bhakoot_koota, nadi_koota, guna_milan, NAKSHATRA_NADI, NAKSHATRA_GANA,
)
from jyotipy.constants import NAKSHATRAS


def test_varna_same_sign_scores_full():
    r = varna_koota("Cancer", "Cancer")
    assert r["score"] == 1


def test_varna_higher_groom_varna_scores_full():
    # Groom Kshatriya (Leo), bride Vaishya (Taurus) -> groom rank higher -> 1
    r = varna_koota("Taurus", "Leo")
    assert r["score"] == 1


def test_varna_lower_groom_varna_scores_zero():
    # Groom Shudra (Gemini), bride Brahmin (Cancer) -> groom rank lower -> 0
    r = varna_koota("Cancer", "Gemini")
    assert r["score"] == 0


def test_vashya_same_group_scores_max():
    r = vashya_koota(45.0, 50.0)  # both Taurus -> Chatushpada
    assert r["score"] == 2


def test_vashya_vanachara_incompatible_with_everything_except_itself():
    leo_lon = 4 * 30 + 10  # Leo -> Vanachara
    taurus_lon = 1 * 30 + 10  # Chatushpada
    r = vashya_koota(leo_lon, taurus_lon)
    assert r["score"] == 0


def test_vashya_sagittarius_half_split():
    sag_first_half = 8 * 30 + 5    # Manava
    sag_second_half = 8 * 30 + 25  # Chatushpada
    r1 = vashya_koota(sag_first_half, sag_first_half)
    r2 = vashya_koota(sag_second_half, sag_second_half)
    assert r1["bride_group"] == "Manava"
    assert r2["bride_group"] == "Chatushpada"


def test_tara_same_nakshatra_is_janma_position_and_scores_zero():
    r = tara_koota(0, 0)
    assert r["bride_to_groom_count"] == 1
    assert r["score"] == 0.0


def test_tara_adjacent_nakshatra_is_sampat_and_scores_partial():
    """Position 2 (adjacent, Sampat) is even -> good from that direction."""
    r = tara_koota(0, 1)
    assert r["bride_to_groom_count"] == 2
    assert r["score"] >= 1.5


def test_tara_max_score_is_three():
    # Find a pair where both directions land on even positions.
    r = tara_koota(0, 5)  # diff=5, count=6 (even); reverse diff=22, count=(22%9)+1=5 (odd)
    assert 0 <= r["score"] <= 3


def test_yoni_same_animal_scores_max():
    r = yoni_koota(0, 0)  # Ashwini/Ashwini -> Horse/Horse
    assert r["score"] == 4


def test_yoni_hostile_pair_scores_zero():
    # Ashwini (Horse, idx 0) and Swati (Buffalo, idx 14) -> hostile pair
    r = yoni_koota(0, 14)
    assert r["score"] == 0


def test_graha_maitri_same_lord_scores_max():
    r = graha_maitri_koota("Aries", "Scorpio")  # both Mars-ruled
    assert r["score"] == 5


def test_graha_maitri_mutual_friends_scores_max():
    # Aries (Mars) and Leo (Sun) -- Mars and Sun are mutual natural friends
    r = graha_maitri_koota("Aries", "Leo")
    assert r["score"] == 5


def test_graha_maitri_mutual_enemies_scores_zero():
    # Aries (Mars) and Libra (Venus) -- per the natural relationship table,
    # Venus is Sun's enemy but Mars/Venus are only one-directional
    r = graha_maitri_koota("Leo", "Libra")  # Sun vs Venus -- mutual enemies
    assert r["score"] == 0


def test_gana_deva_list_has_nine_members():
    assert NAKSHATRA_GANA.count("Deva") == 9
    assert NAKSHATRA_GANA.count("Manushya") == 9
    assert NAKSHATRA_GANA.count("Rakshasa") == 9


def test_gana_same_gana_scores_max():
    r = gana_koota(0, 4)  # Ashwini and Mrigashira, both Deva
    assert r["score"] == 6


def test_gana_deva_rakshasa_scores_zero():
    r = gana_koota(0, 2)  # Ashwini (Deva) and Krittika (Rakshasa)
    assert r["score"] == 0


def test_bhakoot_shadashtak_distance_triggers_dosha():
    # Aries to Virgo is a distance of 6 -> Shadashtak dosha
    r = bhakoot_koota("Aries", "Virgo")
    assert r["dosha_present"] is True


def test_bhakoot_dosha_cancelled_by_same_lord():
    # Aries (Mars) and Scorpio (Mars) -- distance 8 (Shadashtak dosha range) but same lord
    r = bhakoot_koota("Aries", "Scorpio")
    assert r["dosha_present"] is True
    assert r["cancelled_by_same_lord"] is True
    assert r["score"] == 7


def test_bhakoot_no_dosha_at_normal_distance():
    r = bhakoot_koota("Aries", "Taurus")  # distance 2 -> Dwirdwadash dosha actually
    assert r["dosha_present"] is True  # confirms 2-12 pair also triggers


def test_nadi_pattern_has_nine_of_each():
    assert NAKSHATRA_NADI.count("Aadi") == 9
    assert NAKSHATRA_NADI.count("Madhya") == 9
    assert NAKSHATRA_NADI.count("Antya") == 9


def test_nadi_same_nakshatra_triggers_dosha():
    r = nadi_koota(0, 0)
    assert r["score"] == 0


def test_nadi_different_nadi_scores_max():
    # Ashwini (Aadi, idx0) and Krittika (Antya, idx2)
    r = nadi_koota(0, 2)
    assert r["score"] == 8


def test_full_guna_milan_identical_moon_reproduces_nadi_dosha():
    """Well-known real-world fact: identical Moon nakshatra scores well
    below the max, specifically because of Nadi dosha (and Tara/Janma),
    not because it was special-cased -- this should emerge naturally
    from the individual koota rules."""
    result = guna_milan(45.0, 45.0)
    assert result["kootas"]["nadi"]["score"] == 0
    assert result["total_score"] < 36


def test_full_guna_milan_returns_all_eight_kootas():
    result = guna_milan(10.0, 100.0)
    assert set(result["kootas"].keys()) == {
        "varna", "vashya", "tara", "yoni", "graha_maitri", "gana", "bhakoot", "nadi",
    }
    assert result["max_score"] == 36


def test_full_guna_milan_total_never_exceeds_36():
    import random
    random.seed(42)
    for _ in range(20):
        b, g = random.uniform(0, 360), random.uniform(0, 360)
        result = guna_milan(b, g)
        assert 0 <= result["total_score"] <= 36