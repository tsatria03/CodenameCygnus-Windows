"""The agent profile: the dominant trait, how far the player has come, the four trait
scales and the achievements."""
import _quiet  # noqa: F401  first, before any of the game

from episode import STORY, fresh_achievements, key, make_app

from codenamecygnus.game.menus import MainMenu
from codenamecygnus.game.profile import (AchievementList, ProfileScreen, dominant_trait,
                                         scale_text)
from codenamecygnus.game.progress import Progress

PROLOGUE, ART_SHOW, LAIR = (STORY.episodes[e] for e in ('1.1.1', '1.2.1', '1.3.1'))
HOLIDAY = STORY.episodes['1.8.1']


def rows(screen):
    return [r.text for r in screen.rows()]


def test_the_dominant_trait_is_the_one_furthest_from_0_by_the_end_it_leans_to():
    assert dominant_trait({'Diplomacy': 3, 'Openness': -1}) == 'Charismatic'
    assert dominant_trait({'Openness': -2, 'Diplomacy': 1}) == 'Secretive'
    assert dominant_trait({'Activeness': 1}) == 'Athletic'
    assert dominant_trait({'Predictability': -4}) == 'Impulsive'
    assert dominant_trait({}) is None and dominant_trait({'Openness': 0}) is None


def test_a_tie_goes_to_the_first_in_the_originals_order():
    assert dominant_trait({'Activeness': -2, 'Openness': 2}) == 'Bold'
    assert dominant_trait({'Activeness': 2, 'Diplomacy': -2}) == 'Hostile'


def test_each_scale_says_which_way_it_leans_and_how_far():
    assert scale_text('Diplomacy', 3) == 'Diplomacy: Charismatic, 3'
    assert scale_text('Openness', -2) == 'Openness: Secretive, 2'
    assert scale_text('Activeness', 0) == 'Activeness: balanced'


def test_a_new_game_has_a_profile_of_nothing_yet():
    app = make_app()
    profile = ProfileScreen(app, STORY, achievements=fresh_achievements())
    assert rows(profile) == [
        'Back', 'Dominant trait: none yet.', 'Furthest episode: none yet.',
        'Episodes completed: 0 of 8.', 'Game progress: 0 percent.',
        'Openness: balanced', 'Predictability: balanced', 'Diplomacy: balanced',
        'Activeness: balanced', 'Achievements: 0 of 16']


def test_the_profile_reads_the_story_where_the_furthest_episode_is():
    app = make_app()
    p = Progress.shared()
    p.complete(PROLOGUE, {'Diplomacy': 1})
    p.begin(ART_SHOW, {'Diplomacy': 1})
    p.save_place(ART_SHOW, '016F_contactMark', {'Diplomacy': 3, 'Openness': -1})
    p.complete(HOLIDAY, {'Openness': 9})            # its own, never the mission's
    shown = rows(ProfileScreen(app, STORY, achievements=fresh_achievements()))
    assert shown[1:5] == ['Dominant trait: Charismatic.', 'Furthest episode: Episode 2, Art Show.',
                          'Episodes completed: 2 of 8.', 'Game progress: 25 percent.']
    assert shown[5:9] == ['Openness: Secretive, 1', 'Predictability: balanced',
                          'Diplomacy: Charismatic, 3', 'Activeness: balanced']


def test_a_finished_episode_gives_how_it_ended():
    app = make_app()
    Progress.shared().complete(PROLOGUE, {'Activeness': -2})
    shown = rows(ProfileScreen(app, STORY, achievements=fresh_achievements()))
    assert shown[1] == 'Dominant trait: Clever.' and shown[2] == 'Furthest episode: Episode 1, Prologue.'


def test_the_main_menu_opens_it_with_the_profile_sound_on_back():
    app = make_app()
    app.stack.push(MainMenu(app, STORY))
    key(app, 'down')
    key(app, 'return')                              # Agent profile
    assert isinstance(app.stack.top, ProfileScreen)
    assert app.speech.said[-2:] == ['Agent profile.', 'Back']
    assert getattr(app.audio.menu_sounds[-1], 'name', None) == '1930radio b'
    key(app, 'down')
    key(app, 'return')                              # Enter says a row again
    assert app.speech.said[-1] == 'Dominant trait: none yet.' and isinstance(app.stack.top, ProfileScreen)


def test_achievements_lists_all_16_earned_or_not_with_their_descriptions():
    app = make_app()
    kept = fresh_achievements()
    kept.add('event.m1e1_cardsWin')
    profile = ProfileScreen(app, STORY, achievements=kept)
    assert rows(profile)[-1] == 'Achievements: 1 of 16'
    app.stack.push(profile)
    key(app, 'end')
    key(app, 'return')
    listing = app.stack.top
    assert isinstance(listing, AchievementList) and app.speech.said[-2:] == ['Achievements.', 'Back']
    shown = rows(listing)
    assert len(shown) == 17 and shown[0] == 'Back'
    assert shown[1] == ("Card Shark, earned. Raise the bet in the Prologue's card game, "
                        "so that Krasnoff folds.")
    assert shown[2].startswith('Martini, not earned yet. Order the Martini')


if __name__ == '__main__':
    _quiet.run_tests(globals())
