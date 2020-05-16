# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from milanuncios.items import MilanunciosItem
from scrapy import Request
import re
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
    start_urls = ['http://milanuncios.com/perros/?fromSearch=1/']
    # il = ItemLoader(item= MilanunciosItem(), response=response)
    

    rules = [Rule(LinkExtractor(allow=('#fotos')), callback='parse_fotos', follow=True)]
    # driver = webdriver.Chrome('./chromedriver')  

    def parse_fotos(self, response):
        # il = ItemLoader(item= MilanunciosItem(), response=response)
        # print ("pased fotos")
        # fotos_urls = response.xpath('//*[@class="pagAnuFoto"]/img/@src').extract()
        # for url in fotos_urls:
        #     yield url
        # pass
        # self.driver.get(response.url)
        # self.driver.find_element_by_class_name("byCall").click()
        # self.driver.swi
        item = MilanunciosItem()
        # il = ItemLoader(item= MilanunciosItem(), response=response)
        url_an = response.url
        adId = response.xpath('//div[@class="pillDiv pillRef"]/strong/text()').extract_first()
        contact_url_base = "https://www.milanuncios.com/datos-contacto/?usePhoneProxy=0&from=detail&id="
        # telefono es un item devuelto desde el callback parse_telefono()
       
        
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
        print("                LOCALIZACION: ",localizacion)


        # il.replace_value('urlanuncio', url_an)
        # il.replace_value('fotos', fotos)
        # il.replace_value('titulo', titulo)
        # il.replace_value('texto', texto)
        # il.replace_value('telefono', telefono)

        item['urlanuncio']=url_an
        item['image_urls']=fotos
        item['titulo']=titulo
        item['texto']=texto
        item['tipoContacto']=tipoContacto
        item['anunciante']=anunciante
        item['refanuncio']=refanuncio
        item['localizacion'] = localizacion

        # print("contact url is: ",contact_url_base+adId)
        
        # yield self.il.load_item()
        request = Request(
            url=contact_url_base+adId,
            callback=self.parse_telefono,
            meta={'item':item}
            # meta={'itemLoader':il}
        )
        # il = ItemLoader(item= item, response=response)
        # yield il.load_item()
        # print("----------------------------")
        # print(item.values)
        # print("----------------------------")
        yield request

    
    def parse_telefono(self, response):
        codigo_pagina = str(response.body)
        pattern = "getTrackingPhone\((.*?)\)"
        telefono = re.search(pattern, str(codigo_pagina)).group(1)
        # if str(response.xpath('//div[@class="texto"]/div/strong/text()').extract_first()).startswith('MUY IMPORTANTE'):
        #     anunciante = response.xpath('//div[@class="texto"]/div[2]/strong/text()').extract_first()
        # else:
        #     anunciante = response.xpath('//div[@class="texto"]/div/strong/text()').extract_first()
        # print(":::::::::::::::TELEFONO::::::::::::::::::::\n")
        # print(telefono)
        # print(":::::::::::::::::::::::::::::::::::::::::::\n")
        item = response.meta['item']
        # il = ItemLoader(item= item, response=response)
        item['telefono']=telefono
        # item['anunciante']=anunciante
        # self.il.load_item()

        return item


        


