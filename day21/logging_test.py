# import logging
#
# def main():
#     logging.basicConfig(
#         filename='app.log',
#         level=logging.DEBUG,
#         format='%(asctime)s:%(levelname)s:%(message)s'
#     )
#     logging.debug("I am written to the file")
#
#
# if __name__ == '__main__':
#     main()
#

import sys

# make a copy of original stdout route
stdout_backup = sys.stdout

# define the log file that receives your log info
log_file = open("message.log", "a")

# redirect print output to log file
sys.stdout = log_file

print("Now all print info will be written to message.log")
# any command line that you will execute
print("aaa")

log_file.close()
# restore the output to initial pattern
sys.stdout = stdout_backup

print("Now this will be presented on screen")
print("bbb")