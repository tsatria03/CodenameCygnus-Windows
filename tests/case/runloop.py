"""The timer loop: once, repeating, cancelled, in order, held and resumed."""
import _quiet  # noqa: F401  first, before any of the game

from codenamecygnus.platform import runloop
from codenamecygnus.platform.runloop import RunLoop


class Clock:
    """A clock the test moves by hand."""

    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def make():
    clock = Clock()
    runloop.clock = clock
    return RunLoop(), clock


def test_a_call_runs_once_when_due():
    loop, clock = make()
    ran = []
    loop.after(2.0, ran.append, 'x')
    clock.now += 1.9
    loop.pump()
    assert ran == []
    clock.now += 0.1
    loop.pump()
    loop.pump()
    assert ran == ['x']


def test_calls_run_in_the_order_they_fall_due():
    loop, clock = make()
    ran = []
    loop.after(3.0, ran.append, 'late')
    loop.after(1.0, ran.append, 'early')
    loop.after(1.0, ran.append, 'early, scheduled second')
    clock.now += 5
    loop.pump()
    assert ran == ['early', 'early, scheduled second', 'late'], ran


def test_a_repeating_call_skips_missed_beats():
    loop, clock = make()
    ran = []
    loop.every(1.0, ran.append, 'tick')
    clock.now += 1.0
    loop.pump()
    assert ran == ['tick']
    clock.now += 5.5                        # a long stall: one call, not five
    loop.pump()
    assert ran == ['tick', 'tick']
    clock.now += 1.0
    loop.pump()
    assert ran == ['tick', 'tick', 'tick']


def test_a_cancelled_call_never_runs():
    loop, clock = make()
    ran = []
    call = loop.after(1.0, ran.append, 'x')
    call.cancel()
    clock.now += 2
    loop.pump()
    assert ran == [] and not call.active


def test_cancelling_a_repeating_call_from_inside_it_stops_it():
    loop, clock = make()
    ran = []
    holder = {}

    def tick():
        ran.append(1)
        holder['call'].cancel()
    holder['call'] = loop.every(1.0, tick)
    for _ in range(3):
        clock.now += 1
        loop.pump()
    assert ran == [1]


def test_hold_stops_the_clock_and_resume_keeps_the_time_left():
    loop, clock = make()
    ran = []
    call = loop.after(7.0, ran.append, 'timed out')
    clock.now += 3.0
    loop.hold()
    clock.now += 100.0                      # paused for a long time
    loop.pump()
    assert ran == []
    assert abs(loop.remaining(call) - 4.0) < 1e-9, loop.remaining(call)
    loop.resume()
    clock.now += 3.9
    loop.pump()
    assert ran == []
    clock.now += 0.1
    loop.pump()
    assert ran == ['timed out']


def test_an_error_in_a_call_is_logged_and_the_loop_carries_on():
    loop, clock = make()
    ran = []

    def broken():
        raise ValueError('boom')
    loop.after(1.0, broken)
    loop.after(1.0, ran.append, 'next')
    clock.now += 1
    loop.pump()
    assert ran == ['next']


def test_a_repeating_call_needs_an_interval():
    loop, _clock = make()
    try:
        loop.every(0, lambda: None)
    except ValueError:
        return
    raise AssertionError('an interval of 0 was accepted')


if __name__ == '__main__':
    _quiet.run_tests(globals())
