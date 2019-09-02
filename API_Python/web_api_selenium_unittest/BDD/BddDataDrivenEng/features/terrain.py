# encoding=utf-8
from lettuce import *
import logging


# initialize log
logging.basicConfig(
    level=logging.DEBUG,
    format=' % (asctime)s % (filename)s[line:%(lineno)d] % (levelname)s % (message)s',
    datefmt=' % a, % Y-% m-% d % H: % M: % S',
    filename=r'D:\Pycharm\test_xiaozhan\lxz_python\BDD\BddDataDrivenEng\BddDataDrivenEng.log',
    filemode='w'
)
# run before all
@before.all
def say_hello():
    logging.info('Lettuce will start to run tests right now....')
    print('Lettuce will start to run tests right now')

# run before each scenario
@before.each_scenario
def setup_some_scenario(scenario):
    print('Begin to execute scenario name:' + scenario.name)
    logging.info('Begin to execute scenario name:' + scenario.name)


# run before each step
'''@before.each_step
def setup_some_step(step):
    run = 'running step %r, defined at %s' % (
        step.sentence,  # 执行的步骤
        step.defined_a.file  # 步骤定义在哪个文件
    )
    # 将每个场景的每一步信息打印到日志
    logging.info(run)
'''
# 每个step执行后执行
@after.each_step
def teardown_some_step(step):
    logging.info("End of the '%s'" % step.sentence)

# 在每个scenario后执行
@after.each_scenario
def teardown_some_scenario(scenario):
    print('finished, scenario name:' + scenario.name)
    logging.info('finished, scenario name:' + scenario.name)

# 在所有场景结束后执行
@after.all
def say_goodbye(total):
    result = ("Congratulations, %d of %d scenarios passed!" % (
        total.scenarios_ran,
        total.scenarios_passed
    ))
    print(result)
    logging.info(result)
    print('--------Goodbye!-------')
