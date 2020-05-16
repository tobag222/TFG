# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# from scrapy.exporters import CsvItemExporter
from py2neo import Graph, Node, Relationship
import os

class MilanunciosPipeline(object):
    graph = Graph(auth=("neo4j","gabgab"))
    graph.delete_all()

    def process_item(self, item, spider):
        print( "///////////", os.getcwd())
        # os.chdir('./imagenes_perros')

        # si el path no es cero es que hay imagen.
        # if item['images'][0]['path']:

        anuncio = Node("Ad", titulo=str(item['titulo']), url=str(item['urlanuncio']), texto=str(item['texto']), fotos=item['image_urls'], ref=str(item['refanuncio']))
        localicacion = Node("location", city=str(item['localizacion']))
        telefono = Node("Tlf", numero=item['telefono'])
        telfono_aparece_en = Relationship(telefono, "APARECE_EN", anuncio)
        anunciante = Node("Anunciante", nombre=str(item['anunciante']), contacto=str(item['tipoContacto']))
        anunciante_postea_anuncio = Relationship(anunciante, "POSTEA", anuncio)
        anunciante_tiene_telefono = Relationship(anunciante, "TIENE", telefono)
        telefono_vendeen_localizacion = Relationship(telefono, "VENDEEN", localicacion)


        self.graph.create(anuncio)
        self.graph.create(localicacion)
        self.graph.create(telefono)
        self.graph.create(telfono_aparece_en)
        self.graph.create(anunciante)
        self.graph.create(anunciante_postea_anuncio)
        self.graph.create(anunciante_tiene_telefono)
        self.graph.create(telefono_vendeen_localizacion)



        print("8888888888888888888888888888")
        print(item.values)
        print("1111111111111111111111111111")
        return item

