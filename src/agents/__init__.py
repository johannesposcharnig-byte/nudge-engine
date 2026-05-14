"""Agent implementations for the Nudge Engine."""

from .critic import CriticAgent
from .data import DataAgent
from .devils_advocate import DevilsAdvocateAgent
from .evaluation import EvaluationAgent
from .governance import GovernanceAgent
from .ml import MLAgent
from .policy import PolicyAgent
from .research import ResearchAgent
from .statistical import StatisticalAgent

__all__ = [
    "CriticAgent",
    "DataAgent",
    "DevilsAdvocateAgent",
    "EvaluationAgent",
    "GovernanceAgent",
    "MLAgent",
    "PolicyAgent",
    "ResearchAgent",
    "StatisticalAgent",
]
