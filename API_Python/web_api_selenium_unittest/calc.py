#!/usr/bin/python
# encoding=utf-8

#import tempConvert

#print("32摄氏度 = %.2f华氏度" % tempConvert.c2f(32))
#print("99华氏度 = %.2f摄氏度" % tempConvert.f2c(99))


######### another method to import #####

#from tempConvert import c2f,f2c

#print("32摄氏度 = %.2f华氏度" % c2f(32))
#print("99华氏度 = %.2f摄氏度" % f2c(99))

######### another method to import module ######

#import package.tempConvert as tc
#import package.printer as p
import package.tempConvert

print("32摄氏度 = %.2f华氏度" % package.tempConvert.c2f(32))
print("99华氏度 = %.2f摄氏度" % package.tempConvert.f2c(99))

p.func("hello")
