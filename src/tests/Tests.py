import json
from pprint import pprint

from Resolver import Resolver


def resolve(filename, uri):
    with open(filename, 'r') as f:
        text = f.read()

    substitutions, _ = Resolver.resolve(text, uri)
    substituted_text = Resolver.substitute_in_text(text, substitutions)
    print(substituted_text)


# noinspection PyPep8Naming
def resolveAndLinkArticles(filename):
    with open(filename, 'r') as json_data:
        for line in json_data:
            try:
                entityLinks = {}
                dataText = json.loads(line)

                # if 'Agassi' in dataText['id']:
                print('Article: ' + dataText['id'])
                articleLabel = dataText['id']
                articleLabel = articleLabel[articleLabel.rfind('/') + 1:].replace('_', ' ')
                entityLinks[articleLabel] = dataText['id']

                pprint(dataText['links'])
                # pprint(dataText['text'])
                for item in dataText['links']:
                    entityLinks[item['anchorText']] = item['link']

                substitutions, resolvedSentences = Resolver.resolve(
                    text=dataText['text'],
                    entity_uri=dataText['id'])

                substitutedText = Resolver.substitute_in_text(
                    text=dataText['text'],
                    substitutions=substitutions)

                linkedPassages = Resolver.get_passages_and_linked_entities(
                    substitutions=substitutions,
                    resolved_sentences=resolvedSentences,
                    entity_links=entityLinks)

                for linkedPassage in linkedPassages:
                    print(linkedPassage)

            except ValueError:
                continue


def testJson(filename):
    with open(filename) as json_data:
        for line in json_data:
            try:
                entityLinks = {}
                dataText = json.loads(line)
                pprint(dataText['id'])
                for item in dataText['links']:
                    entityLinks[item['anchorText']] = item['link']
                # print(str(dataText['links'][0]['anchorText']) + ' ' + str(dataText['links'][0]['link']))
                break
                # pprint(dataText['links'])
            except ValueError:
                continue
                # print(dataText['anchorText'])

                # pprint(dataText['title'])


if __name__ == '__main__':
    resolve('resources/example.txt', 'http://dbpedia.org/resource/Donald_Trump')
    resolve('resources/barack_obama.txt', 'http://dbpedia.org/resource/Barack_Obama')
    resolve('resources/ceres.txt', 'http://dbpedia.org/resource/Ceres_(dwarf_planet)')
    resolve('resources/germany.txt', 'http://dbpedia.org/resource/Germany')
    resolve('resources/paris.txt', 'http://dbpedia.org/resource/Paris')
    resolve('resources/google.txt', 'http://dbpedia.org/resource/Google')
    resolve('resources/metallica.txt', 'http://dbpedia.org/resource/Metallica')
    resolve('resources/quantum_mechanics.txt', 'http://dbpedia.org/resource/Quantum_mechanics')
    resolve('resources/star_wars.txt', 'http://dbpedia.org/resource/Star_Wars')
    resolve('resources/sw_force_awakens.txt', 'http://dbpedia.org/resource/Star_Wars:_The_Force_Awakens')
    resolve('resources/michael_jackson.txt', 'http://dbpedia.org/resource/Michael_Jackson')

    resolveAndLinkArticles('/home/andfre/Downloads/short_enwiki_db_2016-10-20_with_db_links.json')
    # resolve('resources/jobs_new.txt')
    # lexiconGenderClassifier = LexiconGenderClassifier()
    # lexiconGenderClassifier.buildLexiconFromWikipedia('/home/andfre/Downloads/short_enwiki_db_2016-10-20_with_db_links.json')
