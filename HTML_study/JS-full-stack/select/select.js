 let data = {1:["chaoyang","haidian","shunyi"], 2:["pudong","yangpu","xuhui"]};  //js中的object，类似于字典
 let s1 = document.getElementById("s1");
 s1.onchange = function() {
     console.log(this .value);      //取到哪一个市
     var areas = data[this.value];   //取到对应市的区
     var s2 = document.getElementById("s2"); //找到对应的区
     s2.innerText = "";    //清空之前的内容
     for(let i=0;i<areas.length;i++) {
         var optEle = document.createElement("option");  //创建标签option
         optEle.innerText = areas[i]; //给标签赋值
         s2.appendChild(optEle);      //添加标签到某个位置
     }
 }