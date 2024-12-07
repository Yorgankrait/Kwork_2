from django.db import models

from PIL import Image
from django.conf import settings
import os

import hashlib
import random
from functools import partial

RANDOM_STRING = "ABCEHKMPTX0123456789"
ITEM_RANDOM_CHAR = 6
RANDOM_STRING_HASH = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
ITEM_RANDOM_CHAR_HASH = 5
ITEM_RANDOM_CHAR_HASH_EDIT = 10

def hash_file(file, block_size=65536):
    hasher = hashlib.md5()
    for buf in iter(partial(file.read, block_size), b''):
        hasher.update(buf)
    return hasher.hexdigest()


def upload_to(instance, filename):
    """
    :type instance: dolphin.models.File
    """
    instance.file_img.open()
    filename_base, filename_ext = os.path.splitext(filename)
    return "upload_file/{0}{1}".format(hash_file(instance.file_img), filename_ext)

def getRandomHash(count_random):
    strRandom = ""
    for i in range(count_random):
        strRandom = strRandom + random.choice(RANDOM_STRING)
        #obj_search = Space.objects.all().filter(logo=RANDOM_STRING).first()
        #if obj_search!=None:
        #    while obj_search!=None:
        #        count_random = count_random + 1
        #        strRandom = getRandom(count_random)
        #        obj_search = Space.objects.all().filter(logo=RANDOM_STRING).first()
    return strRandom

class InData(models.Model):
    GUID = models.CharField(max_length=255, blank=True, null=True)
    hash = models.CharField(max_length=255, default=getRandomHash(5), blank=True, null=True)
    json_in = models.TextField(null=True, blank=True)
    its_parce = models.BooleanField(default=False)

    created_at = models.DateTimeField(verbose_name='created date', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='updated date', auto_now=True)


    def __str__(self):
        return self.GUID.__str__()

    class Meta:
        verbose_name = 'InData'
        verbose_name_plural = 'InData'

class Wh(models.Model):

    url = models.TextField(null=True, blank=True)
    json_in = models.TextField(null=True, blank=True)
    its_parce = models.BooleanField(default=False)

    created_at = models.DateTimeField(verbose_name='created date', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='updated date', auto_now=True)


    class Meta:
        verbose_name = 'Wh'
        verbose_name_plural = 'Wh'

class Office(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Manager(models.Model):
    first_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    office = models.ForeignKey(Office, on_delete=models.CASCADE, blank=True, null=True)  # Связь с Office

    def __str__(self):
        return self.first_name

class Order(models.Model):
    number = models.CharField(max_length=20)
    office = models.ForeignKey(Office, on_delete=models.CASCADE)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    #products = models.ManyToManyField(Product, related_name='orders')
    #supplements = models.ManyToManyField(Supplement, related_name='orders')
    #services = models.ManyToManyField(Service, related_name='orders')

    def __str__(self):
        return self.number

class Product(models.Model):
    identifier = models.IntegerField()
    system = models.CharField(max_length=100)
    series = models.CharField(max_length=100)
    width = models.IntegerField()
    height = models.IntegerField()
    base_color = models.CharField(max_length=100)
    inner_color = models.CharField(max_length=100)
    outer_color = models.CharField(max_length=100)
    handles = models.CharField(max_length=100)
    quantity = models.IntegerField()
    image = models.TextField()  # Строка для хранения base64 изображения

    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.system} - {self.series}"

class Option(models.Model):
    name = models.CharField(max_length=255)
    #quantity = models.IntegerField()
    #cost = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

class UpSale(models.Model):
    name = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name