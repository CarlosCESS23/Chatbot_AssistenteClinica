import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


#Listas de palavras comuns em português para ignorar

PARAVRAS_COMUNS = set(stopwords.words('portuguese'))

#Base de conhecimento de sintomas e condições de casos leves:

SINTOMAS_CHAVE = {
    "febre", "calafrio", "calafrios",
    "tosse", "espirro", "espirros",
    "dor de cabeça", "enxaqueca", "cefaleia",
    "dor de garganta", "garganta inflamada",
    "coriza", "nariz escorrendo",
    "congestão nasal", "nariz entupido",
    "dor no corpo", "dores no corpo", "mialgia",
    "cansaço", "fadiga", "fraqueza", "moleza",
    "falta de ar", "dificuldade para respirar",
    "dor no peito", "aperto no peito",
    "náusea", "enjoo", "vômito", "vomitar",
    "diarreia",
    "dor abdominal", "dor de barriga",
    "tontura",
    "perda de olfato", "perda de paladar"
}

def extrair_sintomas(texto) -> list[str]:

    #Essa função do texto serve para extrair os sintomas conhecidos:

    texto_lower = texto.lower() # Para diminui todos os tamanhos do texto
    tokens =  word_tokenize(texto_lower, language="portuguese")

    #Aqui vai remover as palavras para focar somente nas importantes

    tokens_filtrados = [palavra for palavra in tokens if palavra not in PARAVRAS_COMUNS]

    sintomas_encontrados = set()

    #Transforma a lista de tokens de volta em texto para procurar por termos compostos
    texto_filtrado_str = ' '.join(tokens_filtrados)

    for sintoma in SINTOMAS_CHAVE:
        
        #Aqui verifica se o sintoma (simples ou composto está no texto)
        if sintoma in texto_filtrado_str:
            sintomas_encontrados.add(sintoma)

    return list(sintomas_encontrados)