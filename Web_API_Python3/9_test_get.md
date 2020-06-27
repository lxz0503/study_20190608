title: python接口测试教程（9）——  测试get方法
author:
  name: 乙醇
  url: http://itest.info
output: test_get.html
controls: true
theme: sudodoki/reveal-cleaver-theme
--

# 测试jenkins get接口
## 乙醇
2015年1月18日

--
## boss的任务

使用unittest + requrests来测试jenkins的get接口 

--

## 哪个接口

获取所有job的名称

```
http://localhost:8080/jenkins/api/json?tree=jobs[name]
```

--

## 序列化与反序列化

在本课里，序列化和反序列化可以认为是将json和python的dict互转

* 序列化: python dict -> json
* 反序列化: json -> python dict 
--

## json与dict互转实例

``` python
import json
# 序列化
d = {'k': 'v'}
j = json.dumps(d)

# 反序列化
print json.loads(j)
```
--

### demo

--

## 思考题

如何测试开启了鉴权的jenkins get接口

--

## 下一集
### 使用unittest测试jenkins的get接口

