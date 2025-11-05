"""
Follow-up schedule constants for RealtorOS.
"""

FOLLOWUP_SCHEDULE = {
    "Day 1": {
        "days": 1,
        "priority": "high",
        "description": "First follow-up after initial contact"
    },
    "Day 3": {
        "days": 3,
        "priority": "medium",
        "description": "Second follow-up to maintain engagement"
    },
    "Week 1": {
        "days": 7,
        "priority": "medium",
        "description": "Weekly check-in to provide updates"
    },
    "Week 2": {
        "days": 14,
        "priority": "low",
        "description": "Bi-weekly follow-up for nurturing"
    },
    "Month 1": {
        "days": 30,
        "priority": "low",
        "description": "Monthly follow-up for long-term nurturing"
    }
}

# Priority levels for task scheduling
PRIORITY_LEVELS = {
    "high": 1,
    "medium": 2,
    "low": 3
}

# Task status options
TASK_STATUSES = [
    "pending",
    "completed",
    "skipped",
    "cancelled"
]

# Client stages
CLIENT_STAGES = [
    "lead",
    "negotiating",
    "under_contract",
    "closed",
    "lost"
]

# Property types
PROPERTY_TYPES = [
    "residential",
    "commercial",
    "land",
    "other"
]

