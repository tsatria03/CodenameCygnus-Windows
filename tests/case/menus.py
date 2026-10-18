"""The opening, the main menu, the episode list and Credits, by what they say and play."""
import _quiet  # noqa: F401  first, before any of the game

import random

from episode import STORY, key, make_app

from codenamecygnus.game.episode_screen import RESTART_WARNING, EpisodeScreen
from codenamecygnus.game.menus import (HEADPHONES, LOADING, LOCKED, PORT_CREDIT, CreditsScreen,
                                       EpisodeList, EpisodeMenu, HeadphonesNotice, MainMenu,
                                       Opening, credit_lines)
from codenamecygnus.game.progress import Progress
from codenamecygnus.platform import runloop


def sounds(app):
    """The interface sounds played, by name, such as '1930radio a'."""
    return [getattr(s, 'name', s) for s in app.audio.menu_sounds]


def open_game(app):
    app.stack.push(Opening(app, story=STORY, rng=random.Random(3)))
    return app.stack.top


def test_the_opening_says_the_name_and_a_loading_message():
    app = make_app()
    opening = open_game(app)
    assert app.speech.said == ['Codename Cygnus. %s' % opening.message]
    assert opening.message in LOADING


def test_the_headphones_notice_comes_the_first_time_after_the_wait():
    app = make_app()
    open_game(app)
    app.loop.pump(runloop.clock() + 1.0)
    assert isinstance(app.stack.top, Opening), 'it went on before the message was heard'
    app.loop.pump(runloop.clock() + 3.0)
    assert isinstance(app.stack.top, HeadphonesNotice)
    assert app.speech.said[-2:] == [HEADPHONES, 'Continue']
    key(app, 'return')
    assert isinstance(app.stack.top, MainMenu) and app.settings.get('headphones_notice_shown')


def test_after_the_first_time_the_opening_goes_straight_to_the_main_menu():
    app = make_app()
    app.settings.set('headphones_notice_shown', True)
    open_game(app)
    key(app, 'space')                               # any key goes on at once
    assert isinstance(app.stack.top, MainMenu)
    assert app.speech.said[-2:] == ['Main menu.', 'Episodes']
    app.loop.pump(runloop.clock() + 5)               # the opening's own wait does nothing now
    assert isinstance(app.stack.top, MainMenu) and len(app.stack.screens) == 1


def test_escape_on_the_headphones_notice_goes_on_too():
    app = make_app()
    open_game(app)
    key(app, 'return')
    key(app, 'escape')
    assert isinstance(app.stack.top, MainMenu) and app.running


def test_the_main_menu_rows_and_escape_quits():
    app = make_app()
    menu = MainMenu(app, STORY)
    app.stack.push(menu)
    assert [r.text for r in menu.rows()] == ['Episodes', 'Settings', 'Credits', 'Quit']
    key(app, 'escape')
    assert not app.running


def test_episodes_lists_the_eight_by_number_and_title_with_the_episodes_sound():
    app = make_app()
    app.stack.push(MainMenu(app, STORY))
    key(app, 'return')
    listing = app.stack.top
    assert isinstance(listing, EpisodeList) and sounds(app) == ['1930radio a']
    assert app.speech.said[-2:] == ['Episodes. Mission 1.', 'Back']
    rows = [r.text for r in listing.rows()]
    assert rows[1] == 'Episode 1, Prologue' and rows[-1] == 'Episode 8, Holiday Party'
    assert len(rows) == 9


def test_back_at_the_top_of_the_episode_list_goes_back():
    app = make_app()
    app.stack.push(MainMenu(app, STORY))
    key(app, 'return')
    key(app, 'return')                              # Back, the first row
    assert isinstance(app.stack.top, MainMenu)
    assert sounds(app) == ['1930radio a', '1930radio a']


def progress():
    return Progress.shared()


