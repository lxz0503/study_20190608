ControlFocus("打开", "","Edit")
WinWait("[CLASS:#32770]","",5)
#上传文件ip.txt文件
ControlSetText("打开", "", "Edit1", "D:\soft\ip.txt")
Sleep(1000)
ControlClick("打开", "","Button1");
