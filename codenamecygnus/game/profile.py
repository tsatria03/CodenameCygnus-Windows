"""The profile: section 2 of aidocks/plans/saves_plan.md, from
aidocks/plans/menus_plan.md.

The original's Profile screen (``-[CCProfileDatasource createDatasource]``, 0x100017d68)
without its agent name, which belonged to the player's online account and which the
story never uses:

    Back
    Dominant trait: Charismatic.
    Furthest episode: Episode 3, Neptune's Lair.
    Episodes completed: 2 of 8.
    Game progress: 25 percent.
    Openness: Bold, 2          the four trait scales, each saying which way it leans
    Predictability: balanced
    Diplomacy: Charismatic, 3
    Activeness: Clever, 1
    Achievements: 3 of 16      Enter lists all 16, each earned or not, with its description

The traits are read as the original's ``traitsFromProfile:accessible:`` (0x1000184d4) and
the ``Extensions`` category's ``dominantTrait`` (0x1000337cc): each trait is one number, a
choice word at one end raising it and its opposite lowering it. The dominant trait is the
one furthest from 0 either way, named by the end it leans to. The original kept whichever
it met first in an unordered dictionary on a tie; the port takes the first in the
original's own order, Openness, Predictability, Diplomacy, Activeness, so it is the same
every time. The scales say which way they lean, as the original's VoiceOver text, "Openness:
2", did not (the dev, 2026-10-17: "I want it announced clearly").
"""
from __future__ import annotations

from ..ui.menu import Menu, Row
from .achievements import ACHIEVEMENTS
from .progress import Progress
from .story import TRAITS

#: Each trait's two ends, the low end first (traitsFromProfile:accessible:).
ENDS = {
    'Openness': ('Secretive', 'Bold'),
    'Predictability': ('Impulsive', 'Focused'),
    'Diplomacy': ('Hostile', 'Charismatic'),
    'Activeness': ('Clever', 'Athletic'),
}


def leaning(trait, value):
    """The end a trait leans to: "Charismatic" for Diplomacy 3, "Hostile" for -1."""
    low, high = ENDS[trait]
    return high if value > 0 else low


def dominant_trait(variables):
    """The trait furthest from 0, as its end, or None while every trait is 0. A tie goes
    to the first in the original's order."""
    best, best_size = None, 0
    for trait in TRAITS:
        value = variables.get(trait, 0)
        if abs(value) > best_size:
            best, best_size = trait, abs(value)
    return leaning(best, variables[best]) if best else None


def scale_text(trait, value):
    """ "Diplomacy: Charismatic, 3", "Openness: Secretive, 2", "Activeness: balanced" """
    if value == 0:
        return '%s: balanced' % trait
    return '%s: %s, %d' % (trait, leaning(trait, value), abs(value))


class ProfileScreen(Menu):
    name = 'profile'
    # "Profile", as the original's screen was called (the dev, 2026-10-18: "Please rename
    # agent profile to profile").
    title = 'Profile.'

    def __init__(self, app, story, progress=None, achievements=None):
        super().__init__(app)
        from .achievements import Achievements
        self.story = story
        self.progress = progress if progress is not None else Progress.shared(story)
        self.achievements = achievements if achievements is not None else Achievements.shared()

    def rows(self):
        p = self.progress
        variables = p.mission_variables()
        dominant = dominant_trait(variables)
        furthest = p.furthest_episode()
        total = len(self.story.playable_episodes())
        done = p.completed_count()
        say_again = lambda: self.say(self.row_text())
        lines = [
            'Dominant trait: %s.' % (dominant or 'none yet'),
            'Furthest episode: %s.' % ('Episode %d, %s' % (furthest.number, furthest.title)
                                       if furthest else 'none yet'),
            'Episodes completed: %d of %d.' % (done, total),
            'Game progress: %d percent.' % round(100 * done / total if total else 0),
        ] + [scale_text(t, variables.get(t, 0)) for t in TRAITS]
        return ([Row('Back', self.back)] + [Row(line, say_again) for line in lines] +
                [Row('Achievements: %d of %d' % (self.achievements.count, len(ACHIEVEMENTS)),
                     lambda: self.open(AchievementList(self.app, self.achievements)))])


class AchievementList(Menu):
    """All 16, each earned or not, with what earns it."""

    name = 'achievements'
    title = 'Achievements.'

    def __init__(self, app, achievements):
        super().__init__(app)
        self.achievements = achievements

    def rows(self):
        say_again = lambda: self.say(self.row_text())
        return [Row('Back', self.back)] + [
            Row('%s, %s. %s' % (name, 'earned' if key in self.achievements else 'not earned yet',
                                description), say_again)
            for key, name, description in ACHIEVEMENTS]
