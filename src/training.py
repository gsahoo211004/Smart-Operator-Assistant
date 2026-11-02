"""Training catalog helpers."""

from __future__ import annotations

from src.data_loader import load_training_bookings, load_training_modules


def get_modules():
    return load_training_modules()


def get_bookings():
    return load_training_bookings()
