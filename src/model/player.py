from dataclasses import dataclass


@dataclass
class Player:
    '''
    Class that describes a one footbal player.
    '''

    name: str
    role: str
    age: int
    nationality: str
    club: str
    price: int
