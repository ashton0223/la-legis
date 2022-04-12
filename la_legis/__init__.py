from . import core

def create_legislature():
    l = core.Legis()
    l.create_house()
    l.create_senate()

    l.house.add_speaker()
    l.senate.add_president()