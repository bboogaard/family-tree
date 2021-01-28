from dataclasses import dataclass
from typing import List

from tree.models import Ancestor, Lineage as LineageModel


@dataclass
class Lineage:
    generations: List[Ancestor]

    @classmethod
    def from_lineage(cls, lineage: LineageModel):
        generations = [lineage.ancestor] + [
            generation.ancestor
            for generation in lineage.generations.all()
        ] + [
            lineage.descendant
        ]
        return Lineage(generations=generations)
