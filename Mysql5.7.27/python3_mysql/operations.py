""" this is for creating database and tables"""

drop_database = """ drop database if exists `test_result`"""
create_database = """ 
                      create database `test_result`  
                  """

# create table
# drop_table = """DROP TABLE IF EXISTS ia_result"""   # this line is not useful
create_table = """
               CREATE TABLE IF NOT EXISTS `ia_result` (
              `id` int(12),
              `name` VARCHAR (20),
              `status` varchar(255),
              `arch` char(20),
              `date` datetime,   # you can use date type, and you should use current_date when inserting data
              PRIMARY KEY (`id`)
              )ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=gbk"""

# insert data
insert_data = """
                     INSERT INTO `ia_result` (id,name,status,arch,date)VALUES 
                     ('1', 'ICMP-1.1', 'Passed', 'IA', NOW()),    # if the type is datetime,you can use NOW()
                     ('2', 'ICMP-1.2', 'FAIL', 'IA', NOW()),     # CURRENT_DATE 
                     ('3', 'ICMP-1.3', 'FAIL', 'IA', NOW())
               """

# update data
update_data = """
                     # UPDATE `ia_result`  SET status='Passed' WHERE name='ICMP-1.2' 
                     UPDATE `ia_result`  SET status='Passed' 
               """

