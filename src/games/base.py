from abc import ABC, abstractmethod


class BaseGame(ABC):
    @abstractmethod
    def get_initial_state(self) -> dict:
        pass

    @abstractmethod
    def validate_move(self, current_state: dict, move: dict, player_id: str) -> bool:
        pass

    @abstractmethod
    def apply_move(self, current_state: dict, move: dict) -> dict:
        pass

    @abstractmethod
    def check_victory(self, current_state: dict) -> str | None:
        pass
