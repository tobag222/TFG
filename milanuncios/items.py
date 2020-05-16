# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MilanunciosItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    urlanuncio = scrapy.Field()
    texto = scrapy.Field()
    titulo = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    telefono = scrapy.Field()
    tipoContacto = scrapy.Field()
    anunciante = scrapy.Field()
    refanuncio = scrapy.Field()
    localizacion = scrapy.Field()