import re
from typing import List, Dict

class ActionDetector:
    def __init__(self):
        # Define patterns for action detection
        self.patterns = [
            {
                "id": "view_dashboard",
                "label": "View Dashboard",
                "regex": r"(?i)dashboard|status|overview",
                "type": "navigation"
            },
            {
                "id": "download_report",
                "label": "Download Report",
                "regex": r"(?i)report|download|export",
                "type": "file"
            },
            {
                "id": "open_manual",
                "label": "Open Manual",
                "regex": r"(?i)manual|instruction|guide",
                "type": "pdf"
            }
        ]

    def detect_actions(self, text: str) -> List[Dict]:
        """
        Analyzes the given text and returns a list of detected actions.
        """
        actions = []
        
        for pattern in self.patterns:
            if re.search(pattern["regex"], text):
                actions.append({
                    "id": pattern["id"],
                    "label": pattern["label"],
                    "type": pattern["type"]
                })
        
        return actions

# Singleton instance
action_detector = ActionDetector()
