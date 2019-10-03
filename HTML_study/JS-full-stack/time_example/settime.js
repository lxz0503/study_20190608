//对于定时器，一定要打开后记得清除
//这个例子点击开始按钮就会打开一个定时器
//所以增加了点击两次开始后，处理定时器清理的问题，否则每点击一次就打开一个新的定时器，而关掉的只是最新的
var s;    //全局定时器
//输入框
function foo() {
    var i1 = document.getElementById("i1");
    var now = new Date();
    i1.value = now.toLocaleTimeString(); //设置i1的输入框内容为当前时间
}
//开始按钮
var b1 = document.getElementById("b1");
b1.onclick = function() {
    foo();                       //点击b1这个开始按钮后，就调用foo()函数
    if (s === undefined) {     //如果全局定时器为undefined
        s = setInterval(foo,1000);   //就设置一个全局定时器
    }
}
//停止按钮
var b2 = document.getElementById("b2");
b2.onclick = function() {
    clearInterval(s);           //点击停止后，清除这个定时器，
    console.log(s);     //清除后,s依然有值
    s = undefined;     //所以这里把s设置为undefined
}

