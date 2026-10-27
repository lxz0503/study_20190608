1 安装vscode,下一步---遇到框就勾选
左侧  Extentions 安装插件
安装插件： open in browser, beautify

vscode写好的代码需要 ctrl+s 保存
快捷键；
一个！就能生成html的骨架
直接敲标签名就能生成标签
shift + alt + A   块注释
shift + alt + F   代码格式化
ctrl + k + 0  代码收起
ctrl + k + j  代码展开
alt + B 直接打开写好的html文件
============================================
我的vscode工程目录创建在 C:\Users\xli3\study\vscode
必须先创建这个目录，然后才能敲代码
VSCODE如何一下子写好HTML5的框架代码：
创建一个后缀为html的文件，
在第一行小写输入!  ---然后回车即可---这是家里MAC上的操作---可能是版本的区别
windows版本估计比较新
我的windows电脑上操作如下：
首行输入html:5 然后回车即可
https://blog.csdn.net/littlesun_lzy/article/details/125835376
xiaozhan：其实上面的自动生成HTML代码的操作，在pycharm上一直有
=========================================================
Vscode运行js代码---vscode因为直接安装了node.js，所以方便了很多
在terminal中，进到代码目录，直接敲 node 文件名.js ----这种比较推荐
目前直接在html中插入js文件也可以---参考我的1.js---我只是在console中输出一个打印--所以需要打开console
之前一直没打开，所以没看到结果---害的我伤脑筋 还购买了其它课程 xiaozhan
------------------------------------
参考我的框架代码： test1.html
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>test1</title>
    <script src="../xiaozhan_javascript/test1.js"></script>  // 在头部引入js文件
</head>
<body>
    <script>test1()</script>   // 直接调用test1.js里面的test1()函数
</body>

===============================================
vscode调试HTML的一些插件
http://www.360doc.com/content/22/0107/21/33911811_1012319127.shtml

==========================================
JS由3部分组成：
ES---语法规则
DOM----处理网页内容的方法和接口
BOM---与浏览器进行交互的方法和接口

ES6里面定义变量 用 let
let是用于替代var来声明变量（var是ES6之前用来声明变量的关键词）
const是用来声明常量的（var，let声明变量时，变量一旦初始化之后，还可以重新赋值，
const声明常量，一旦初始化，就不能重新赋值了，否则会报错）


isNaN 检测一个指是否是非有效数字，如果不是有效数字--返回True
如果是有效数字----返回False
isNan([val]) ---里面的中括号的用法--相当于一个占位符--提示要传入一个值

Number()方法把里面的其它类型值转化为数字类型:
Number([val])
在使用isNaN进行检测的时候，先调用Number()方法把里面的其它类型值转化为数字类型，如下：
Number('10') = 10  ---是一个数字---所以下面的返回False
console.log(isNaN('10')) ----False
Number('AA') = NaN ---- 不是有效数字--所以isNaN('AA') ---返回True
console.log(Number('12.5px')) ----NaN
console.log(Number('12.5')) ---12.5
console.log(Number('')) --- 空字符串---返回值为0
console.log(Number(true)) ---- 返回1
console.log(Number(false)) ----返回0

console.log(isNaN(false)) ----返回False ---因为Number(false)=0
console.log(Number(null)) ----返回0
console.log(Number(undefined)) --- 返回NaN

[].toString()  --- 返回空字符串 "" --Number("")--返回0
[12].toString() ----返回 "12" ---Number("12")---返回12
[12,23].toString()----返回"12,23" --NaN
----------------------------------------
把其它类型值转化为数值类型---从左到右一次查找有效数字，直到遇到非数字，就停止
方法有如下三种函数：
let  str = '12.5px';
console.log(Number(str))  ---NaN  因为出现了非有效的数字px
console.log(parseFloat(str)) ----返回12.5
console.log(parseInt(str)) -----返回12
---------------------------------------

视频 15 String字符串数据类型
引用数据类型包括：object（数组  对象 正则）  function
symbol---唯一值
所有用单引号 双引号 反引号(ES6的语法) 括起来的都是字符串
# 把其它类型转化为字符串的规则
(val).toString()     拼接字符串即+
普通对象.toString() ----得到的结果就是  '普通对象' --就是加了一层单引号
console.log('10'-10)  --- 结果为0
console.log('10px'-10) ----NaN
console.log('10'+10) ----'1010'   就是字符串拼接
10+null+true+undefined  ---- null为0，true为1，undefined为NaN---结果就是NaN
10+null+true+undefined + [] ---[]是空字符串---所以结果为 ‘NaN'
注意： 空数组[]变为数字，先要变成空字符串
[12] ---变为数字先转化为 字符串 '12'--- 10 + [12] --结果为'1012'
+ 加号 在JS中的功能除了相加，就是字符串拼接，只要遇到字符串--就是走字符串拼接功能

