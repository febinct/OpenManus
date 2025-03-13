#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Cost:
    """
    Cost class can record various costs during running and evaluation.
    Currently we define the following costs:
        accumulated_cost: the total cost (USD $) of the current LLM.
    """

    def __init__(self) -> None:
        self._accumulated_cost: float = 0.0
        self._costs: list[float] = []

    @property
    def accumulated_cost(self) -> float:
        return self._accumulated_cost

    @accumulated_cost.setter
    def accumulated_cost(self, value: float) -> None:
        if value < 0:
            raise ValueError("Total cost cannot be negative.")
        self._accumulated_cost = value

    @property
    def costs(self) -> list:
        return self._costs

    def add_cost(self, value: float) -> None:
        if value < 0:
            raise ValueError("Added cost cannot be negative.")
        self._accumulated_cost += value
        self._costs.append(value)

    def get(self):
        """
        Return the costs in a dictionary.
        """
        return {"accumulated_cost": self._accumulated_cost, "costs": self._costs}

    def log(self):
        """
        Log the costs.
        """
        cost = self.get()
        logs = ""
        for key, value in cost.items():
            logs += f"{key}: {value}\n"
        return logs
