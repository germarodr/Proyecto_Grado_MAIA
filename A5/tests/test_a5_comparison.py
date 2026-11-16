"""Verifica F1 vectorizado y validaciones antes de comparar modelos."""
import sys
from pathlib import Path
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import comparar_modelos as comparison
import a5_runtime as runtime


class ComparisonTests(unittest.TestCase):
    def test_vectorized_macro_matches_reference_including_invalids(self):
        rng = np.random.default_rng(13)
        for _ in range(12):
            matrix = rng.integers(0, 4, size=(9, 10))
            gold, predicted = [], []
            for i in range(9):
                for j in range(10):
                    gold += [runtime.LABELS[i]] * int(matrix[i, j])
                    predicted += [(runtime.LABELS + [runtime.INVALID])[j]] * int(matrix[i, j])
            self.assertAlmostEqual(float(comparison.macro_from_matrices(matrix)),
                runtime.classification_metrics(gold, predicted)["f1_macro"])

    def test_paired_group_counts_match_explicit_resampling(self):
        groups = np.zeros((2, 9, 10))
        groups[0, 0, 0] = 2
        groups[0, 1, 9] = 1
        groups[1, 1, 1] = 3
        weights = np.array([[2, 0], [0, 2], [1, 1]])
        sampled = (weights @ groups.reshape(2, -1)).reshape(3, 9, 10)
        for i, weight in enumerate(weights):
            explicit = sum((groups[k] * weight[k] for k in range(2)), np.zeros((9, 10)))
            self.assertAlmostEqual(float(comparison.macro_from_matrices(sampled[i])),
                                   float(comparison.macro_from_matrices(explicit)))

    def test_changed_reference_or_missing_cases_are_rejected(self):
        baseline = {"case": {"reference": "Background", "citing_paper_id": "paper"}}
        rows = [{"inst_key": "case", "condition": c, "reference": "Gap", "citing_id": "paper",
                 "valid": "True", "predicted_label": "Background"} for c in comparison.CONDITIONS]
        with self.assertRaisesRegex(ValueError, "gold"):
            comparison.check_commercial(rows, baseline)
        with self.assertRaises(ValueError):
            comparison.check_commercial(rows[:-1], baseline)


if __name__ == "__main__":
    unittest.main()