===========================================
视频16 布尔 Boolean数据类型
把其它类型值转化为布尔值规则：
只有0  NaN  null '' undefined 5个值转为false，其余全部是true
方法如下：
Boolean([val])
Boolean(0)    Boolean('')   Boolean(null) Boolean(NaN)   Boolean(undefined)

Boolean(!1) --- 感叹号表示取反---所以里面为0---结果为false

if(val) --如果里面只有一个值--就要先把这个值转为bool值--然后判断真假
if(1) { console.log('aa')}   --- 1永远为true
if(0)  ----0 为false
if('3px'+3) ---里面是字符串'3px3'--转化为bool值是true
if('3px'-3)----里面结果是NaN---转化为bool值是false
=========================================================

视频17  null和undefined类型
null--意料之中
一般使用null作为初始的空值， 而不是用0或者其它空字符串--因为会占用内存空间
一般是开始定义变量,但是不知道它的值，  let a = null   null不需要存储空间
经过后期赋值操作  最后 a = 10 或者其它数

undefined 意料之外
let num;   创建一个变量  但是没有赋值---默认值就是undefined

==============================================================

视频18  对象数据类型
普通对象：{key:value，key;value,.....}  感觉就是字典类型---默认key都是字符串类型--所以不用加单双引号
let person = {
    name: 'sam',
    age: 40,
    hight: '170cm'
}
获取属性名对应的value：  对象.属性名 ---console.log(person.name)
console.log(person['name'])
delete person['name']   真删除属性
person['name'] = null   假删除  设置为null

=======================================

视频19 特殊对象--数组的数据结构
在w3school上可以学习基本语法：
https://www.w3school.com.cn/jsref/jsref_obj_array.asp

let cars = ["Tesla", "Volvo", "BMW"]
数组索引从零开始：数组中的第一个元素是 0，第二个元素是 1
car.length  --- 返回数组长度
cars[0] --取第一个值
============================================
视频 20   数据类型的区别 --堆栈底层机制
--------------------------------------面试题
let a = 12;
let b = a;
b = 13;
console.log(a)   ---这里是12

let n = {
    name: 'zhufeng'
}

let m = n;
m.name='beijing';
console.log(n.name)  ---这里是beijing
---------------------------------------
继续视频20---参考截图
浏览器执行JS代码分如下几步：
1.从电脑中分配一块内存--用来执行代码--即栈内存
2.浏览器分配一个主线程自上而下执行JS代码

栈内存里面分为：
变量存储空间          值存储空间

举例： let a = 12  其实在系统里经过了3步：
1.创建变量a，放到当前的栈内存的变量存储空间
2.创建一个值12，放到值存储空间----只适用于简单的数值存储，复杂数据结构不是如此,例如数组或者对象类型
3.=赋值，让变量a和值12联系起来

----------------------------------堆内存------
存储对象数据类型时候---即键值对的时候用  xiaozhan  分析下面的流程 明白底层原理
对象数据类型里面有多个键值对--即多个值
复杂值类型--引用类型的存储--分为3步
1.分配内存，用来存储引用类型，这是堆内存  heap --内存有16进制机制 假设堆内存地址为0xAAAFFFF0000
2.把对象中的键值对依次存储到堆内存中,也存储length属性
 同时把堆内存地址存储到栈内存的值存储空间
    ---注意栈内存 值存储空间存储的是堆内存地址
    ----- 存储0xAAAFFFF0000
3.把堆内存地址和变量关联  ---n就是变量  n和0xAAAFFFF000关联
以后找变量  先找这个堆内存地址  就能找到变量n了

n ---- 堆内存的地址--里面存储 name:'zhufeng'
然后m来了，m和n同时指向了一个堆内存地址
然后给m.name赋值 就直接修改了这块堆内存下面的键值对---这时候n还是指向这块堆内存的
所以就相当于n.name也发生了变化

