import unittest

from scoring import calculate_dass, calculate_trauma, dass_category, determine_review_priority
from survey_config import DASS_ITEMS, TRAUMA_ITEMS


class DassScoringTests(unittest.TestCase):
    def test_zero_answers_are_normal(self):
        result = calculate_dass({item["id"]: 0 for item in DASS_ITEMS})
        self.assertEqual(result["scores"], {"Depression": 0, "Anxiety": 0, "Stress": 0})
        self.assertEqual(result["highest_level"], "Normal")

    def test_all_three_answers_reach_maximum(self):
        result = calculate_dass({item["id"]: 3 for item in DASS_ITEMS})
        self.assertEqual(result["scores"], {"Depression": 42, "Anxiety": 42, "Stress": 42})
        self.assertEqual(result["highest_level"], "Sangat Teruk")

    def test_threshold_boundaries(self):
        self.assertEqual(dass_category("Depression", 9), "Normal")
        self.assertEqual(dass_category("Depression", 10), "Ringan")
        self.assertEqual(dass_category("Anxiety", 19), "Teruk")
        self.assertEqual(dass_category("Anxiety", 20), "Sangat Teruk")
        self.assertEqual(dass_category("Stress", 33), "Teruk")
        self.assertEqual(dass_category("Stress", 34), "Sangat Teruk")

    def test_known_item_mapping(self):
        answers = {item["id"]: 0 for item in DASS_ITEMS}
        for item_id in (3, 5, 10, 13, 16, 17, 21):
            answers[item_id] = 1
        result = calculate_dass(answers)
        self.assertEqual(result["raw"]["Depression"], 7)
        self.assertEqual(result["scores"]["Depression"], 14)
        self.assertEqual(result["levels"]["Depression"], "Sederhana")


class TraumaScoringTests(unittest.TestCase):
    def test_safety_item_any_endorsement_is_urgent(self):
        answers = {item["id"]: None for item in TRAUMA_ITEMS}
        answers["TR01"] = 1
        trauma = calculate_trauma(answers)
        dass = calculate_dass({item["id"]: 0 for item in DASS_ITEMS})
        self.assertTrue(trauma["immediate_safety_flag"])
        self.assertEqual(determine_review_priority(dass, trauma), "Segera")

    def test_positive_is_two_or_more(self):
        answers = {item["id"]: 0 for item in TRAUMA_ITEMS}
        answers["TR05"] = 2
        trauma = calculate_trauma(answers)
        self.assertEqual(trauma["positive_items"], ["TR05"])
        self.assertEqual(trauma["domains_flagged"], ["Akal"])


if __name__ == "__main__":
    unittest.main()

