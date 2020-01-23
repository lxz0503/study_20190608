from django.shortcuts import render
from product.models import Product

# Create your views here.


def product_manage(request):
    username = request.session.get('user', '')
    product_list = Product.objects.all()   # get all data from database and store them into a list

    # you can also define a dictionary as below
    # or you can write sql to update your database
    # product_list = [
    #                 {'id': 1, 'product_name': 'baidu', 'product_desc': 'search', 'product_owner': 'liyanhong', 'create_time': '1999'},
    #                 {'id': 2, 'product_name': 'taobao', 'product_desc': 'shopping', 'product_owner': 'mayun','create_time': '1998'},
    #                 {'id': 3, 'product_name': 'sohu', 'product_desc': 'general', 'product_owner': 'zhang','create_time': '1997'},
    #                 ]
    print('aaaaaaaaaa')
    return render(request, 'product_manage.html', {'user': username, 'products': product_list})


