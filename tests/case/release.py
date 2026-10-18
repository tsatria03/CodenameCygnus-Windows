"""compiler.py and releaser.py, by what they work out: nothing is built, zipped into the
repository, committed, tagged or uploaded."""
import _quiet  # noqa: F401  first, before any of the game

import os
import tempfile
import types
import zipfile

import compiler
import releaser

LOG = """unrelease:
First change.
Second change.

26.10.14-1:
An old change.
"""


def flags(**given):
    base = dict(embed=False, onefile=False, no_game=False, console=False, clean=False,
                dry_run=False, test=False)
    base.update(given)
    return types.SimpleNamespace(**base)


def test_the_changelog_is_read_by_its_headings():
    blocks = compiler.parse_changelog(LOG)
    assert [b[0] for b in blocks] == ['unrelease:', '26.10.14-1:']
    assert compiler.unreleased_lines(LOG) == ['First change.', 'Second change.']
    assert compiler.render_changelog(blocks) == LOG


def test_a_shipped_changelog_drops_only_an_empty_unrelease():
    empty = 'unrelease:\n\n26.10.14-1:\nAn old change.\n'
    assert compiler.without_unrelease(empty) == '26.10.14-1:\nAn old change.\n'
    assert compiler.without_unrelease(LOG) == LOG


def test_filing_moves_the_unreleased_lines_under_the_version():
    text, changed, _notes = releaser.plan_changelog(LOG, '26.10.18-1')
    assert changed
    assert text.startswith('unrelease:\n\n26.10.18-1:\nFirst change.\nSecond change.\n\n26.10.14-1:')
    assert releaser.release_notes(text, '26.10.18-1') == 'First change.\nSecond change.'


def test_filing_puts_back_a_missing_unrelease():
    text, changed, notes = releaser.plan_changelog('26.10.14-1:\nOld.\n', '26.10.18-1')
    assert changed and text.startswith('unrelease:') and 'put back' in notes[0]


def test_the_version_counts_the_days_releases_from_the_tags():
    assert releaser.next_version([], '26.10.18') == '26.10.18-1'
    assert releaser.next_version(['V26.10.18-1', 'V26.10.18-2', 'V26.10.17-5', 'mission-1'],
                                 '26.10.18') == '26.10.18-3'
    assert releaser.tag_for('26.10.18-1') == 'V26.10.18-1'
    assert releaser.title_for('26.10.18-1') == 'CodenameCygnus V26.10.18-1'
    assert releaser.zip_name('26.10.18-1') == 'CodenameCygnus-Win-26.10.18-1.zip'


def test_a_folder_build_is_windowed_with_everything_it_needs():
    cmd = compiler.command(flags())
    assert cmd[-1] == 'CodenameCygnus.py' and '--windowed' in cmd and '--onefile' not in cmd
    joined = ' '.join(cmd)
    assert 'nvdaControllerClient64.dll' in joined and '--collect-all prism' in joined
    assert 'pocketsphinx/model' in joined and 'libportaudio64bit.dll' in joined
    assert compiler.LICENSES_STAGE + os.pathsep + 'licenses' in cmd
    assert compiler.GAME_STAGE + os.pathsep + 'game' not in cmd


def test_the_single_exe_carries_the_game_inside_and_the_console_build_a_console():
    cmd = compiler.command(flags(embed=True), embed_game=True)
    assert '--onefile' in cmd and compiler.GAME_STAGE + os.pathsep + 'game' in cmd
    assert cmd[cmd.index('--distpath') + 1] == compiler.output_dir()
    assert '--windowed' not in compiler.command(flags(console=True))
    assert '--clean' in compiler.command(flags(clean=True))


def test_the_build_carries_only_the_game_data_it_reads():
    src = compiler.game_source()
    names = compiler.game_files(src)
    text = sorted(n for n in names if n.endswith('.json'))
    assert text == [os.path.join('data', 'text', n)
                    for n in ('missions.json', 'resources.json', 'states.json')]
    info = compiler.PACK_INFO in names                  # once tools/build_pack.py has run
    assert len(names) == 11 + info and compiler.missing_game_files(src) == []
    assert compiler.data_summary(names) == (
        "12 files: 3 story files, 8 menu sounds and the mission pack's fingerprint" if info
        else '11 files: 3 story files and 8 menu sounds')
    assert not any('missions' + os.sep in n or 'descriptor' in n for n in names)


def test_every_license_is_found():
    found = compiler.license_files()
    assert all(src and os.path.isfile(src) for _rel, src in found), \
        [rel for rel, src in found if not src or not os.path.isfile(src)]
    folders = {rel.split(os.sep)[0] for rel, _src in found}
    assert folders == {'nvda-controller-client', 'prism', 'pocketsphinx', 'sounddevice', 'cffi', 'cryptography', 'pygame'}


def test_a_test_run_is_judged_by_its_log():
    good = 'x INFO cygnus game data: C:\\g\\game\ny INFO cygnus Codename Cygnus closed\n'
    assert compiler.judge_test(0, good, '') == []
    assert any('no log' in p for p in compiler.judge_test(0, '', ''))
    assert any('crash report' in p for p in compiler.judge_test(1, good, 'Traceback'))
    assert any('still running' in p for p in compiler.judge_test(None, good, ''))


def test_the_menus_offer_the_plans_choices():
    assert [f for _t, f in compiler.MENU] == [
        [], ['--test'], ['--embed'], ['--embed', '--test'], ['--clean'], ['--console'],
        ['--onefile'], ['--no-game'], ['--dry-run']]
    assert len(releaser.MENU) == 9 and releaser.MENU[-1][0].startswith('Upload the mission pack')


def test_the_zip_extracts_to_one_folder_and_only_for_its_version():
    build = tempfile.mkdtemp(dir=_quiet.FOLDER)
    os.makedirs(os.path.join(build, 'docks'))
    for name, text in (('VERSION', '26.10.18-1\n'), (os.path.join('docks', 'readme.txt'), 'hi')):
        with open(os.path.join(build, name), 'w', encoding='utf-8') as fh:
            fh.write(text)
    assert releaser.built_version(build) == '26.10.18-1'
    target = os.path.join(tempfile.mkdtemp(dir=_quiet.FOLDER), 'out.zip')
    real = releaser.zip_path
    releaser.zip_path = lambda version: target
    try:
        releaser.package(build, '26.10.18-1')
    finally:
        releaser.zip_path = real
    with zipfile.ZipFile(target) as box:
        assert sorted(box.namelist()) == ['CodenameCygnus-Windows/VERSION',
                                          'CodenameCygnus-Windows/docks/readme.txt']


if __name__ == '__main__':
    _quiet.run_tests(globals())
