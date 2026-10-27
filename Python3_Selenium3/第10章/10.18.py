import xml.dom.minidom
dom = xml.dom.minidom.parse('user.xml')
root = dom.documentElement
list = root.getElementsByTagName("user")
print(list[0].getAttribute("id"))
print(list[0].getElementsByTagName("password")[0].childNodes[0].nodeValue)
