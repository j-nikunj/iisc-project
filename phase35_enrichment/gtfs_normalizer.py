from pathlib import Path
from typing import Dict, List, Any
import re

import pandas as pd


class GTFSNormalizer:
    def __init__(
        self,
        loaded_data: Dict[str, pd.DataFrame],
        ontology_config: dict
    ):
        self.loaded_data = loaded_data
        self.ontology_config = ontology_config

        self.normalized_entities: Dict[str, List[dict]] = {
            "transit_stop": [],
            "transit_route": [],
            "transit_trip_pattern": [],
            "stop_time_event": []
        }

    @staticmethod
    def clean_string(value: Any) -> str:
        if pd.isna(value):
            return ""

        value = str(value).strip()

        value = re.sub(r"\s+", " ", value)

        return value

    @staticmethod
    def normalize_identifier(value: Any) -> str:
        if pd.isna(value):
            return ""

        return str(value).strip().lower()

    @staticmethod
    def safe_float(value: Any):
        try:
            return float(value)
        except Exception:
            return None

    def normalize_stops(self):
        print("\nNormalizing transit stops...\n")

        df = self.loaded_data.get("stops.txt")

        if df is None:
            print("[WARNING] stops.txt not loaded.")
            return

        for _, row in df.iterrows():
            stop_entity = {
                "node_class": "transit_stop",
                "id": self.normalize_identifier(row.get("stop_id")),
                "name": self.clean_string(row.get("stop_name")),
                "description": self.clean_string(row.get("stop_desc")),
                "latitude": self.safe_float(row.get("stop_lat")),
                "longitude": self.safe_float(row.get("stop_lon")),
                "zone_id": self.clean_string(row.get("zone_id")),
                "wheelchair_accessible": row.get("wheelchair_boarding"),
                "semantic_role": "multimodal_access_point"
            }

            self.normalized_entities["transit_stop"].append(stop_entity)

        print(
            f"[DONE] Normalized "
            f"{len(self.normalized_entities['transit_stop'])} transit stops."
        )

    def normalize_routes(self):
        print("\nNormalizing transit routes...\n")

        df = self.loaded_data.get("routes.txt")

        if df is None:
            print("[WARNING] routes.txt not loaded.")
            return

        for _, row in df.iterrows():
            route_entity = {
                "node_class": "transit_route",
                "id": self.normalize_identifier(row.get("route_id")),
                "short_name": self.clean_string(row.get("route_short_name")),
                "long_name": self.clean_string(row.get("route_long_name")),
                "description": self.clean_string(row.get("route_desc")),
                "route_type": row.get("route_type"),
                "route_color": self.clean_string(row.get("route_color")),
                "semantic_role": "mobility_corridor"
            }

            self.normalized_entities["transit_route"].append(route_entity)

        print(
            f"[DONE] Normalized "
            f"{len(self.normalized_entities['transit_route'])} transit routes."
        )

    def normalize_trips(self):
        print("\nNormalizing trip patterns...\n")

        df = self.loaded_data.get("trips.txt")

        if df is None:
            print("[WARNING] trips.txt not loaded.")
            return

        for _, row in df.iterrows():
            trip_entity = {
                "node_class": "transit_trip_pattern",
                "id": self.normalize_identifier(row.get("trip_id")),
                "route_id": self.normalize_identifier(row.get("route_id")),
                "service_id": self.clean_string(row.get("service_id")),
                "headsign": self.clean_string(row.get("trip_headsign")),
                "direction_id": row.get("direction_id"),
                "wheelchair_accessible": row.get("wheelchair_accessible"),
                "bikes_allowed": row.get("bikes_allowed"),
                "semantic_role": "temporal_mobility_pattern"
            }

            self.normalized_entities["transit_trip_pattern"].append(trip_entity)

        print(
            f"[DONE] Normalized "
            f"{len(self.normalized_entities['transit_trip_pattern'])} trip patterns."
        )

    def normalize_stop_times(self):
        print("\nNormalizing stop-time operational events...\n")

        df = self.loaded_data.get("stop_times.txt")

        if df is None:
            print("[WARNING] stop_times.txt not loaded.")
            return

        for _, row in df.iterrows():
            stop_time_entity = {
                "node_class": "stop_time_event",
                "trip_id": self.normalize_identifier(row.get("trip_id")),
                "arrival_time": self.clean_string(row.get("arrival_time")),
                "departure_time": self.clean_string(row.get("departure_time")),
                "stop_id": self.normalize_identifier(row.get("stop_id")),
                "stop_sequence": row.get("stop_sequence"),
                "pickup_type": row.get("pickup_type"),
                "drop_off_type": row.get("drop_off_type"),
                "semantic_role": "temporal_operational_transition"
            }

            self.normalized_entities["stop_time_event"].append(
                stop_time_entity
            )

        print(
            f"[DONE] Normalized "
            f"{len(self.normalized_entities['stop_time_event'])} stop-time events."
        )

    def summarize_normalized_entities(self):
        print("\n" + "=" * 80)
        print("NORMALIZED ENTITY SUMMARY")
        print("=" * 80)

        for entity_type, entities in self.normalized_entities.items():
            print(f"\n{entity_type}: {len(entities)}")

            if entities:
                print("\nSample Entity:")
                print(entities[0])

    def run(self):
        print("\n" + "=" * 80)
        print("GTFS SEMANTIC NORMALIZATION")
        print("=" * 80)

        self.normalize_stops()

        self.normalize_routes()

        self.normalize_trips()

        self.normalize_stop_times()

        self.summarize_normalized_entities()

        print("\nSemantic normalization completed successfully.\n")