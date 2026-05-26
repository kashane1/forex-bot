"""Read-only cross-asset feature ingestion scaffolding."""

from research.cross_asset_features.alignment import (
    align_features_to_h4_with_availability,
    align_wide_frame_to_h4,
)
from research.cross_asset_features.loader import (
    FEATURE_FILES,
    align_features_to_h4,
    build_availability_report,
    load_feature_csv,
    load_features_from_directory,
    write_availability_report,
)
from research.cross_asset_features.schema import (
    CANONICAL_FEATURE_IDS,
    FEATURE_SCHEMA,
    LEGACY_FEATURE_ALIASES,
    FeatureSeries,
    load_source_registry,
    validate_source_registry,
)

__all__ = [
    "CANONICAL_FEATURE_IDS",
    "FEATURE_FILES",
    "FEATURE_SCHEMA",
    "LEGACY_FEATURE_ALIASES",
    "FeatureSeries",
    "align_features_to_h4",
    "align_features_to_h4_with_availability",
    "align_wide_frame_to_h4",
    "build_availability_report",
    "load_feature_csv",
    "load_features_from_directory",
    "load_source_registry",
    "validate_source_registry",
    "write_availability_report",
]
