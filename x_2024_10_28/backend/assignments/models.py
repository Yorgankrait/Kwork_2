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

    
# Create your models here.
class Assignment(models.Model):

    first_term = models.DecimalField(
        max_digits=5, decimal_places=2, null=False, blank=False
    )

    second_term = models.DecimalField(
        max_digits=5, decimal_places=2, null=False, blank=False
    )

    # sum should be equal to first_term + second_term
    # its value will be computed in Celery
    sum = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
class Offer(models.Model):    
    price = models.CharField(max_length=100, blank=True, null=True)
    text_small = models.TextField(blank=True, null=True)
    text_big = models.TextField(blank=True, null=True)
    price_crossed = models.CharField(max_length=100, blank=True, null=True)
    term = models.CharField(max_length=255, blank=True, null=True)
    price_izd = models.CharField(max_length=100, blank=True, null=True)
    price_kompl = models.CharField(max_length=100, blank=True, null=True)
    price_service = models.CharField(max_length=100, blank=True, null=True)
    manager = models.CharField(max_length=255, blank=True, null=True)
    offer_hash = models.CharField(max_length=100, blank=True, null=True)    
    is_active = models.BooleanField(default=True, verbose_name='Актуальность')    
    updated_at = models.DateTimeField(verbose_name='updated date', auto_now=True)

    def __str__(self):
        return self.offer_hash.__str__() 
        
    class Meta:
        verbose_name = 'Offer'
        verbose_name_plural = 'Offer'
        
class Izd(models.Model):    
    offer = models.ForeignKey(Offer, related_name='izds', on_delete=models.CASCADE)
    img = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    har = models.CharField(max_length=100, blank=True, null=True)
    cout = models.CharField(max_length=100, blank=True, null=True)
    price = models.CharField(max_length=100, blank=True, null=True)    
    updated_at = models.DateTimeField(verbose_name='updated date', auto_now=True)

    def __str__(self):
        return self.name.__str__() 
        
    class Meta:
        verbose_name = 'Izd'
        verbose_name_plural = 'Izd'
        
class Additional(models.Model): 
    offer = models.ForeignKey(Offer, related_name='additionals', on_delete=models.CASCADE)
    img = models.CharField(max_length=255, blank=True, null=True)
    sticker = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)   
    updated_at = models.DateTimeField(verbose_name='updated date', auto_now=True)

    def __str__(self):
        return self.name.__str__() 
        
    class Meta:
        verbose_name = 'Additional'
        verbose_name_plural = 'Additional'
        

class FileUploadImage(models.Model):
    hash = models.CharField(max_length=255, default=getRandomHash(ITEM_RANDOM_CHAR_HASH), verbose_name='hash')
    file_img = models.ImageField(upload_to=upload_to, blank=True, null=True, verbose_name='file')
    updated_at = models.DateTimeField(verbose_name='updated date', auto_now=True)

    def __str__(self):
        return self.hash.__str__() 
        
    class Meta:
        verbose_name = 'ФайлыИзображений'
        verbose_name_plural = 'ФайлыИзображений'
        

'''        
{
                                id: '533001122', 
                                price: '267 501', 
                                text_small : 'В продолжение нашего разговора высылаю Вам предварительный расчет стоимости заказа.', 
                                text_big:`Следующим этапом предлагаю встретиться на объекте для более подробного обсуждения особенностей и решений.
                                          Тонкость в том, что каждое решение по остеклению индивидуально и всех нюансов учесть без выезда на объект
                                          невозможно. По результатам встречи я смогу сделать окончательное предложение как по стоимости, так и по самому
                                          решению.`,
                                price_crossed: '315 450',
                                term: 'Срок изготовления: 4 дня',
                                price_izd: '25 000',
                                price_kompl: '25 000',
                                price_service: '25 000',
                                manager: 'Александр Саввин',
                                izds: [{
                                  id: "1",
                                  img: '',
                                  name: 'Изделие: Лоджия 1',
                                  har: 'Okonti, Bravo; 2800х1600',
                                  cout: '6',
                                  price: '25 000 р.',
                                },{
                                  id: "2",
                                  img: '',
                                  name: 'Изделие: Окно О-1',
                                  har: 'Okonti, Bravo; 3000х1600',
                                  cout: '1',
                                  price: '44 806 р.',
                                }],
                                additionals : [{
                                    img: 'assets/img/image-1.png',
                                    sticker: '-20%',
                                    name: 'Москитная сетка',
                                    note: 'Рамочная москитная сетка для окна белая. изделие, препятствующее проникновению в помещение насекомых, но не нарушающее циркуляцию воздуха. Изготавливается из безопасных материалов, которые легко очищаются от загрязнений.',
                                  },
                                  {
                                    img: 'assets/img/image-2.png',
                                    sticker: 'Бесплатно',
                                    name: 'Гребёнка',
                                    note: 'Гребенка регулирует ширину открывания окон и дверей, не дает им распахиваться настежь. Устанавливается на створки и ограничивает их движение. Состоит из двух элементов: гребенчатой пластины из ABS пластика, которая монтируется на раме, и фиксирующей фурнитуры (стального уголка), крепящегося к подвижной части окна или двери. Ограничитель не запирает створки. С его помощью осуществляется проветривание помещений в течение продолжительного времени в любую погоду. При неполном раскрытии окон и дверей не создаются сильные сквозняки и тепло не улетучивается из комнат слишком быстро.',
                                  },
                                ]  

                              }
'''

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