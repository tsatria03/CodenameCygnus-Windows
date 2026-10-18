"""The progress file: what each episode begins and ends with, the place to continue from,
the locks, and Restart erasing what came after."""
import _quiet  # noqa: F401  first, before any of the game

import json
import os
import tempfile

from episode import STORY, end_voice, jump, start, until_choices

from codenamecygnus.game.progress import COMPLETED, IN_PROGRESS, NEW, Progress

PROLOGUE, ART_SHOW, LAIR = (STORY.episodes[e] for e in ('1.1.1', '1.2.1', '1.3.1'))
HOLIDAY = STORY.episodes['1.8.1']


def fresh(path=None):
    return Progress(path or os.path.join(tempfile.mkdtemp(dir=_quiet.FOLDER), 'progress.json'),
                    story=STORY)


def test_a_new_game_has_only_the_prologue_and_holiday_party_open():
    p = fresh()
    assert [e.title for e in STORY.playable_episodes() if not p.locked(e)] == ['Prologue', 'Holiday Party']
    assert all(p.state_of(e) == NEW for e in STORY.playable_episodes())
    assert p.continue_episode() is None


def test_an_episode_begins_with_what_the_one_before_it_ended_with():
    p = fresh()
    assert p.start_variables(ART_SHOW) == {}
    p.complete(PROLOGUE, {'Diplomacy': 2, 'event.m1e1_cardsWin': 1})
    assert not p.locked(ART_SHOW)
    assert p.start_variables(ART_SHOW) == {'Diplomacy': 2, 'event.m1e1_cardsWin': 1}
    assert p.start_variables(HOLIDAY) == {}, 'Holiday Party uses none of the others'


def test_the_place_is_kept_in_the_file_and_read_back():
    p = fresh()
    p.begin(PROLOGUE, {})
    p.save_place(PROLOGUE, '012introRejectPrompt', {'Openness': 1})
    again = fresh(p.file.path)
    assert again.state_of(PROLOGUE) == IN_PROGRESS
    assert again.place(PROLOGUE) == ('012introRejectPrompt', {'Openness': 1})
    assert again.continue_episode() is PROLOGUE


def test_continue_goes_to_the_episode_played_most_recently():
    p = fresh()
    p.save_place(PROLOGUE, '012introRejectPrompt', {})
    p.save_place(HOLIDAY, '009drinkPrompt_m1e8', {})
    assert p.continue_episode() is HOLIDAY
    p.complete(HOLIDAY, {})
    assert p.continue_episode() is None and p.place(PROLOGUE) is not None


def test_restart_erases_every_later_episode_but_never_holiday_party():
    p = fresh()
    p.complete(PROLOGUE, {'Openness': 1})
    p.complete(ART_SHOW, {'Openness': 2})
    p.save_place(LAIR, '012roseResponse', {})
    p.save_place(HOLIDAY, '009drinkPrompt_m1e8', {})
    began = p.restart(PROLOGUE)
    assert began == {} and p.state_of(PROLOGUE) == IN_PROGRESS and p.place(PROLOGUE) is None
    assert p.state_of(ART_SHOW) == NEW and p.state_of(LAIR) == NEW and p.locked(ART_SHOW)
    assert p.state_of(HOLIDAY) == IN_PROGRESS and p.place(HOLIDAY) is not None


def test_restart_starts_again_with_what_the_episode_began_with():
    p = fresh()
    p.complete(PROLOGUE, {'Openness': 1})
    p.begin(ART_SHOW, p.start_variables(ART_SHOW))
    p.save_place(ART_SHOW, '016F_contactMark', {'Openness': 5})
    assert p.restart(ART_SHOW) == {'Openness': 1}


def test_a_damaged_entry_is_left_out_rather_than_trusted():
    path = os.path.join(tempfile.mkdtemp(dir=_quiet.FOLDER), 'progress.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({'last': '9.9.9', 'episodes': {
            '1.1.1': {'state': 'completed', 'ended_with': {'Openness': 'lots', 'Diplomacy': 1}},
            '9.9.9': {'state': 'completed'}, '1.2.1': 'nonsense'}}, f)
    p = fresh(path)
    assert p.state_of(PROLOGUE) == COMPLETED and p.start_variables(ART_SHOW) == {'Diplomacy': 1}
    assert p.continue_episode() is None and p.state_of(ART_SHOW) == NEW


def test_playing_saves_the_place_with_the_variables_from_before_the_state():
    app, screen = start()
    p = Progress.shared()
    jump(app, screen, '003introRaiseBet')            # IMPULSIVE: lowers Predictability
    state, variables = p.place(PROLOGUE)
    assert state == '003introRaiseBet'
    assert variables.get('Predictability') == 0 and screen.run.variables['Predictability'] == -1
    # Continuing there enters it again, applying it once: -1, not -2.
    from codenamecygnus.game.episode_screen import EpisodeScreen
    again = EpisodeScreen(app, PROLOGUE, story=STORY, variables=variables, at=state, progress=p)
    app.stack.push(again)
    assert again.run.variables['Predictability'] == -1


def test_finishing_an_episode_completes_it_and_opens_the_next():
    app, screen = start()
    p = Progress.shared()
    jump(app, screen, PROLOGUE.end)
    until_choices(app, screen)
    assert p.state_of(PROLOGUE) == COMPLETED and not p.locked(ART_SHOW)
    assert p.place(PROLOGUE) is None


def test_the_pause_menus_restart_erases_what_came_after_too():
    app, screen = start()
    p = Progress.shared()
    p.complete(ART_SHOW, {})                        # as if played before
    until_choices(app, screen)
    screen.restart()
    assert p.state_of(ART_SHOW) == NEW


if __name__ == '__main__':
    _quiet.run_tests(globals())
