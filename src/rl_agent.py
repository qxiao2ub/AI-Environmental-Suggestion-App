"""Lightweight reinforcement-learning layer for recommendation improvement.

This is a contextual bandit rather than a full production RL system. It learns which
recommendation wording/action works best for a given user group and hazard from feedback.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass
class ContextualBandit:
    epsilon: float = 0.10
    alpha: float = 0.35
    seed: int = 42
    q_values: dict[str, dict[str, float]] = field(default_factory=dict)
    counts: dict[str, dict[str, int]] = field(default_factory=dict)
    feedback_log: list[dict[str, object]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._rng = np.random.default_rng(self.seed)

    @staticmethod
    def context_key(user_type: str, hazard: str) -> str:
        return f"{user_type.strip().lower()}::{hazard.strip().lower()}"

    def choose_action(self, user_type: str, hazard: str, actions: Iterable[str]) -> str:
        action_list = list(actions)
        if not action_list:
            return "No action available for this context."
        key = self.context_key(user_type, hazard)
        self.q_values.setdefault(key, {action: 0.0 for action in action_list})
        self.counts.setdefault(key, {action: 0 for action in action_list})
        for action in action_list:
            self.q_values[key].setdefault(action, 0.0)
            self.counts[key].setdefault(action, 0)

        if self._rng.random() < self.epsilon:
            return str(self._rng.choice(action_list))
        return max(action_list, key=lambda action: self.q_values[key].get(action, 0.0))

    def update(self, user_type: str, hazard: str, action: str, reward: float) -> float:
        reward = float(np.clip(reward, 0.0, 1.0))
        key = self.context_key(user_type, hazard)
        self.q_values.setdefault(key, {})
        self.counts.setdefault(key, {})
        old_value = self.q_values[key].get(action, 0.0)
        new_value = old_value + self.alpha * (reward - old_value)
        self.q_values[key][action] = new_value
        self.counts[key][action] = self.counts[key].get(action, 0) + 1
        self.feedback_log.append(
            {
                "context": key,
                "user_type": user_type,
                "hazard": hazard,
                "action": action,
                "reward": reward,
                "updated_q_value": new_value,
                "n_feedback": self.counts[key][action],
            }
        )
        return new_value

    def feedback_dataframe(self) -> pd.DataFrame:
        if not self.feedback_log:
            return pd.DataFrame(columns=["context", "user_type", "hazard", "action", "reward", "updated_q_value", "n_feedback"])
        return pd.DataFrame(self.feedback_log)

    def policy_table(self) -> pd.DataFrame:
        records = []
        for context, actions in self.q_values.items():
            for action, value in actions.items():
                records.append(
                    {
                        "context": context,
                        "action": action,
                        "q_value": round(float(value), 3),
                        "feedback_count": self.counts.get(context, {}).get(action, 0),
                    }
                )
        if not records:
            return pd.DataFrame(columns=["context", "action", "q_value", "feedback_count"])
        return pd.DataFrame(records).sort_values(["context", "q_value"], ascending=[True, False])


def simulate_feedback(agent: ContextualBandit, user_type: str, hazard: str, actions: list[str], n_rounds: int = 20) -> pd.DataFrame:
    """Demonstrate how feedback changes policy values using simulated rewards."""
    if not actions:
        return agent.feedback_dataframe()
    preferred_keyword = hazard.split()[0].lower()
    for _ in range(n_rounds):
        action = agent.choose_action(user_type, hazard, actions)
        reward = 0.85 if preferred_keyword in action.lower() else 0.45
        reward = float(np.clip(agent._rng.normal(reward, 0.12), 0, 1))
        agent.update(user_type, hazard, action, reward)
    return agent.feedback_dataframe()