def test_an_episode_says_its_description_then_offers_start():
    app = make_app()
    progress().complete(STORY.episodes['1.1.1'], {})     # so Art Show is open
    app.stack.push(MainMenu(app, STORY))
    key(app, 'return')
    key(app, 'down')
    key(app, 'down')
    key(app, 'return')                              # Art Show
    screen = app.stack.top
    assert isinstance(screen, EpisodeMenu)
    description = STORY.episodes['1.2.1'].description
    assert app.speech.said[-2:] == ['Episode 2, Art Show.', 'Back']
    assert [r.text for r in screen.rows()] == ['Back', description, 'Start']
    key(app, 'down')
    assert app.speech.said[-1] == description
    key(app, 'return')                              # Enter on it says it again
    assert app.speech.said[-1] == description and app.stack.top is screen
    assert sounds(app)[-1] == 'sound a'


def test_the_last_episodes_screens_have_no_preview():
    app = make_app()
    progress().complete(STORY.episodes['1.6.1'], {})     # so Signum Cygni is open
    for episode_id in ('1.7.1', '1.8.1'):
        episode = STORY.episodes[episode_id]
        menu = EpisodeMenu(app, STORY, episode)
        assert [r.text for r in menu.rows()] == ['Back', episode.description, 'Start'], episode_id


def test_start_plays_the_episode_and_leaving_it_comes_back_to_the_list():
    app = make_app()
    app.stack.push(MainMenu(app, STORY))
    key(app, 'return')
    key(app, 'down')
    key(app, 'return')                              # the Prologue
    key(app, 'down')
    key(app, 'down')
    key(app, 'return')                              # Start, after the description
    playing = app.stack.top
    assert isinstance(playing, EpisodeScreen) and playing.episode.title == 'Prologue'
    assert sounds(app)[-1] == '1930radio a'
    assert not any(isinstance(s, EpisodeMenu) for s in app.stack.screens)
    key(app, 'escape')
    assert sounds(app)[-1] == 'sound a', 'the pause menu opened without its sound'
    key(app, 'end')
    key(app, 'return')                              # Return to menu
    assert isinstance(app.stack.top, EpisodeList)
    assert app.speech.said[-2:] == ['Episodes. Mission 1.', 'Episode 1, Prologue, in progress'], \
        'not back on the episode'


def test_the_list_says_each_episodes_state_and_which_are_locked():
    app = make_app()
    listing = EpisodeList(app, STORY)
    rows = [r.text for r in listing.rows()]
    assert rows[1:3] == ['Episode 1, Prologue', 'Episode 2, Art Show, locked']
    assert rows[-1] == 'Episode 8, Holiday Party', 'Holiday Party is locked at first'
    progress().complete(STORY.episodes['1.1.1'], {})
    progress().begin(STORY.episodes['1.2.1'], {})
    rows = [r.text for r in listing.rows()]
    assert rows[1:4] == ['Episode 1, Prologue, completed', 'Episode 2, Art Show, in progress',
                         "Episode 3, Neptune's Lair, locked"]


def test_a_locked_episode_opens_on_back_its_description_and_locked():
    app = make_app()
    app.stack.push(MainMenu(app, STORY))
    key(app, 'return')
    key(app, 'down')
    key(app, 'down')
    key(app, 'return')                              # Art Show, locked
    screen = app.stack.top
    assert isinstance(screen, EpisodeMenu)
    assert app.speech.said[-2:] == ['Episode 2, Art Show.', 'Back']
    assert [r.text for r in screen.rows()] == ['Back', STORY.episodes['1.2.1'].description, 'Locked']
    key(app, 'end')
    key(app, 'return')                              # Locked: why, as the original said it
    assert app.speech.said[-1] == LOCKED == ('You need to complete the previous episode '
                                             'before starting this one.')
    assert app.stack.top is screen


