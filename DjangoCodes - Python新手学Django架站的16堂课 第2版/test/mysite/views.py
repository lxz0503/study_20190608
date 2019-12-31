from django.shortcuts import render
import random
from django.contrib import messages
from mysite import forms
import os
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
from uuid_upload_path import uuid
import glob

def index(request):
    messages.get_messages(request)

    pics = random.sample(range(1,30),6)

    return render(request, 'index.html', locals())


def gen(request):
    messages.get_messages(request)
    backfiles = glob.glob(os.path.join(settings.BASE_DIR,'mysite/static/backimages/*.jpg'))
    if request.method=='POST':
        form = forms.GenForm(request.POST)
        saved_filename = mergepic(request.POST.get('backfile'),
                                      request.POST.get('msg'), 
                                      int(request.POST.get('font_size')),
                                      int(request.POST.get('x')),
                                      int(request.POST.get('y')))
    else:
        form = forms.GenForm(backfiles)

    return render(request, 'gen.html', locals())



def mergepic(filename, msg, font_size, x, y):
    fill = (0,0,0,255)
    image_file = Image.open(os.path.join(settings.BASE_DIR,'mysite/static/backimages/', filename))
    im_w, im_h = image_file.size 
    im0 = Image.new('RGBA', (1,1))
    dw0 = ImageDraw.Draw(im0)
    font = ImageFont.truetype(os.path.join(settings.BASE_DIR,'wt014.ttf'), font_size)
    fn_w, fn_h = dw0.textsize(msg, font=font)

    im = Image.new('RGBA', (fn_w, fn_h), (255,0,0,0))
    dw = ImageDraw.Draw(im)
    dw.text((0,0), msg, font=font, fill=fill)
    image_file.paste(im, (x, y), im)
    saved_filename = uuid()+'.jpg'
    image_file.save(os.path.join(settings.BASE_DIR,"media", saved_filename))
    return saved_filename

