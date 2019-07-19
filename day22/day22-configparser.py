import configparser

test_name = "IKE-1.1"
status = "PASS"
config = configparser.ConfigParser()
config.read("nightly.ini")
config.set("LTAF", "test_name", test_name)
config.set("LTAF", "status", status)
# config.set("LTAF", "function_pass", function_pass)
# config.set("LTAF", "function_fail", function_fail)
# config.set("LTAF", "spin", spin)
# config.set("LTAF", "log", log)
# config.set("LTAF", "week", nightly_date)
# config.set("LTAF", "release_name", release_name)
config.write(open('nightly.ini', "r+"))