总结： 基本数据类型--按值操作--也叫值类型
引用数据类型---按堆内存地址操作----也叫按引用地址操作
----------------------------------------------------------------------
视频21 堆栈内存 练习  必须掌握  建议画图来加强熟练程度  参考vscode的代码 3.js
let n = [10,20]
let m = n
let x = m;
m[0]=100
x=[30,40]  ----这里要创建新的堆内存 但是不用创建变量x
x[0]=200
m=x  --这时候m指向了x，不和n一起了
m[1]=300
n[2]=400 ---n里面没有index 2，所以这是新增加了一个值
console.log(n,m,x)
===================================================
栈内存的作用： 存储变量，存储基本类型值，执行代码
JS代码赋值的特点是关联，用等于号，而不是直接拷贝  ---xiaozhan
视频22 一道阿里面试题
let a = {
    n:1
};
let b = a;
a.x=a={     # 这里要首先理解 a=b=3  这种赋值  --其实就是先让a=3 再b=3,记住这种连等赋值方法 先从左边开始
    n:2
};
console.log(a.x)  #  undefined  看图 已经没有x这个属性
console.log(b)
-------------------------
vscode运行结果：
PS C:\Users\xli3\study\vscode\xiaozhan_javascript> node 4.js
undefined
{ n: 1, x: { n: 2 } }

分析： a.x不是创建变量，而是给一个属性赋值----a.x={n:2} ---创建新的堆内存

a和{n:2}的关联--就是在值存储空间里增加{n:2}的堆内存地址
b还是和原来的堆内存关联，但是此时里面已经添加了属性x

----------===============================================
js中的NaN是Number类型   但是却不是一个数字   奇葩
视频23  数据类型检测

typeof   返回是字符串，里面包含的是数据类型  例如'number'
instanceof  检测当前实例是否属于某个类
constructor
Object.prototype.toString.call() ----检测数据类型最好的方法

----------------------
基于typeof无法检测出当前值是普通对象还是数组对象，只有是对象，就返回 ‘object'

typeof null --- 返回'object'  null是空对象指针
typeof [] --- 返回 'object'
typeof typeof []  -- 返回结果如下
'string'
------------------------------------------------------------
视频24 3种常用的判断   语法和C语言类似  if-else   switch-case
let a = '5'
if (a ==5) { console.log('aaa')}   # 这里条件成立 因为字符串a先转成数字类型的5
注意： if else和switch--case语句有些区别，其中判断值是否相等，
if--else种用的是两个==， 而switch-case是用了3个等号，即需要严格相等才行

举例： 5 == ’5‘  ---返回true
      5 === ’5‘ ---返回false    三个等号是绝对相等
两个等号，即相等的运算规律是：先把两边转成相同类型，然后再比较
三个等号，绝对相等，如果两边类型不同，则不相等
=======================================================

视频25 基于CSS实现鼠标划过显示详情-----不熟悉CSS语法  暂时不研究
但是需要学习  HTML + CSS，  JS是核心
就是鼠标放在某个地方--然后会显示对应的内容---网站很常见的功能--记得美多mall里面做过

=====================================================
视频26  基于JS实现鼠标点击切换效果--就是点击一下显示 收回后不显示
还是涉及到HTML和CSS相关的知识---暂时放下，后续单独学习HTML+CSS课程

================================================================

视频27 掌握for循环
JS脚本学习网站    https://www.w3school.com.cn/js/index.asp

for循环用法和C语言一样
for (i = 0; i < 5; i++) {
    console.log("数字是 " + i + "<br>");
}

JavaScript 支持不同类型的循环：

for - 多次遍历代码块
for/in - 遍历对象属性  ---参考例子7-for.js
while - 当指定条件为 true 时循环一段代码块
do/while - 当指定条件为 true 时循环一段代码块
-------------------------------------------
for in 循环：
const person = {fname:"Bill", lname:"Gates", age:25};

let text = "";
for (let x in person) {
  console.log(text += person[x]);
}
-------------------------------------------------------------
JavaScript   for of 语句循环遍历可迭代对象的值。
它允许您循环遍历可迭代的数据结构，例如数组、字符串、映射、节点列表等
const cars = ["BMW", "Volvo", "Mini"];

let text = "";
for (let x of cars) {   // 如果是let x in cars  则遍历的是数组下标
    console.log(text += x);
}

===============================================

视频28 判断逻辑的案例练习


JS代码格式化网站-----