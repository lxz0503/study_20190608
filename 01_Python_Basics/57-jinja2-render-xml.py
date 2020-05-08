#!/usr/bin/env python3
# coding=utf-8
import os
import jinja2
import configparser

def my_render(tpl_path, **kwargs):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(loader=jinja2.FileSystemLoader(path or './')).get_template(filename).render(**kwargs)


NAMES = ['server_a_host','server_a_port',
         'server_b_host','server_b_port',
         'server_c_host','server_c_port']

def parser_vars_into_globals(filename):
    parser = configparser.ConfigParser()
    parser.read(filename)
    print(globals())  # this is a dict

    for name in NAMES:
        globals()[name] = parser.get('DEFAULT', name)
    print(globals())  # {'server_a_host': '1.1.1.1', 'server_a_port': '10', 'server_b_host': '2.1.1.1', 'server_b_port': '20', 'server_c_host': '3.1.1.1', 'server_c_port': '30'}


def test_xml():
    parser_vars_into_globals('base.cfg')
    with open('service1.xml', 'w') as f:
        f.write(my_render('service1_template.xml', **globals()))

    with open('service2.xml', 'w') as f:
        f.write(my_render('service2_template.xml', **globals()))

if __name__ == '__main__':
    test_xml()
