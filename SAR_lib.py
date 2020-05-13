import json
from nltk.stem.snowball import SnowballStemmer
import os
import re
import shlex

class SAR_Project:
    """
    Prototipo de la clase para realizar la indexacion y la recuperacion de noticias

        Preparada para todas las ampliaciones:
          parentesis + multiples indices + posicionales + stemming + permuterm + ranking de resultado

    Se deben completar los metodos que se indica.
    Se pueden añadir nuevas variables y nuevos metodos
    Los metodos que se añadan se deberan documentar en el codigo y explicar en la memoria
    """

    # lista de campos, el booleano indica si se debe tokenizar el campo
    # NECESARIO PARA LA AMPLIACION MULTIFIELD
    fields = [("title", True), ("date", False),
              ("keywords", True), ("article", True),
              ("summary", True)]


    # numero maximo de documento a mostrar cuando self.show_all es False
    SHOW_MAX = 10


    def __init__(self):
        """
        Constructor de la classe SAR_Indexer.
        NECESARIO PARA LA VERSION MINIMA

        Incluye todas las variables necesaria para todas las ampliaciones.
        Puedes añadir más variables si las necesitas

        """
        self.index = {
            "title": {},
            "article": {},
            "summary": {},
            "keywords": {},
            "date": {}
        } # hash para el indice invertido de terminos --> clave: termino, valor: posting list.
                        # Si se hace la implementacion multifield, se pude hacer un segundo nivel de hashing de tal forma que:
                        # self.index['title'] seria el indice invertido del campo 'title'.
        self.doc_id = 0 ## Id de los doc, goes from 1 to infinity
        self.news_id = 0 ## Id de las noticias, goes from 1 to infinity
        self.sindex = {} # hash para el indice invertido de stems --> clave: stem, valor: lista con los terminos que tienen ese stem
        self.ptindex = {} # hash para el indice permuterm.
        self.docs = {} # diccionario de terminos --> clave: entero(docid),  valor: ruta del fichero.
        self.weight = {} # hash de terminos para el pesado, ranking de resultados. puede no utilizarse
        self.news = {} # hash de noticias --> clave entero (newid), valor: la info necesaria para diferencia la noticia dentro de su fichero
        self.tokenizer = re.compile("\W+") # expresion regular para hacer la tokenizacion
        self.stemmer = SnowballStemmer('spanish') # stemmer en castellano
        self.show_all = False # valor por defecto, se cambia con self.set_showall()
        self.show_snippet = False # valor por defecto, se cambia con self.set_snippet()
        self.use_stemming = False # valor por defecto, se cambia con self.set_stemming()
        self.use_ranking = False  # valor por defecto, se cambia con self.set_ranking()


    ###############################
    ###                         ###
    ###      CONFIGURACION      ###
    ###                         ###
    ###############################


    def set_showall(self, v):
        """

        Cambia el modo de mostrar los resultados.

        input: "v" booleano.

        UTIL PARA TODAS LAS VERSIONES

        si self.show_all es True se mostraran todos los resultados el lugar de un maximo de self.SHOW_MAX, no aplicable a la opcion -C

        """
        self.show_all = v


    def set_snippet(self, v):
        """

        Cambia el modo de mostrar snippet.

        input: "v" booleano.

        UTIL PARA TODAS LAS VERSIONES

        si self.show_snippet es True se mostrara un snippet de cada noticia, no aplicable a la opcion -C

        """
        self.show_snippet = v


    def set_stemming(self, v):
        """

        Cambia el modo de stemming por defecto.

        input: "v" booleano.

        UTIL PARA LA VERSION CON STEMMING

        si self.use_stemming es True las consultas se resolveran aplicando stemming por defecto.

        """
        self.use_stemming = v


    def set_ranking(self, v):
        """

        Cambia el modo de ranking por defecto.

        input: "v" booleano.

        UTIL PARA LA VERSION CON RANKING DE NOTICIAS

        si self.use_ranking es True las consultas se mostraran ordenadas, no aplicable a la opcion -C

        """
        self.use_ranking = v




    ###############################
    ###                         ###
    ###   PARTE 1: INDEXACION   ###
    ###                         ###
    ###############################


    def index_dir(self, root, **args):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Recorre recursivamente el directorio "root"  y indexa su contenido
        los argumentos adicionales "**args" solo son necesarios para las funcionalidades ampliadas

        """

        self.multifield = args['multifield']
        self.positional = args['positional']
        self.stemming = args['stem']
        self.permuterm = args['permuterm']
        print("Retrieving information...")
        for dir, subdirs, files in os.walk(root):
            for filename in files:
                if filename.endswith('.json'):
                    fullname = os.path.join(dir, filename)
                    self.index_file(fullname)
        print("Indexing complete!")
        ##########################################
        ## COMPLETAR PARA FUNCIONALIDADES EXTRA ##
        ##########################################


    def index_file(self, filename):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Indexa el contenido de un fichero.

        Para tokenizar la noticia se debe llamar a "self.tokenize"

        Dependiendo del valor de "self.multifield" y "self.positional" se debe ampliar el indexado.
        En estos casos, se recomienda crear nuevos metodos para hacer mas sencilla la implementacion

        input: "filename" es el nombre de un fichero en formato JSON Arrays (https://www.w3schools.com/js/js_json_arrays.asp).
                Una vez parseado con json.load tendremos una lista de diccionarios, cada diccionario se corresponde a una noticia

        """

        with open(filename) as fh:
            if(self.multifield):
                sections = ['title','article', 'summary', 'keywords', 'date']
            else:
                sections = ['article']

            self.doc_id += 1 # id del filename
            self.docs[self.doc_id] = filename # esto es así?
            jlist = json.load(fh) # To Do: asignar id al fichero filename
            for noticia in jlist: # To Do: asignar id a la noticia
                self.news_id += 1 # id de la noticia
                self.news[self.news_id] = self.docs[self.doc_id] + ": " + noticia["id"] # Sé que se podría hacer con filename
                                                                                        # pero esto me parece más limpio
                for section in sections: # por el multifield
                    content = noticia[section]
                    tokens = self.tokenize(content)
                    aux = {}
                    for token in tokens:
                        aux[token] = aux.get(token, 0) + 1 # se cuentan las ocurrencias
                    for word in aux:
                        self.index[section][word] = self.index[section].get(word, []) # si no existe se crea una lista
                        self.index[section][word].append(Posting(self.news_id, aux[word])) # se crea el posting del token en la noticia en la sección

        #
        # "jlist" es una lista con tantos elementos como noticias hay en el fichero,
        # cada noticia es un diccionario con los campos:
        #      "title", "date", "keywords", "article", "summary"
        #
        # En la version basica solo se debe indexar el contenido "article"
        #
        #
        #
        #################
        ### COMPLETAR ###
        #################

    def index_multifield(self, noticia):
        sections = ['title', 'summary', 'keywords', 'date']



    def tokenize(self, text):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Tokeniza la cadena "texto" eliminando simbolos no alfanumericos y dividientola por espacios.
        Puedes utilizar la expresion regular 'self.tokenizer'.

        params: 'text': texto a tokenizar

        return: lista de tokens

        """
        return self.tokenizer.sub(' ', text.lower()).split()



    def make_stemming(self):
        """
        NECESARIO PARA LA AMPLIACION DE STEMMING.

        Crea el indice de stemming (self.sindex) para los terminos de todos los indices.

        self.stemmer.stem(token) devuelve el stem del token

        """

        pass
        ####################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE STEMMING ##
        ####################################################



    def make_permuterm(self):
        """
        NECESARIO PARA LA AMPLIACION DE PERMUTERM

        Crea el indice permuterm (self.ptindex) para los terminos de todos los indices.

        """
        pass
        ####################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE STEMMING ##
        ####################################################




    def show_stats(self):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Muestra estadisticas de los indices

        """

        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################
        if(self.multifield):
            sections = ['title','article','summary','keywords','date']
        else:
            sections = ['article']

        print("\n========================================")
        print("Number of indexed days:", len(self.docs))
        print("----------------------------------------")
        print("Number of indexed news:", len(self.news))
        print("----------------------------------------")
        print("TOKENS:")
        for i in sections:
            print("  # of tokens in {}: {}".format(i, len(self.index[i])))
        print("----------------------------------------")
        if(self.stemming):
            print("STEMS:")
            for i in sections:
                print("  # of stems in {}: {}".format(i, len(self.index[i]))) # aún falta hacer cosas
            print("----------------------------------------")
        if(self.positional):
            print("Positional queries are allowed")
        else:
            print("Positional queries are NOT allowed")
        print("========================================")

        ## Como los permuterm no existen en nuestro diseño
        ## no me voy a molestar en implementarlo



    ###################################
    ###                             ###
    ###   PARTE 2.1: RECUPERACION   ###
    ###                             ###
    ###################################


    def solve_query(self, query, prev={}):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Resuelve una query.
        Debe realizar el parsing de consulta que sera mas o menos complicado en funcion de la ampliacion que se implementen


        param:  "query": cadena con la query
                "prev": incluido por si se quiere hacer una version recursiva. No es necesario utilizarlo.


        return: posting list con el resultado de la query

        """

        if query is None or len(query) == 0:
            return []

        class State(Enum):
            POST = auto()   #Representa una posting list de un término
            OP = auto()     #Representa una operación
            PAR = auto()    #Representa un paréntesis

        #shlex mantiene el texto entre comillas con posix=False
        #y separa los paréntesis en tokens únicos con punctuation_chars=True
        #técnicamente con punctuation_chars separa los caracteres ();<>|&
        #también separa con los dos puntos (:) lo cual es raro pero funciona así

        #Haremos una primera pasada para hacer las queries al sistema de recuperación.
        #Después las uniremos con AND, OR, NOT y los paréntesis
        
        #Si aparece un token después de un token hay que hacer un and entre los dos.
        #En ese caso añadiremos un AND a la pila de objetos que quedará como resultado
        token_after_token = False
        
        tokens = shlex.shlex(instream=query, posix=False, punctuation_chars=True)
        elements=[]
        t = tokens.get_token()
        while (t != ''):
            if (t == 'AND') or (t == 'OR') or (t == 'NOT'):
                elements.append((State.OP, t))
                t = tokens.get_token()
                token_after_token = False
                
            elif (t == '(') or (t == ')'):
                elements.append((State.PAR, t))
                t = tokens.get_token()
                token_after_token = False
                
            else: #token
                
                #If there were two consecutive tokens, we need to make an AND between them.
                #We push an AND onto the stack
                if token_after_token:
                    elements.append((State.OP, "AND"))
                    
                t0 = t
                t = tokens.get_token() #fortunately, if it's eof, shlex returns '' and we can work with that
                
                
                if (t == ':'):  #it's a multifield term and t0 is the field
                    t = tokens.get_token() #t is now the token to search
                    elements.append((State.POST, self.get_posting(t, field=t0)))

                    t = tokens.get_token()
                else:   #no multifield
                    elements.append((State.POST, self.get_posting(t0)))
                    #t is the next token

                token_after_token = True
        
        #Ahora elements es una lista (pila) de tuplas (State, object) con la que podemos organizar un analizador
        #léxico



    def get_posting(self, term, field='article'):
        """
        NECESARIO PARA TODAS LAS VERSIONES
        Luego las uniremos con la consulta
        Devuelve la posting list asociada a un termino.
        Dependiendo de las ampliaciones implementadas "get_posting" puede llamar a:
            - self.get_positionals: para la ampliacion de posicionales
            - self.get_permuterm: para la ampliacion de permuterms
            - self.get_stemming: para la amplaicion de stemming


        param:  "term": termino del que se debe recuperar la posting list.
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices

        return: posting list

        """
        pass
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################



    def get_positionals(self, terms, field='article'):
        """
        NECESARIO PARA LA AMPLIACION DE POSICIONALES

        Devuelve la posting list asociada a una secuencia de terminos consecutivos.

        param:  "terms": lista con los terminos consecutivos para recuperar la posting list.
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices

        return: posting list

        """
        #Max: Este es el algoritmo visto en teoría de intersección posicional con k=1 (términos consecutivos)



    def get_stemming(self, term, field='article'):
        """
        NECESARIO PARA LA AMPLIACION DE STEMMING

        Devuelve la posting list asociada al stem de un termino.

        param:  "term": termino para recuperar la posting list de su stem.
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices

        return: posting list

        """

        stem = self.stemmer.stem(term)

        ####################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE STEMMING ##
        ####################################################


    def get_permuterm(self, term, field='article'):
        """
        NECESARIO PARA LA AMPLIACION DE PERMUTERM

        Devuelve la posting list asociada a un termino utilizando el indice permuterm.

        param:  "term": termino para recuperar la posting list, "term" incluye un comodin (* o ?).
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices

        return: posting list

        """

        ##################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA PERMUTERM ##
        ##################################################




    def reverse_posting(self, p):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Devuelve una posting list con todas las noticias excepto las contenidas en p.
        Util para resolver las queries con NOT.


        param:  "p": posting list


        return: posting list con todos los newid exceptos los contenidos en p

        """

        """
        El objetivo es encontrar todas las noticias y
        devolverlas en formato posting list. Realmente esto
        lo podemos hacer si iteramos por todo el diccionario
        de noticias y para cada una creamos un objeto posting. Perdemos la información posicional... pero
        no vamos a tener una consulta como
        "valencia AND NOT playa", así que no importa
        """
        res = []
        #IMPORTANTE: p y news están ordenados
        j = 0   #El índice de la noticia que queremos omitir
        #Se puede hacer en tiempo lineal con la talla de news
        keys = self.news.keys()
        for i in range(0,len(keys)):
            #p[j] es un objeto de tipo Posting
            if (keys[i] != p[j].news_id):
                #Añadimos un posting correspondiente a la noticia (perdemos frequency y positional pero no importa)
                res.append(Posting(keys[i]))
            else:
                j+=1
                if (j == len(p)):
                    i+=1
                    break #Todas las demás noticias no están en p y deben ser añadidas

        for k in range(i,len(keys)):
            res.append(Posting(keys[k]))

        return res



    #Precondición: p1 y p2 son listas de postings:
    #[Posting]
    def and_posting(self, p1, p2):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Calcula el AND de dos posting list de forma EFICIENTE

        param:  "p1", "p2": posting lists sobre las que calcular


        return: posting list con los newid incluidos en p1 y p2


        """
        res = []
        i = 0   #Indice de p1
        j = 0   #Indice de p2
        if (len(p1) == 0 or len(p2) == 0):
            return res
        #Tenemos un elemento en p1 y p2. Comprobamos tipo,
        #solo por seguridad
        if not (isinstance(p1[i], Posting)):
            raise Exception("and_posting: El tipo de la posting list no es [Posting]")
        while (i < len(p1) and j < len(p2)):
            if (p1[i].news_id == p2[j].news_id):
                res.append(p1[i])
                i+=1
                j+=1
            elif (p1[i].news_id < p2[j].news_id):
                i+=1
            else:
                j+=1

        while (i < len(p1)):
            res.append(p1[i])
            i+=1

        return res


    def or_posting(self, p1, p2):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Calcula el OR de dos posting list de forma EFICIENTE

        param:  "p1", "p2": posting lists sobre las que calcular


        return: posting list con los newid incluidos de p1 o p2

        """
        res = []
        i = 0   #Indice de p1
        j = 0   #Indice de p2
        if (len(p1) == 0):
            return p2
        if (len(p2) == 0):
            return p1
        #Tenemos un elemento en p1 y p2. Comprobamos tipo,
        #solo por seguridad
        if not (isinstance(p1[i], Posting)):
            raise Exception("or_posting: El tipo de la posting list no es [Posting]")
        while (i < len(p1) and j < len(p2)):
            if (p1[i].news_id == p2[j].news_id):
                res.append(p1[i])
                i+=1
                j+=1
            elif (p1[i].news_id < p2[j].news_id):
                res.append(p1[i])
                i+=1
            else:
                res.append(p2[j])
                j+=1
        return res
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################

    #Precondición: p1 y p2 son listas de postings:
    #[Posting]
    def minus_posting(self, p1, p2):
        """
        OPCIONAL PARA TODAS LAS VERSIONES

        Calcula el except de dos posting list de forma EFICIENTE.
        Esta funcion se propone por si os es util, no es necesario utilizarla.

        param:  "p1", "p2": posting lists sobre las que calcular


        return: posting list con los newid incluidos de p1 y no en p2

        """
        res = []
        i = 0   #Indice de p1
        j = 0   #Indice de p2
        if (len(p1) == 0):
            return res
        if (len(p2) == 0):
            return p1

        #Tenemos un elemento en p1 y p2. Comprobamos tipo,
        #solo por seguridad
        if not (isinstance(p1[i], Posting)):
            raise Exception("minus_posting: El tipo de la posting list no es [Posting]")
        while (i < len(p1) and j < len(p2)):
            if (p1[i].news_id == p2[j].news_id):
                i+=1
                j+=1
            elif (p1[i].news_id < p2[j].news_id):
                res.append(p1[i])
                i+=1
            else:
                j+=1

        return res






    #####################################
    ###                               ###
    ### PARTE 2.2: MOSTRAR RESULTADOS ###
    ###                               ###
    #####################################


    def solve_and_count(self, query):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Resuelve una consulta y la muestra junto al numero de resultados

        param:  "query": query que se debe resolver.

        return: el numero de noticias recuperadas, para la opcion -T

        """
        result = self.solve_query(query)
        print("%s\t%d" % (query, len(result)))
        return len(result)  # para verificar los resultados (op: -T)


    def solve_and_show(self, query):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Resuelve una consulta y la muestra informacion de las noticias recuperadas.
        Consideraciones:

        - En funcion del valor de "self.show_snippet" se mostrara una informacion u otra.
        - Si se implementa la opcion de ranking y en funcion del valor de self.use_ranking debera llamar a self.rank_result

        param:  "query": query que se debe resolver.

        return: el numero de noticias recuperadas, para la opcion -T

        """
        result = self.solve_query(query)
        if self.use_ranking:
            result = self.rank_result(result, query)

        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################




    def rank_result(self, result, query):
        """
        NECESARIO PARA LA AMPLIACION DE RANKING

        Ordena los resultados de una query.

        param:  "result": lista de resultados sin ordenar
                "query": query, puede ser la query original, la query procesada o una lista de terminos


        return: la lista de resultados ordenada

        """

        pass

        ###################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE RANKING ##
        ###################################################

"""
La idea de esta clase es que los posting de los índices sean objetos estructurados,
aprovechar la orientación a objetos, en vez de hacerlo con listas. Sobretodo pensando
en la mejora de las posicionales: para no tener que iterar por "listas de listas de listas".
"""
class Posting:

    def __init__(self, news_id, frequency):
        self.news_id = news_id
        self.frequency = frequency

    def __init__(self, news_id):
        self.news_id = news_id
        self.frequency = 1

    def __eq__(self, other):
        if isinstance(other, Posting):
            return self.news_id == other.news_id
        else:
            return NotImplemented
