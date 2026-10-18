"""The story's rules, on the real exported story: variables, conditions, choices and episodes."""
import _quiet  # noqa: F401  first, before any of the game

import random

from codenamecygnus.game.story import Playthrough, Story, holds

STORY = Story()


def test_conditions_compare_as_the_story_writes_them():
    v = {'Diplomacy': 2, 'event.m1e2_serum': 1}
    assert holds('Diplomacy>=0', v) and holds('Diplomacy>1', v) and not holds('Diplomacy<=0', v)
    assert holds('event.m1e2_serum==1', v) and not holds('event.m1e2_serum==0', v)
    assert holds('Openness<1', v)


def test_a_variable_never_set_counts_as_0():
    assert holds('event.m1e1_cardsWin==0', {}) and not holds('event.m1e1_cardsWin==1', {})


def test_a_condition_that_cannot_be_read_is_false():
    assert not holds('oops', {}) and not holds('a=>1', {})


def test_a_states_media_are_told_apart_by_name():
    s = STORY.state('016F_contactMark')
    assert s.voice == '016F_contactMark.m4a'
    assert s.background == 'back_bar.m4a'
    assert s.decision == 'decision_single.m4a'


def test_the_scene_heading_comes_from_the_script():
    assert STORY.state('001introOpen').heading == 'CASINO - BACK ROOM - CARD TABLE'
    assert STORY.state('016F_contactMark').heading is None


def test_a_condition_decides_where_a_state_goes():
    splitter = '009introInterruptionSplitter'
    assert STORY.next_state(splitter, {'event.m1e1_cardsWin': 1}) == '010introInterruptionWinPrompt'
    assert STORY.next_state(splitter, {}) == '010introInterruptionLosePrompt'


def test_a_choice_state_does_not_go_on_by_itself():
    assert STORY.next_state('002introOpenPrompt', {}) is None
    assert [c.text for c in STORY.choices('002introOpenPrompt')] == ['FOCUSED', 'IMPULSIVE']


def test_hidden_choices_can_be_said_but_are_not_offered():
    offered = [c.text for c in STORY.choices('045prizePrompt_m1e8')]
    every = [c.text for c in STORY.choices('045prizePrompt_m1e8', include_hidden=True)]
    assert 'OPEN' not in offered and 'NO' not in offered
    assert 'OPEN' in every and 'NO' in every


def test_holiday_partys_choices_time_out_after_7_seconds():
    assert STORY.timeout('009drinkPrompt_m1e8') == (7.0, '010Ctimeout_m1e8')
    assert STORY.timeout('002introOpenPrompt') is None


def test_a_choice_word_is_spoken_capitalised():
    assert [c.spoken for c in STORY.choices('012introRejectPrompt')] == ['Charismatic', 'Hostile']


def test_states_set_raise_and_lower_variables():
    run = Playthrough(STORY, STORY.episodes['1.1.1'])
    run.start()
    assert run.variables['Predictability'] == 0 and run.variables['npc_state.tomassi'] == 1
    run.enter('003introRaiseBet')               # IMPULSIVE: lowers Predictability, wins at cards
    assert run.variables['Predictability'] == -1 and run.variables['event.m1e1_cardsWin'] == 1
    run.enter('003introRaiseBet')
    assert run.variables['Predictability'] == -2


def test_a_state_can_earn_an_achievement_once():
    run = Playthrough(STORY, STORY.episodes['1.1.1'])
    run.start()
    run.enter('achievement_cardsWin')
    run.enter('achievement_cardsWin')
    assert run.earned == ['net.reactivestudios.codenamecygnus.event.m1e1_cardsWin']


def test_the_prologue_starts_at_the_card_table_and_waits_for_two_cards():
    run = Playthrough(STORY, STORY.episodes['1.1.1'])
    state = run.start()
    while not run.waiting and state is not None:
        state = run.after_voice()
    assert run.current.name == '001introOpen' and [c.text for c in run.choices()] == ['TWO CARDS']


def test_the_van_escape_leads_where_each_choice_says():
    for prompt, word, ending in (('3_AAB007matthewsEscapePrompt_m1e7', 'GRAB IT', '4_AABA002alexAthleticRefuseMatthewsEND_m1e7'),
                                 ('3_AAB007alexEscapePrompt_m1e7', 'HANG ON', '4_AABB003alexAthleticRefuseAlexEND_m1e7')):
        run = Playthrough(STORY, STORY.episodes['1.7.1'])
        run.enter(prompt)
        choice = next(c for c in run.choices() if c.text == word)
        run.choose(choice)
        assert run.after_voice().name == ending, word


def test_the_episodes_are_the_eight_of_mission_1():
    playable = STORY.playable_episodes()
    assert [e.title for e in playable] == ['Prologue', 'Art Show', "Neptune's Lair", 'Consulate',
                                           'Lazarus Awakens', "Neptune's Gift", 'Signum Cygni', 'Holiday Party']
    assert not STORY.episodes['1.8.1'].locked_at_first
    assert STORY.episodes['1.2.1'].locked_by == '1.1.1'
    assert STORY.episodes['1.2.1'].number == 2


def play(episode, rng, limit=100000):
    """Play an episode through, choosing at random; the states it passed.

    Holiday Party sends a wrong choice back to the start of the party, so a run of random
    choices there passes about 1,600 states at the median and up to 15,000 (measured
    2026-10-17, over 300 runs, every one finishing). The limit is far above that, and still
    catches a story that truly cannot end."""
    run = Playthrough(STORY, episode)
    run.start()
    passed = 0
    while not run.finished:
        passed += 1
        assert passed < limit, '%s did not finish: stuck near %s' % (episode.title, run.current.name)
        if run.waiting:
            out = run.timeout()
            if out and rng.random() < 0.2:
                run.time_out()
            else:
                run.choose(rng.choice(run.all_choices()))
        elif run.after_voice() is None and not run.finished:
            raise AssertionError('%s stopped at %s, which leads nowhere' % (episode.title, run.current.name))
    return run


def test_every_episode_always_reaches_its_end_whatever_is_chosen():
    rng = random.Random(23)
    for episode in STORY.playable_episodes():
        for _ in range(60):
            run = play(episode, rng)
            assert run.current.name == episode.end


if __name__ == '__main__':
    _quiet.run_tests(globals())
