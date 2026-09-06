# CarbonSense Research Data

This directory contains the user-supplied research datasets, factor tables, processed train/test splits, and feature mapping artifacts.

The live application does **not** automatically retrain from these files. Its prediction service remains pinned to the frozen deployment artifact and contract. Use `retrain.py` only in a controlled research environment and validate any candidate artifact before deployment.
