var i1 = document.getElementById("i1");
i1.onfocus = function() {     //获得焦点后
    i1.value = " ";  //clear 输入框
}

//失去焦点后，表示鼠标点击其他地方
i1.onblur= function() {
    if(!i1.value.trim()) {
        i1.value = "手机";    //必须把此文件重新另存为utf-8格式才能显示中文
    }
}