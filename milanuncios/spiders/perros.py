# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from milanuncios.items import MilanunciosItem
from scrapy import Request
import re

import random
# from selenium import webdriver
# from scrapy.selector import Selector
'''
aquí no usamos la clase Spider por defecto 
por eso quitamos el import scrapy de siempre
e importamos otra clase llamada CrawlSpider
'''
class PerrosSpider(CrawlSpider):
    name = 'perros'
    allowed_domains = ['milanuncios.com']
    randnum = random.randrange(1,5)
    # start_urls = ['http://milanuncios.com/venta-de-perros/?fromSearch='+str(randnum)]
    start_urls = ['http://milanuncios.com/venta-de-perros/?fromSearch=1']

    rules = [Rule(LinkExtractor(allow=('#fotos')), callback='parse_fotos', follow=True), Rule(LinkExtractor(restrict_xpaths=('//*[contains(@class,"adlist-paginator-pagelink adlist-paginator-pageselected")][contains(@onclick,"pSiguiente")]')),callback='parse', follow=True)]  
  
    def parse_fotos(self, response):
        
        url_an = response.url
        adId = response.xpath('//div[@class="pillDiv pillRef"]/strong/text()').extract_first()
        contact_url_base = "https://www.milanuncios.com/datos-contacto/?usePhoneProxy=0&from=detail&id="
       
        
        fotos = response.xpath('//*[@class="pagAnuFoto"]/img/@src').extract()
        titulo = response.xpath('//*[@class="ad-detail-title"]/text()').extract_first()
        texto = response.xpath('//*[@class="pagAnuCuerpoAnu"]/text()').extract_first()
        tipoContacto=""
        if response.xpath('//div[@class="pagAnuContactSellerType pagAnuContactSellerTypePro"]'):
            tipoContacto = "profesional"
        else:
            tipoContacto = "particular"
        anunciante = response.xpath('//div[@class="pagAnuContactNombre"]/text()').extract_first()
        refanuncio = response.xpath('//div[@class="pillDiv pillRef"]/strong/text()').extract_first()
        pattern = "\((.*?)\)" # la ciudad viene como "- labradores(MADRID)"
        localizacion = re.search(pattern, str(response.xpath('//div[@class="pagAnuCatLoc"]/text()').extract_first())).group(1)

        request = Request(
            url=contact_url_base+adId,
            callback=self.parse_telefono,
            meta={
                'urlanuncio': url_an,
                'image_urls': fotos,
                'titulo': titulo,
                'texto': texto,
                'tipoContacto': tipoContacto,
                'anunciante': anunciante,
                'refanuncio': refanuncio,
                'localizacion': localizacion
            }
        )
        yield request



    
    def parse_telefono(self, response):        
        codigo_pagina = str(response.body)
        il = ItemLoader(item= MilanunciosItem(), response=response)

        pattern = "getTrackingPhone\((.*?)\)"

        urlanuncio = response.meta['urlanuncio']
        image_urls = response.meta['image_urls']
        titulo = response.meta['titulo']
        texto = response.meta['texto']
        tipoContacto = response.meta['tipoContacto']
        anunciante = response.meta['anunciante']
        refanuncio = response.meta['refanuncio']
        localizacion = response.meta['localizacion']

        telefono = re.search(pattern, str(codigo_pagina)).group(1)

        il.replace_value('urlanuncio',urlanuncio)
        il.replace_value('image_urls',image_urls)
        il.replace_value('titulo',titulo)
        il.replace_value('texto',texto)
        il.replace_value('tipoContacto',tipoContacto)
        il.replace_value('anunciante',anunciante)
        il.replace_value('refanuncio',refanuncio)
        il.replace_value('localizacion',localizacion)
        il.replace_value('telefono',telefono)

        yield il.load_item()



        


