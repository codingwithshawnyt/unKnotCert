"""
Mini environment for knot state transitions.
"""

import numpy as np
from typing import List, Tuple, Dict, Any, Optional

from .gauss import Token, MoveDescriptor, get_valid_actions, apply_action, crossing_number
from .canonical import canonical, canonical_str

Token = Tuple[int, int]
MoveDescriptor = Tuple


class KnotEnv:
    """Environment for Reidemeister moves on Gauss word representations."""

    def __init__(self, max_crossings: int = 50, max_actions: int = 128):
        self.max_crossings = max_crossings
        self.max_actions = max_actions
        self.state: Optional[List[Token]] = None
        self._next_id: int = 1
        self._initial_word: Optional[List[Token]] = None

    def reset(self, initial_word: List[Token]) -> Dict[str, Any]:
        """Reset environment to initial word."""
        self.state = initial_word.copy()
        self._initial_word = initial_word.copy()
        max_id = max(c for c, _ in initial_word) if initial_word else 0
        self._next_id = max_id + 1
        return self._get_obs()

    def step(self, action_index: int) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """Take a step using the action at action_index in valid_actions."""
        valid = self.valid_actions()
        if action_index >= len(valid):
            raise ValueError(f"Invalid action index {action_index}, only {len(valid)} valid actions")

        move = valid[action_index]
        self.state, self._next_id = apply_action(self.state, move, self._next_id)

        done = len(self.state) == 0 or crossing_number(self.state) == 0
        reward = 0.0  # Not used for certification
        info = {'crossing_number': crossing_number(self.state)}
        return self._get_obs(), reward, done, info

    def valid_actions(self) -> List[MoveDescriptor]:
        """Return list of valid moves from current state."""
        if self.state is None:
            return []
        return get_valid_actions(self.state, self._next_id)

    def action_mask(self) -> np.ndarray:
        """Return boolean mask of valid actions (size max_actions)."""
        num_valid = len(self.valid_actions())
        mask = np.zeros(self.max_actions, dtype=bool)
        mask[:num_valid] = True
        return mask

    def _get_obs(self) -> Dict[str, Any]:
        """Return observation dictionary."""
        return {
            'state': self.state,
            'action_mask': self.action_mask(),
            'canonical': canonical_str(self.state) if self.state else '',
            'crossing_number': crossing_number(self.state) if self.state else 0
        }
