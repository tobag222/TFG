# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# from scrapy.exporters import CsvItemExporter
from py2neo import Graph, Node, Relationship
import os



# from urllib.parse import urlparse
# import scrapy
# from scrapy.pipelines.images import ImagesPipeline

# class MisImagenesPipeline(ImagesPipeline):

#     def get_media_requests(self, item, info):
#         return [scrapy.Request(x, meta={'nombre_imagen': item["refanuncio"][0]}) 
#                 for x in item.get('image_urls', [])]

#     # def file_path(self, request, response=None, info=None):
#     #     return f'{request.meta['nombre_imagen']}.jpg'
#     def file_path(self, request, response=None, info=None):
#         return 'full/' + os.path.basename(request.meta['nombre_imagen'])


class MilanunciosPipeline(object):
    graph = Graph(auth=("neo4j","gabgab"))
    graph.delete_all()

    def process_item(self, item, spider):
        # print( "///////////", os.getcwd())
        # os.chdir('./imagenes_perros')

        # si el path no es cero en la primera imagen es que HAY IMAGEN.
        # if item['images'][0]['path']:
        #     i = 0
        #     nuevo_nombre_imagen = item['refanuncio'][0]
        #     for image in item['images']:
        #         nuevo_path_imagen = 'full/' + nuevo_nombre_imagen + '_' + str(i) + '.jpg'
        #         os.rename(item['images'][i]['path'], nuevo_path_imagen)
        #         i = i + 1

        if item['images'][0]['path']:
            for field in item['images']:
                print("/////////////////////////////////////////////////", field['path'])

        anuncio = Node("Ad", titulo=str(item['titulo'][0]), url=str(item['urlanuncio'][0]), texto=str(item['texto'][0]), fotos=item['image_urls'], ref=str(item['refanuncio'][0]))
        localicacion = Node("location", city=str(item['localizacion'][0]))
        telefono = Node("Tlf", numero=item['telefono'][0])
        telfono_aparece_en = Relationship(telefono, "APARECE_EN", anuncio)
        anunciante = Node("Anunciante", nombre=str(item['anunciante'][0]), contacto=str(item['tipoContacto'][0]))
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

