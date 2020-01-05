def demo(*args, **kwargs):
    print(args)     # (1, 2, 3)
    print(kwargs)   # {'name': '小明', 'age': 18}


gl_nums = [1, 2, 3]   # gl_nums = (1, 2, 3)
gl_dict = {"name": "小明", "age": 18}
demo(*gl_nums, **gl_dict)
