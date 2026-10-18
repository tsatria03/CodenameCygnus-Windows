"""The 16 achievements, kept on the player's computer: section 5 of
aidocks/plans/story_engine_plan.md.

The original reported them to Apple's Game Center, whose servers held their names and
descriptions, so those are lost. The port keeps its own list (the dev, 2026-10-17: "I want
local achievements since the game center thing is an apple thing, and it's online"), with
names the dev approved ("I like all of the names") and descriptions made specific ("Please
change it to make it more clearer"), each checked against analysis/script/.

23 states earn one, since some can be reached by several routes. A state names its
achievement by the original's Game Center id, such as
``net.reactivestudios.codenamecygnus.event.m1e1_cardsWin``; the port keeps the part after
``net.reactivestudios.codenamecygnus.``. Earned ones are kept for good in
``saves/achievements.json`` (aidocks/plans/saves_plan.md), across every replay and restart.
"""
from __future__ import annotations

import logging

from .. import paths
from ..platform.files import JsonFile

log = logging.getLogger('achievements')

PREFIX = 'net.reactivestudios.codenamecygnus.'

#: (id, name, description), in the order the agent profile lists them.
ACHIEVEMENTS = (
    ('event.m1e1_cardsWin', 'Card Shark',
     "Raise the bet in the Prologue's card game, so that Krasnoff folds."),
    ('event.m1e2_drink_1', 'Martini',
     'Order the Martini at the hotel bar in Art Show.'),
    ('event.m1e3_sex_1', "Neptune's Lover",
     "Go off with Serena or Seth, Neptune's lover, when they invite you in, in Neptune's Lair."),
    ('event.m1e4_chooseTrust_0', 'Trust Matthews',
     "Speak Director Matthews' password, BE, into the bomb in Consulate, rather than MAELSTROM."),
    ('inventory.m1e5_lazarusCard_1', "Lazarus' Card",
     "Cut the green wire in Lazarus' test in Lazarus Awakens, so that he gives you his card."),
    ('trait.happyChildhood_0', 'Unhappy Childhood',
     "Tell Neptune that your childhood was not a happy one, in Neptune's Gift."),
    ('romance.m1_maleInterest_0', "Ladies' Agent",
     'Tell Director Matthews, in Art Show, that you work your charm on ladies.'),
    ('romance.m1_maleInterest_1', "Gentlemen's Agent",
     'Tell Director Matthews, in Art Show, that you work your charm on gentlemen.'),
    ('trait.cygnusLoyalty_1', "Alexander's Loyalist",
     'Finish Signum Cygni having sided with Alexander more than with Director Matthews.'),
    ('trait.cygnusLoyalty_0', "Matthews' Loyalist",
     'Finish Signum Cygni having sided with Director Matthews more than with Alexander.'),
    ('npc_favor.succeedRhodes', "Rhodes' Ally",
     'Win Agent Rhodes over to your side in Signum Cygni.'),
    ('npc_favor.failRhodes', "Rhodes' Rival",
     'Turn Agent Rhodes against you in Signum Cygni, so that you end up fighting him.'),
    ('completion.1.7.1', 'Mission Complete',
     'Finish Signum Cygni, the last episode of Mission 1.'),
    ('prize', 'The Prize',
     'Find the prize ending of Holiday Party.'),
    ('sneeze', 'Sneeze',
     'Find the sneeze ending of Holiday Party.'),
    ('stalemate', 'Stalemate',
     'Find the stalemate ending of Holiday Party.'),
)
IDS = [a[0] for a in ACHIEVEMENTS]
NAMES = {a[0]: a[1] for a in ACHIEVEMENTS}
DESCRIPTIONS = {a[0]: a[2] for a in ACHIEVEMENTS}


def short_id(achievement_id):
    """``event.m1e1_cardsWin`` for the original's full Game Center id, or for itself."""
    return achievement_id[len(PREFIX):] if achievement_id.startswith(PREFIX) else achievement_id


def name_of(achievement_id):
    return NAMES.get(short_id(achievement_id), short_id(achievement_id))


class Achievements:
    _shared = None

    @classmethod
    def shared(cls):
        if cls._shared is None:
            cls._shared = Achievements()
        return cls._shared

    def __init__(self, path=None):
        self.file = JsonFile(path or paths.user_path('saves', 'achievements.json'))
        saved = self.file.data.get('earned')
        saved = saved if isinstance(saved, list) else []
        self.earned = {short_id(a) for a in saved if isinstance(a, str) and short_id(a) in NAMES}
        if self.file.recovered:
            self.save()

    def __contains__(self, achievement_id):
        return short_id(achievement_id) in self.earned

    @property
    def count(self):
        return len(self.earned)

    def add(self, achievement_id):
        """Note an achievement earned. True the first time ever, when it is to be announced."""
        key = short_id(achievement_id)
        if key not in NAMES:
            log.warning('a state earns %s, which is not one of the 16', achievement_id)
            return False
        if key in self.earned:
            return False
        self.earned.add(key)
        self.save()
        log.info('achievement earned: %s', NAMES[key])
        return True

    def save(self):
        self.file.data = {'earned': [a for a in IDS if a in self.earned]}
        self.file.write()
