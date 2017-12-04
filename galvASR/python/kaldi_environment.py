from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from contextlib import contextmanager
import logging
import os

log = logging.getLogger('galvASR')

GALVASR_ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..'))


def setup_environment():
    if os.environ.get('KALDI_ROOT') is None:
        KALDI_ROOT = os.path.join(GALVASR_ROOT, 'third_party', 'kaldi', 'kaldi')
        log.info('KALDI_ROOT environment variable not already set. Defaulting '
                 'to submodule path: %s', KALDI_ROOT)
        os.environ['KALDI_ROOT'] = KALDI_ROOT
    if os.environ.get('OPENFST_ROOT') is None:
        OPENFST_ROOT = os.path.join(GALVASR_ROOT, 'third_party', 'openfst')
        log.info('OPENFST_ROOT environment variable not already set. Defaulting '
                 'to symlink path (to Kaldi\'s install): %s', OPENFST_ROOT)
        os.environ['OPENFST_ROOT'] = OPENFST_ROOT
    if not os.path.exists(os.path.join(os.environ['KALDI_ROOT'], 'egs')):
        raise ValueError('KALDI_ROOT is not pointing to a Kaldi repo!')
    for env_variable in ('KALDI_ROOT', 'OPENFST_ROOT'):
        if not os.path.isabs(os.environ[env_variable]):
            raise ValueError('{0} is not an absolute path. Instead, {1}'.
                             format(env_variable, os.environ[env_variable]))

    # This is a modified copy-pasta of
    # $KALDI_ROOT/tools/config/common_path.sh
    os.environ['PATH'] = """\
{KALDI_ROOT}/src/bin:\
{KALDI_ROOT}/src/chainbin:\
{KALDI_ROOT}/src/featbin:\
{KALDI_ROOT}/src/fgmmbin:\
{KALDI_ROOT}/src/fstbin:\
{KALDI_ROOT}/src/gmmbin:\
{KALDI_ROOT}/src/ivectorbin:\
{KALDI_ROOT}/src/kwsbin:\
{KALDI_ROOT}/src/latbin:\
{KALDI_ROOT}/src/lmbin:\
{KALDI_ROOT}/src/nnet2bin:\
{KALDI_ROOT}/src/nnet3bin:\
{KALDI_ROOT}/src/nnetbin:\
{KALDI_ROOT}/src/online2bin:\
{KALDI_ROOT}/src/onlinebin:\
{KALDI_ROOT}/src/sgmm2bin:\
{KALDI_ROOT}/src/sgmmbin:\
{KALDI_ROOT}/src/tfrnnlmbin:\
{OPENFST_ROOT}/bin:\
{PATH}""".format(**os.environ)

    # Add utils/ to path directly for historical reasons.
    # https://github.com/kaldi-asr/kaldi/issues/2058
    # Prefer to make calls with the utils/ prefix, though.
    os.environ['PATH'] = "{KALDI_ROOT}/egs/wsj/s5/utils/:{PATH}".format(**os.environ)

    # Search for "LC_ALL" in http://kaldi-asr.org/doc/data_prep.html
    # for a discussion of the importance of this environment variable.
    os.environ['LC_ALL'] = 'C'

    # Normally the contents of cmd.sh. May want to make these
    # configurable at some point.
    os.environ['train_cmd'] = 'run.pl'
    os.environ['decode_cmd'] = 'run.pl'


@contextmanager
def kaldi_load_utils_and_steps():
    save_cwd = os.getcwd()
    steps = os.path.join(save_cwd, 'steps')
    utils = os.path.join(save_cwd, 'utils')
    path_sh = os.path.join(save_cwd, 'path.sh')
    cmd_sh = os.path.join(save_cwd, 'cmd.sh')
    # While this should catch exceptions, and clean up the symlinks,
    # there is a small chance that python will be killed (e.g., kill
    # -9) without the exit portion of this function running, so don't
    # error out if the symlink already exists.
    if not os.path.islink(steps):
        os.symlink('{KALDI_ROOT}/egs/wsj/s5/steps'.format(**os.environ), steps)
    if not os.path.islink(utils):
        os.symlink('{KALDI_ROOT}/egs/wsj/s5/utils'.format(**os.environ), utils)
    with open(path_sh, 'w+'), open(cmd_sh, 'w+'):
        # Some legacy kaldi scripts insist upon loading path.sh in the
        # current workind directory, though this is wholly unnecessary
        # since it's a precondition to calling those scripts that the
        # environment is set up correctly. setup_environment()
        # alreadys sets up the environment variables as path.sh would,
        # so we just create an empty file. Same goes for cmd.sh
        pass
    try:
        yield
    finally:
        if os.getcwd() != save_cwd:
            log.warning('You changed your working directory. Kaldi\'s steps and '
                        'utils symlinks and path.sh and cmd.sh will still be '
                        ' cleaned up, but this is generally discouraged.')
        os.remove(steps)
        os.remove(utils)
        os.remove(path_sh)
        os.remove(cmd_sh)
