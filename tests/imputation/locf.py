"""
Test cases for LOCF imputation method.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause


import unittest

import numpy as np
import pytest
import torch

from pypots.imputation import LOCF
from pypots.utils.logging import logger
from pypots.utils.metrics import calc_mae
from tests.global_test_config import (
    DATA,
    DEVICE,
    TEST_SET,
    H5_TRAIN_SET_PATH,
    H5_VAL_SET_PATH,
    H5_TEST_SET_PATH,
)


class TestLOCF(unittest.TestCase):
    logger.info("Running tests for an imputation model LOCF...")
    locf_zero = LOCF(first_step_imputation="zero", device=DEVICE)
    locf_backward = LOCF(first_step_imputation="backward", device=DEVICE)
    locf_mean = LOCF(first_step_imputation="mean", device=DEVICE)
    locf_nan = LOCF(first_step_imputation="nan", device=DEVICE)

    @pytest.mark.xdist_group(name="imputation-locf")
    def test_0_impute(self):
        # if input data is numpy ndarray
        test_X_imputed_zero = self.locf_zero.predict(TEST_SET)["imputation"]
        assert not np.isnan(
            test_X_imputed_zero
        ).any(), "Output still has missing values after running impute()."
        test_MAE = calc_mae(
            test_X_imputed_zero, DATA["test_X_ori"], DATA["test_X_indicating_mask"]
        )
        logger.info(f"LOCF (zero) test_MAE: {test_MAE}")

        test_X_imputed_backward = self.locf_backward.predict(TEST_SET)["imputation"]
        assert not np.isnan(
            test_X_imputed_backward
        ).any(), "Output still has missing values after running impute()."
        test_MAE = calc_mae(
            test_X_imputed_backward,
            DATA["test_X_ori"],
            DATA["test_X_indicating_mask"],
        )
        logger.info(f"LOCF (backward) test_MAE: {test_MAE}")

        test_X_imputed_mean = self.locf_mean.predict(TEST_SET)["imputation"]
        assert not np.isnan(
            test_X_imputed_mean
        ).any(), "Output still has missing values after running impute()."
        test_MAE = calc_mae(
            test_X_imputed_mean,
            DATA["test_X_ori"],
            DATA["test_X_indicating_mask"],
        )
        logger.info(f"LOCF (mean) test_MAE: {test_MAE}")

        test_X_imputed_nan = self.locf_nan.predict(TEST_SET)["imputation"]
        num_of_missing = np.isnan(test_X_imputed_nan).sum()
        assert num_of_missing > 0, "Output should have missing data but not."
        logger.info(f"LOCF (nan) still have {num_of_missing} missing values.")

        # if input data is torch tensor
        X = torch.from_numpy(np.copy(TEST_SET["X"]))
        test_X_ori = torch.from_numpy(np.copy(DATA["test_X_ori"]))
        test_X_indicating_mask = torch.from_numpy(
            np.copy(DATA["test_X_indicating_mask"])
        )

        test_X_imputed_zero = self.locf_zero.predict({"X": X})["imputation"]
        assert not torch.isnan(
            test_X_imputed_zero
        ).any(), "Output still has missing values after running impute()."
        test_MAE = calc_mae(test_X_imputed_zero, test_X_ori, test_X_indicating_mask)
        logger.info(f"LOCF (zero) test_MAE: {test_MAE}")

        test_X_imputed_backward = self.locf_backward.predict({"X": X})["imputation"]
        assert not torch.isnan(
            test_X_imputed_backward
        ).any(), "Output still has missing values after running impute()."
        test_MAE = calc_mae(
            test_X_imputed_backward,
            test_X_ori,
            test_X_indicating_mask,
        )
        logger.info(f"LOCF (backward) test_MAE: {test_MAE}")

        test_X_imputed_mean = self.locf_mean.predict({"X": X})["imputation"]
        assert not torch.isnan(
            test_X_imputed_mean
        ).any(), "Output still has missing values after running impute()."
        test_MAE = calc_mae(
            test_X_imputed_mean,
            test_X_ori,
            test_X_indicating_mask,
        )
        logger.info(f"LOCF (mean) test_MAE: {test_MAE}")

        test_X_imputed_nan = self.locf_nan.predict({"X": X})["imputation"]
        num_of_missing = torch.isnan(test_X_imputed_nan).sum()
        assert num_of_missing > 0, "Output should have missing data but not."
        logger.info(f"LOCF (nan) still have {num_of_missing} missing values.")

    @pytest.mark.xdist_group(name="imputation-locf")
    def test_4_lazy_loading(self):
        self.locf_backward.fit(H5_TRAIN_SET_PATH, H5_VAL_SET_PATH)
        imputation_results = self.locf_backward.predict(H5_TEST_SET_PATH)
        assert not np.isnan(
            imputation_results["imputation"]
        ).any(), "Output still has missing values after running impute()."

        test_MAE = calc_mae(
            imputation_results["imputation"],
            DATA["test_X_ori"],
            DATA["test_X_indicating_mask"],
        )
        logger.info(f"Lazy-loading LOCF test_MAE: {test_MAE}")


if __name__ == "__main__":
    unittest.main()