def test_an_episode_in_progress_offers_continue_and_restart():
    app = make_app()
    prologue = STORY.episodes['1.1.1']
    progress().begin(prologue, {})
    progress().save_place(prologue, '012introRejectPrompt', {'Diplomacy': 1})
    menu = EpisodeMenu(app, STORY, prologue)
    assert [r.text for r in menu.rows()][2:] == ['Continue', 'Restart episode']
    app.stack.push(menu)
    key(app, 'down')
    key(app, 'down')
    key(app, 'return')                              # Continue
    playing = app.stack.top
    assert isinstance(playing, EpisodeScreen) and playing.run.current.name == '012introRejectPrompt'
    assert playing.run.variables.get('Diplomacy') == 1


def test_a_completed_episode_offers_replay_and_its_preview():
    app = make_app()
    progress().complete(STORY.episodes['1.1.1'], {})
    menu = EpisodeMenu(app, STORY, STORY.episodes['1.1.1'])
    assert [r.text for r in menu.rows()][2:] == ['Replay episode', 'Preview next episode']


def test_replay_asks_with_the_originals_warning_and_locks_what_came_after():
    app = make_app()
    for e in ('1.1.1', '1.2.1'):
        progress().complete(STORY.episodes[e], {'Openness': 2})
    app.stack.push(EpisodeMenu(app, STORY, STORY.episodes['1.1.1']))
    key(app, 'down')
    key(app, 'down')
    key(app, 'return')                              # Replay episode
    assert app.speech.said[-2:] == [RESTART_WARNING, 'No']
    key(app, 'escape')                              # No: nothing changes
    assert progress().state_of(STORY.episodes['1.2.1']) == 'completed'
    key(app, 'return')
    key(app, 'down')
    key(app, 'return')                              # Yes
    assert isinstance(app.stack.top, EpisodeScreen) and app.speech.said[-1] == 'Restarting Prologue.'
    assert progress().state_of(STORY.episodes['1.2.1']) == 'new'
    assert progress().locked(STORY.episodes['1.2.1'])


def test_continue_comes_first_in_the_main_menu_and_goes_back_to_the_place():
    app = make_app()
    art_show = STORY.episodes['1.2.1']
    progress().complete(STORY.episodes['1.1.1'], {})
    progress().begin(art_show, {})
    progress().save_place(art_show, '016F_contactMark', {'Openness': 1})
    menu = MainMenu(app, STORY)
    app.stack.push(menu)
    assert app.speech.said[-1] == 'Continue Art Show'
    key(app, 'return')
    playing = app.stack.top
    assert isinstance(playing, EpisodeScreen) and playing.episode is art_show
    assert playing.run.current.name == '016F_contactMark' and sounds(app)[-1] == '1930radio a'


def test_there_is_no_continue_before_anything_is_played():
    app = make_app()
    assert [r.text for r in MainMenu(app, STORY).rows()][0] == 'Episodes'


def test_escape_goes_back_with_the_back_sound():
    app = make_app()
    app.stack.push(MainMenu(app, STORY))
    key(app, 'return')
    key(app, 'escape')
    assert isinstance(app.stack.top, MainMenu) and sounds(app) == ['1930radio a', '1930radio a']


def test_credits_lists_reactive_studios_and_the_port():
    app = make_app()
    app.stack.push(MainMenu(app, STORY))
    key(app, 'down')
    key(app, 'down')
    key(app, 'return')
    credits = app.stack.top
    assert isinstance(credits, CreditsScreen) and sounds(app) == ['1930radio c']
    rows = [r.text for r in credits.rows()]
    assert app.speech.said[-2:] == ['Credits.', 'Back']
    assert rows[:2] == ['Back', 'Codename Cygnus is a game by Reactive Studios.']
    assert 'CEO: Jonathon Myers' in rows and rows[-1] == PORT_CREDIT
    assert '' not in rows


def test_a_credit_with_no_title_is_a_heading_in_plain_case():
    assert credit_lines([{'title': '', 'credit': 'VOICE ACTORS'},
                         {'title': 'Miss Honeybourne', 'credit': 'Sarah Elmaleh'},
                         {'title': '', 'credit': ''}]) == ['Voice actors', 'Miss Honeybourne: Sarah Elmaleh']


if __name__ == '__main__':
    _quiet.run_tests(globals())
