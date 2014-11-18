# encoding=utf-8

import unittest
from subprocess import Popen, PIPE
import os
import tempfile
import shutil
import sys
import game_engine.arena
import json

EXIT_SUCCESS = 0
PYTHON = 'python'
PY = ".py"
BOTS = 'bots'
ARENA_PY = 'arena.py'
EXC_PY = 'exc.py'
GAME_ENGINE_FOLDER = '.'

class ArenaProgramTestCase(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        # create the match temp dir
        self.match_dir = tempfile.mkdtemp()
        self.bots_dir = os.path.join(self.match_dir, BOTS)
        shutil.copy(os.path.join(GAME_ENGINE_FOLDER, ARENA_PY), self.match_dir)
        shutil.copy(os.path.join(GAME_ENGINE_FOLDER, EXC_PY), self.match_dir)
        os.mkdir(self.bots_dir)
        open(os.path.join(self.bots_dir, '__init__.py'), 'w').close()

    def tearDown(self):
        shutil.rmtree(self.match_dir)
        unittest.TestCase.tearDown(self)

    def test_empty_arguments_fails(self):
        ret, _, __ = self._run_arena([])
        self.assertNotEqual(ret, EXIT_SUCCESS)

    def test_only_one_bot_fails(self):
        bot_file = self._generate_bot_script("bot1", self._get_return_None_bot_code())
        ret, _, __ = self._run_arena([bot_file])
        self.assertNotEqual(ret, EXIT_SUCCESS)

    def test_return_None_bot_draw(self):
        self._test_bots_draw(self._get_return_None_bot_code)

    def test_only_moving_bots_draw(self):
        self._test_bots_draw(self._get_only_moving_bot_code)

    def test_shoot_in_the_air_bots_draw(self):
        self._test_bots_draw(self._get_shoot_in_the_air_bot_code)

    def _test_bots_draw(self, get_bot_code):
        bot1_file = self._generate_bot_script("bot1", get_bot_code())
        bot2_file = self._generate_bot_script("bot2", get_bot_code())
        ret, output, err = self._run_arena([bot1_file, bot2_file])
        self.assertEqual(ret, EXIT_SUCCESS)
        #WARNING: make sure we are the only ones to access arena.py code,
        #and the input data is validated. We cannot use json inside the sandbox
        result_dict = eval(output)
        match_result_dict =  result_dict['actions'][-1]
        self.assertEqual(match_result_dict[game_engine.arena.ACTION], game_engine.arena.RESULT)
        self.assertIsNone(match_result_dict[game_engine.arena.WINNER])
        self.assertIsNone(match_result_dict[game_engine.arena.LOSER])
        self.assertTrue(match_result_dict[game_engine.arena.DRAW])


    def _run_arena(self, args):
        arena_script = os.path.join(self.match_dir, ARENA_PY)
        proc = Popen([PYTHON, arena_script] + args, cwd=self.match_dir, stdout=PIPE)
        proc_out, proc_err = proc.communicate()
        return proc.returncode, proc_out, proc_err

    def _generate_bot_script(self, bot_name, bot_code):
        bot_name_py = bot_name + PY
        bot_path = os.path.join(self.bots_dir, bot_name_py)
        with open(bot_path, 'w') as bot_file:
            bot_file.write(bot_code)
        return os.path.join(BOTS, bot_name_py)

    def _get_bot_code(self, evaluate_turn_code):
        return '''
class Bot(object):
    def evaluate_turn(self, feedback, life):%s
''' % evaluate_turn_code

    def _get_return_None_bot_code(self):
        return self._get_bot_code('''
        return None
''')

    def _get_only_moving_bot_code(self):
        return self._get_bot_code('''
        return {'ACTION' : 'MOVE', 'WHERE': 1}
''')

    #We don't use minimum values, because bots kill themselves
    def _get_shoot_in_the_air_bot_code(self):
        return self._get_bot_code('''
        return {'ACTION' : 'SHOOT', 'VEL': 15, 'ANGLE': 15}
''')

if __name__ == '__main__':
    unittest.main()
