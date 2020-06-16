# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from py2neo import Graph, Node, Relationship
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
import os
from PIL import Image

'''

Comprueba si existe el numero de telefono en la BD
'''
def existeTelefono(graph, numero):
    # # nodo = list(graph.nodes.match(labelTlf, numero=numero[0]))
    # if len(nodo) == 0:
    #     return False , nodo
    # else:
    #     return True , nodo
    result = graph.evaluate('MATCH (a:Tlf) where a.numero="' + numero + '" return a')

    if result == None:
        return False, ""
    else:
        return True, result

'''
Comprueba si existe un anunciante asociado a ese telefono 
'''
def anuncioExiste(graph,referencia ,numero):

    result = graph.evaluate('MATCH (u:Tlf)-[:APARECE_EN]->(a:Ad) where u.numero="' + numero + '" AND a.ref="'+referencia+'" return a')
    if result == None:
        return False, ""
    if result["ref"] == referencia:
        return True, result
    else:
        return False, ""

 
    # result = graph.evaluate('MATCH (u:Tlf)-[:APARECE_EN]->(a:Ad) where u.numero="' + numero + '" AND a.ref="'+referencia+'" return a')
    # if result == None:
    #     return False, ""
    # att = []
    # for r in result:
    #     print(r)
    #     att.append(result[r])
    # anuncio = Node("Ad", texto=att[0],titulo=att[1],ref=att[2],abuso=att[3],url=att[4],fotos=att[5])
    # if result["ref"] == referencia:
    #     return True, anuncio
    # else:
    #     return False, ""



def anuncianteExiste(graph,anunciante,numero):

    result = graph.evaluate('MATCH (a:Anunciante)-[:TIENE]->(u:Tlf) where u.numero="' + numero + '" return a') # un 'pablo' por cada telefono
    # result = graph.evaluate('MATCH (a:Anunciante) where a.nombre="'+anunciante+'" return a') # el mismo 'pablo' para varios telefonos
    if result == None:
        return False, ""

    if result["nombre"] == anunciante:
        return True, result
    else:
        return False, ""





def localizacionExiste(graph,localizacion,numero):
    
    result = graph.evaluate('MATCH (a:Tlf)-[:VENDEEN]->(u:location) where a.numero="' + numero + '" AND u.city="' +localizacion+ '"  return u')
    print('MATCH (a:Tlf)-[:VENDEEN]->(u:location) where a.numero="' + numero + '" AND u.city="' +localizacion+ '"  return u')
    """
    if result == None:
        return False, ""
    location = Node("location", city=result["city"])
    if result["city"] == localizacion:
        return True, location
    else:
        return False, ""
    """
    if result == None:
        return False, ""
    else:
        return True, result




class MilanunciosPipeline(object):

    model = load_model('model_ccn_tfg_perros_3.h5')
    graph = Graph(auth=("neo4j", "gabgab"))
    ## si se desea borrar la base de datos, antes de comenzar la extracción 
    graph.delete_all()

    path_base_imagenes ="./imagenes_perros"
        
    def process_item(self, item, spider):
        
        '''
        Procesamiento de las imagenes en busca de casos de abuso usando el modelo
        Se cargan la imagen, si existe, se evalua con el modelo, y se guarda el 
        resultado que arroje en el campo 'abuso'
        '''        
        abuso = False
        if item['images'][0]['path']:  #si existe, es que hay al menos una imagen
            for field in item['images']:
                imagen_path = self.path_base_imagenes + "/" + field['path']
                test_image = image.load_img(imagen_path, target_size = (64, 64))
                test_image = image.img_to_array(test_image)
                test_image = np.expand_dims(test_image, axis=0)
                result = self.model.predict(test_image) ## aquí se hace la prediccion
                print (result[0][0])
                if str(result[0][0]) == '1.0': ##si mal
                    abuso = True

        nodoDevuelto = existeTelefono(self.graph, item["telefono"][0])
        
        ## Si se ha encontrado el telefono en la BD
        # if nodoDevuelto[0] and item['telefono'][0]!='0':
        if nodoDevuelto[0]:
            telefono = nodoDevuelto[1]

            # Se busca si hay anunciante relacionado a ese Tlf
            persDevuelt = anuncianteExiste(self.graph, item['anunciante'][0], item["telefono"][0])
            if not persDevuelt[0]: #Si no existe el anunciante con ese telefono, se crea asociándolo a este telefono
                anunciante = Node("Anunciante", nombre=str(item['anunciante'][0]), contacto=str(item['tipoContacto'][0]))
                self.graph.create(anunciante)

                anunciante_tiene_telefono = Relationship(anunciante, "TIENE", telefono)
                self.graph.create(anunciante_tiene_telefono)


            else:
                anunciante = persDevuelt[1]


            # Se busca si hay anuncio relacionado a ese Tlf
            anuncioDevuelto = anuncioExiste(self.graph,item["refanuncio"][0],item["telefono"][0])
          
            if not anuncioDevuelto[0]: #Si no existe anuncio relacionado a ese Tlf, se crea asociándolo a ese Tlf
                anuncio = Node("Ad", titulo=str(item['titulo'][0]), url=str(item['urlanuncio'][0]),texto=str(item['texto'][0]), fotos=item['image_urls'], ref=str(item['refanuncio'][0]), abuso=str(abuso)  )
                self.graph.create(anuncio)
                telfono_aparece_en = Relationship(telefono, "APARECE_EN", anuncio)
                self.graph.create(telfono_aparece_en)
                print(anunciante.identity)
                anunciante_postea_anuncio = Relationship(anunciante, "POSTEA", anuncio)
                self.graph.create(anunciante_postea_anuncio)
            else: 
                pass
            
            # Se busca si hay localizacion relacionado a ese Tlf
            localizDevuelta= localizacionExiste(self.graph, item["localizacion"][0], item["telefono"][0])
            if not localizDevuelta[0]: #Si no existe la localizacion
                localicacion = Node("location", city=str(item['localizacion'][0]))
                telefono_vendeen_localizacion = Relationship(telefono, "VENDEEN", localicacion)
                self.graph.create(localicacion)
                self.graph.create(telefono_vendeen_localizacion)
        
        ## por defecto si no se comprueba existencia previa del telefono
        else:
            telefono = Node("Tlf", numero=item['telefono'][0])
            anuncio = Node("Ad", titulo=str(item['titulo'][0]), url=str(item['urlanuncio'][0]), texto=str(item['texto'][0]), fotos=item['image_urls'], ref=str(item['refanuncio'][0]), abuso=str(abuso) )
            localicacion = Node("location", city=str(item['localizacion'][0]))
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




