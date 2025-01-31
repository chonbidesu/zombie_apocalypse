# barricade_data.py

from enum import Enum, auto


class BarricadeState(Enum):
    NOT_BARRICADED = auto()
    LOOSELY_BARRICADED = auto()
    LIGHTLY_BARRICADED = auto()
    QUITE_STRONGLY_BARRICADED = auto()
    VERY_STRONGLY_BARRICADED = auto()
    HEAVILY_BARRICADED = auto()
    VERY_HEAVILY_BARRICADED = auto()
    EXTREMELY_HEAVILY_BARRICADED = auto()


BARRICADE_DESCRIPTIONS = {
    BarricadeState.NOT_BARRICADED: "not barricaded",
    BarricadeState.LOOSELY_BARRICADED: "loosely barricaded",
    BarricadeState.LIGHTLY_BARRICADED: "lightly barricaded",
    BarricadeState.QUITE_STRONGLY_BARRICADED: " quite strongly barricaded",
    BarricadeState.VERY_STRONGLY_BARRICADED: "very strongly barricaded",
    BarricadeState.HEAVILY_BARRICADED: "heavily barricaded",
    BarricadeState.VERY_HEAVILY_BARRICADED: "very heavily barricaded",
    BarricadeState.EXTREMELY_HEAVILY_BARRICADED: "extremely heavily barricaded"
}