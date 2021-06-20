import xml.dom.minidom
dom = xml.dom.minidom.parse('user.xml')
root = dom.documentElement
list = root.getElementsByTagName("user")
for l in list:
    print(l.getAttribute("id"))
    print(l.getElementsByTagName("password")[0].childNodes[0].nodeValue)
    print(l.getElementsByTagName("username")[0].childNodes[0].nodeValue)
