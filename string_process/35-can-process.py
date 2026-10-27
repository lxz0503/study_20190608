#!/usr/bin/env python3
from typing import List, Dict, Any


class CANLogAnalyzer(object):
    def __int__(self):
        pass

    def aggregate_traffic(self, logs: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Aggregates raw CAN bus traces into a structured summary map.

        Time Complexity: O(N) where N is the number of logs.
        Space Complexity: O(M) where M is the number of unique CAN IDs.
        """
        # We use a standard dictionary to store our aggregated tracking states
        # Key: CAN_ID -> Value: {"count": int, "last_timestamp": int, "payload": str}
        can_summary = {}

        for log in logs:
            if not log.strip():
                continue

            # Split the immutable string efficiently using whitespace parsing
            # Splitting once per line is O(1) space relative to the line size
            parts = log.split()
            if len(parts) != 3:
                continue  # Skip corrupt telemetry frames safely

            raw_timestamp, can_id, payload = parts
            timestamp = int(raw_timestamp)

            if can_id not in can_summary:
                # Initialize tracking for a newly encountered ECU CAN ID
                can_summary[can_id] = {
                    "count": 1,
                    "last_timestamp": timestamp,
                    "payload": payload
                }
            else:
                # Update metrics for an existing CAN ID
                can_summary[can_id]["count"] += 1

                # Check if this log frame is newer than the one we have stored
                # (Handles unsorted logs elegantly without a global sort operation)
                if timestamp > can_summary[can_id]["last_timestamp"]:
                    can_summary[can_id]["last_timestamp"] = timestamp
                    can_summary[can_id]["payload"] = payload

        # Clean up internal timestamp tracking before returning the final report
        # to match the expected consumer API payload blueprint
        for can_id in can_summary:
            del can_summary[can_id]["last_timestamp"]

        return can_summary


# --- Verification & Test Verification Harness ---
if __name__ == "__main__":
    raw_traces = [
        "1718910001 0x1A0 00FF12AB",
        "1718910005 0x2B0 FFFFFFFF",
        "1718910003 0x1A0 11223344",  # Out of order timestamp for 0x1A0
        "1718910006 0x1A0 AABBCCDD",  # Most recent payload for 0x1A0
        "1718910002 0x2B0 00000000"
    ]

    analyzer = CANLogAnalyzer()
    result = analyzer.aggregate_traffic(raw_traces)

    print(result)
