# Mr Data

Unified Data for the SemanticWeb

This is very early work, might be useful but it's unstable!

Guaranteed to change over time

- [Mr Data](#mr-data)
  * [Search](#search)
    + [ConceptNet](#conceptnet)
    + [DBPedia](#dbpedia)
    + [Wikidata](#wikidata)
    + [Wikipedia](#wikipedia)
    + [Genesis](#genesis)
    + [Openie](#openie)
    + [Wordnet](#wordnet)
    + [Dictionary](#dictionary)
  * [Base Data model](#base-data-model)
    + [Individuals vs Classes](#individuals-vs-classes)
    + [Properties](#properties)
    + [Everything is triples](#everything-is-triples)
      - [Triples Vocabulary](#triples-vocabulary)
  * [Data Storage](#data-storage)
    + [SQL Data Model](#sql-data-model)
      - [SQL Data Store](#sql-data-store)
    + [OWL Data Model](#owl-data-model)
      - [OWL Data Store](#owl-data-store)
    + [SKOS Data Model](#skos-data-model)
      - [SKOS Data Store](#skos-data-store)
    + [RDF Data Model](#rdf-data-model)
      - [RDF Data Store](#rdf-data-store)
  * [Queries](#queries)
    + [SQL queries](#sql-queries)
    + [SPARQL queries](#sparql-queries)
  * [Reasoning](#reasoning)
  * [Related Projects](#related-projects)
  
## Search

The internet is huge, data is structured in several forms, MrData provides 
apis to query the following data sources

- ConceptNet
- DbPedia
- WikiData
- Wikipedia
- Genesis
- OpenIE
- Wordnet
- Dictionary

Results can be normalized into triples for storage/reasoning

Some of these might support SPARQL, more on that in the [Queries](#Queries)
section

### ConceptNet

bla bla, conceptnet intro

```python
from mister_data.search.conceptnet import ConceptNet

engine = ConceptNet()
subject = "dog"
pprint(engine.query(subject))
pprint(engine.labels(subject))

```

sample raw output (truncated)

        {'@context': ['http://api.conceptnet.io/ld/conceptnet5.6/context.ld.json'],
         '@id': '/c/en/dog',
         'edges': [{'@id': '/a/[/r/CapableOf/,/c/en/dog/,/c/en/bark/]',
                    '@type': 'Edge',
                    'dataset': '/d/conceptnet/4/en',
                    'end': {'@id': '/c/en/bark',
                            '@type': 'Node',
                            'label': 'bark',
                            'language': 'en',
                            'term': '/c/en/bark'},
                    'license': 'cc:by/4.0',
                    'rel': {'@id': '/r/CapableOf',
                            '@type': 'Relation',
                            'label': 'CapableOf'},
                    'sources': [{'@id': '/and/[/s/activity/omcs/commons2_template/,/s/contributor/omcs/reine/]',
                                 '@type': 'Source',
                                 'activity': '/s/activity/omcs/commons2_template',
                                 'contributor': '/s/contributor/omcs/reine'},
                                 
                                 ...
                     ],
                'start': {'@id': '/c/en/dog',
                          '@type': 'Node',
                          'label': 'dog',
                          'language': 'en',
                          'term': '/c/en/dog'},
                'surfaceText': '[[dog]] can [[bark]]',
                'weight': 16.0},
               {'@id': '/a/[/r/CapableOf/,/c/en/dog/,/c/en/guard_house/]',
               
               ...
         }
         
sample label triples output

        [('dog', 'CapableOf', 'bark'),
         ('A dog', 'CapableOf', 'guard your house'),
         ('dog', 'RelatedTo', 'pet'),
         ('dog', 'RelatedTo', 'animal'),
         ('a dog', 'AtLocation', 'a kennel'),
         ('flea', 'RelatedTo', 'dog'),
         ('dog', 'RelatedTo', 'canine'),
         ('A dog', 'CapableOf', 'be a pet'),
         ('A dog', 'IsA', 'a loyal friend'),
         ('a dog', 'UsedFor', 'companionship'),
         ('a dog', 'CapableOf', 'run'),
         ('a dog', 'IsA', 'pet'),
         ('the dog', 'AtLocation', 'the table'),
         ('A dog', 'CapableOf', 'guide a blind person'),
         ('a dog', 'Desires', 'a bone'),
         ('A dog', 'HasA', 'four legs'),
         ('a dog', 'IsA', 'mammal'),
         ('a dog', 'AtLocation', 'a park'),
         ('a dog', 'Desires', 'be petted'),
         ('A dog', 'IsA', 'a canine')]

### DBPedia

bla bla, dbpedia  intro

```python
from mister_data.search.dbpedia import DBPedia

engine = DBPedia()
subject = "dog"
pprint(engine.query(subject))
pprint(engine.labels(subject))

```
sample raw output (truncated)

    {'results': [{'categories': [{'label': 'Scavengers',
                              'uri': 'http://dbpedia.org/resource/Category:Scavengers'},
                             {'label': 'Cosmopolitan species',
                              'uri': 'http://dbpedia.org/resource/Category:Cosmopolitan_species'},
                             {'label': 'Dogs',
                              'uri': 'http://dbpedia.org/resource/Category:Dogs'},
                             {'label': 'Sequenced genomes',
                              'uri': 'http://dbpedia.org/resource/Category:Sequenced_genomes'}],
              'classes': [{'label': 'mammal',
                           'uri': 'http://dbpedia.org/ontology/Mammal'},
                          {'label': 'owl#Thing',
                           'uri': 'http://www.w3.org/2002/07/owl#Thing'},
                          {'label': 'animal',
                           'uri': 'http://dbpedia.org/ontology/Animal'},
                          {'label': 'species',
                           'uri': 'http://dbpedia.org/ontology/Species'},
                          {'label': 'eukaryote',
                           'uri': 'http://dbpedia.org/ontology/Eukaryote'}],
              'description': 'The domestic dog (Canis lupus familiaris), is a '
                             'subspecies of the gray wolf (Canis lupus), a '
                             'member of the Canidae family of the mammilian '
                             'order Carnivora. The term "domestic dog" is '
                             'generally used for both domesticated and feral '
                             'varieties. The dog may have been the first '
                             'animal to be domesticated, and has been the most '
                             'widely kept working, hunting, and companion '
                             'animal in human history.',
              'label': 'Dog',
              'redirects': [],
              'refCount': 2684,
              'templates': [],
              'uri': 'http://dbpedia.org/resource/Dog'},
             {'categories': [{'label': 'People self-identifying as substance '
                                       'abusers',
                              'uri': 'http://dbpedia.org/resource/Category:People_self-identifying_as_substance_abusers'},
                             {'label': 'Rappers from Los Angeles, California',
                              'uri': 'http://dbpedia.org/resource/Category:Rappers_from_Los_Angeles,_California'},
                             ...
                             {'label': 'People from Long Beach, California',
                              'uri': 'http://dbpedia.org/resource/Category:People_from_Long_Beach,_California'},
                             {'label': '1971 births',
                              'uri': 'http://dbpedia.org/resource/Category:1971_births'}],
              'classes': [{'label': 'owl#Thing',
                           'uri': 'http://www.w3.org/2002/07/owl#Thing'},
                          {'label': 'person',
                           'uri': 'http://dbpedia.org/ontology/Person'},
                          {'label': 'artist',
                           'uri': 'http://dbpedia.org/ontology/Artist'},
                          {'label': 'musical artist',
                           'uri': 'http://dbpedia.org/ontology/MusicalArtist'},
                          {'label': 'music group',
                           'uri': 'http://schema.org/MusicGroup'},
                          {'label': 'person',
                           'uri': 'http://schema.org/Person'},
                          {'label': 'http://xmlns.com/foaf/0.1/ person',
                           'uri': 'http://xmlns.com/foaf/0.1/Person'},
                          {'label': 'agent',
                           'uri': 'http://dbpedia.org/ontology/Agent'}],
              'description': 'Calvin Cordozar Broadus, Jr. (born October 20, '
                             '1971), better known by his stage name Snoop Dogg '
                             '(formerly known as Snoop Doggy Dogg), is an '
                             'American rapper, record producer, and actor. '
                             'Snoop is best known as a rapper in the West '
                             'Coast hip hop scene, and for being one of Dr. '
                             "Dre's most notable protégés. Snoop Dogg was a "
                             'Crip gang member while in high school. Shortly '
                             'after graduation, he was arrested for cocaine '
                             'possession and spent six months in Wayside '
                             'County Jail.',
              'label': 'Snoop Dogg',
              'redirects': [],
              'refCount': 1689,
              'templates': [],
              'uri': 'http://dbpedia.org/resource/Snoop_Dogg'},
              ...
        
label triples (truncated)

        [('Scavengers', 'uri', 'http://dbpedia.org/resource/Category:Scavengers'),
         ('Dog', 'categorie', 'Scavengers'),
         ('Cosmopolitan species',
          'uri',
          'http://dbpedia.org/resource/Category:Cosmopolitan_species'),
         ('Dog', 'categorie', 'Cosmopolitan species'),
         ('Dogs', 'uri', 'http://dbpedia.org/resource/Category:Dogs'),
         ('Dog', 'categorie', 'Dogs'),
         ('Sequenced genomes',
          'uri',
          'http://dbpedia.org/resource/Category:Sequenced_genomes'),
         ('Dog', 'categorie', 'Sequenced genomes'),
         ('mammal', 'uri', 'http://dbpedia.org/ontology/Mammal'),
         ('Dog', 'isA', 'mammal'),
         ('owl#Thing', 'uri', 'http://www.w3.org/2002/07/owl#Thing'),
         ('Dog', 'isA', 'owl#Thing'),
         ('animal', 'uri', 'http://dbpedia.org/ontology/Animal'),
         ('Dog', 'isA', 'animal'),
         ('species', 'uri', 'http://dbpedia.org/ontology/Species'),
         ('Dog', 'isA', 'species'),
         ('eukaryote', 'uri', 'http://dbpedia.org/ontology/Eukaryote'),
         ('Dog', 'isA', 'eukaryote'),
         ('Dog',
          'description',
          'The domestic dog (Canis lupus familiaris), is a subspecies of the gray wolf '
          '(Canis lupus), a member of the Canidae family of the mammilian order '
          'Carnivora. The term "domestic dog" is generally used for both domesticated '
          'and feral varieties. The dog may have been the first animal to be '
          'domesticated, and has been the most widely kept working, hunting, and '
          'companion animal in human history.'),
         ('Dog', 'uri', 'http://dbpedia.org/resource/Dog'),
         ('People self-identifying as substance abusers',
          'uri',
          'http://dbpedia.org/resource/Category:People_self-identifying_as_substance_abusers'),
         ('Snoop Dogg', 'categorie', 'People self-identifying as substance abusers'),
         ...
        

### Wikidata

bla bla, wikidata intro

```python
from mister_data.search.wikidata import Wikidata

engine = Wikidata()
subject = "dog"
pprint(engine.query(subject))
pprint(engine.labels(subject))

```
sample raw output (truncated)

    {
    ...
     'alias': ['domestic dog'],
     'bite force quotient (P3485)': {'amount': '+117', 'unit': '1'},
     'described by source (P1343)': 'Ottův slovník naučný (Q2041543)',
     'description': 'domestic animal',
     'earliest date (P1319)': '-34000-00-00T00:00:00Z',
     'exact match (P2888)': ['http://globalwordnet.org/ili/i46360',
                             'http://wordnet-rdf.princeton.edu/wn30/02084071-n',
                             'http://odwn-rdf.vu.nl/odwn13/02084071-n',
                             'http://wordnet-rdf.princeton.edu/wn31/102086723-n'],
    ...
     'instance of (P31)': 'group of organisms known by one particular common name '
                          '(Q55983715)',
     'label': ['Q152457',
               ...
               'P3479'],
     'maximum frequency of audible sound (P3465)': {'amount': '+45000',
                                                    'unit': 'http://www.wikidata.org/entity/Q39369'},
     'minimum frequency of audible sound (P3387)': {'amount': '+67',
                                                    'unit': 'http://www.wikidata.org/entity/Q39369'},
     'on focus list of Wikimedia project (P5008)': 'Wikipedia:Vital articles '
                                                   '(Q5460604)',
     'patron saint (P417)': ['Saint Roch (Q152457)',
                             'Hubertus (Q159834)',
                             'Vitus (Q212850)'],
     'produced sound (P4733)': ['bark (Q38681)',
                                'growling (Q1188507)',
                                'panting (Q1592884)'],
     'subclass of (P279)': ['domesticated mammal (Q57814795)', 'pet (Q39201)'],
     'subreddit (P3984)': 'dogs',
     'taxon common name (P1843)': ['Okraman',
                                    ...
                                   'dog',
                                   '狗',
                                   'Hond',
                                   'perru',
                                   'perra',
                                   'perro',
                                   'perra',
                                   'chó'],
     'title': 'Dog',
     "topic's main category (P910)": 'Category:Dogs (Q6830323)',
     'use (P366)': ['pet (Q39201)',
                    'hunting (Q36963)',
                    'guard (Q680928)',
                    'service animal (Q2827808)'],
     'uses (P2283)': 'dog bed (Q54502633)',
     'what': 'group of organisms known by one particular common name'}

sample label triples output

        
        [
        ...
         ('dog', 'subreddit (P3984)', 'dogs'),
         ('dog', 'BabelNet ID (P2581)', '00015267n'),
         ('dog', 'GND ID (P227)', '4026181-5'),
         ('dog', 'Canadian Encyclopedia article ID (P5395)', 'dog'),
         ('dog', 'NYT topic ID (P3221)', 'subject/dogs'),
         ('dog', 'Omni topic ID (P3479)', 'b2d0ab32-ad92-486a-8ff3-c85fc06bdb01'),
         ('dog', 'what', 'group of organisms known by one particular common name'),
         ('dog', 'ILI ID (P5063)', 'i46360'),
         ('dog', 'UNSPSC Code (P2167)', '10101502'),
         ('dog', 'JSTOR topic ID (P3827)', 'dogs'),
         ('dog', 'PSH ID (P1051)', '886'),
         ('dog', 'earliest date (P1319)', '-34000-00-00T00:00:00Z'),
         ('dog', "topic's main category (P910)", 'Category:Dogs (Q6830323)'),
         ('dog', 'Commons category (P373)', 'Dogs'),
         ('dog', 'use (P366)', 'pet (Q39201)'),
         ('dog', 'use (P366)', 'hunting (Q36963)'),
         ('dog', 'use (P366)', 'guard (Q680928)'),
         ('dog', 'use (P366)', 'service animal (Q2827808)'),
         ('Dog heart rate (P3395)', 'unit', 'http://www.wikidata.org/entity/Q743895'),
         ('Dog heart rate (P3395)', 'amount', '+95'),
         ('Dog heart rate (P3395)', 'lowerBound', '+70'),
         ('Dog heart rate (P3395)', 'upperBound', '+120'),
         ('Dog heart rate (P3395)', 'unit', 'http://www.wikidata.org/entity/Q743895'),
         ('Dog heart rate (P3395)', 'amount', '+115'),
         ('Dog heart rate (P3395)', 'lowerBound', '+100'),
         ('Dog heart rate (P3395)', 'upperBound', '+130'),
         ('Dog heart rate (P3395)', 'unit', 'http://www.wikidata.org/entity/Q743895'),
         ('Dog heart rate (P3395)', 'amount', '+80'),
         ('dog', 'Great Russian Encyclopedia Online ID (P2924)', '3588376'),
         ('Dog maximum frequency of audible sound (P3465)',
          'unit',
          'http://www.wikidata.org/entity/Q39369'),
         ('Dog maximum frequency of audible sound (P3465)', 'amount', '+45000'),
         ('dog', 'alias', 'domestic dog')] 

### Wikipedia

bla bla bla, wikipedia intro

Wikipedia is not great for structured data, DbPedia and Wikidata are usually
 better options with same content

```python
from mister_data.search.wikipedia import Wikipedia

engine = Wikipedia()
subject = "dog"
pprint(engine.query(subject))
pprint(engine.labels(subject))

```

sample raw output

        {'alias': ['domestic dog'],
         'description': 'domestic animal',
         'label': 'dog',
         'summary': 'The **domestic dog** ( _Canis lupus familiaris_ when considered a '
                    'subspecies\n'
                    'of the wolf or _Canis familiaris_ when considered a distinct '
                    'species) is a\n'
                    'member of the genus _Canis_ (canines), which forms part of the '
                    'wolf-like\n'
                    'canids, and is the most widely abundant terrestrial carnivore. '
                    'The dog and the\n'
                    'extant gray wolf are sister taxa as modern wolves are not closely '
                    'related to\n'
                    'the wolves that were first domesticated, which implies that the '
                    'direct\n'
                    'ancestor of the dog is extinct. The dog was the first species to '
                    'be\n'
                    'domesticated and has been selectively bred over millennia for '
                    'various\n'
                    'behaviors, sensory capabilities, and physical attributes.\n'
                    '\n'
                    'Their long association with humans has led dogs to be uniquely '
                    'attuned to\n'
                    'human behavior and they are able to thrive on a starch-rich diet '
                    'that would be\n'
                    'inadequate for other canid species. Dogs vary widely in shape, '
                    'size and\n'
                    'colors. Dogs perform many roles for humans, such as hunting, '
                    'herding, pulling\n'
                    'loads, protection, assisting police and military, companionship '
                    'and, more\n'
                    'recently, aiding disabled people and therapeutic roles. This '
                    'influence on\n'
                    'human society has given them the sobriquet of "man\'s best '
                    'friend".',
         'title': 'Dog',
         'wikibaseID': 'Q144',
         'wikidata_url': 'https://www.wikidata.org/wiki/Q144',
         'wikipedia_pageid': 4269567,
         'wikipedia_url': 'https://en.wikipedia.org/wiki/Dog'}
         
labels triples output

            [('dog', 'wikipedia_url', 'https://en.wikipedia.org/wiki/Dog'),
             ('dog', 'description', 'domestic animal'),
             ('dog', 'wikibaseID', 'Q144'),
             ('dog', 'wikidata_url', 'https://www.wikidata.org/wiki/Q144'),
             ('dog', 'alias', 'domestic dog'),
             ('dog', 'label', 'dog'),
             ('dog', 'title', 'Dog'),
             ('dog',
              'summary',
              'The **domestic dog** ( _Canis lupus familiaris_ when considered a '
              'subspecies\n'
              'of the wolf or _Canis familiaris_ when considered a distinct species) is a\n'
              'member of the genus _Canis_ (canines), which forms part of the wolf-like\n'
              'canids, and is the most widely abundant terrestrial carnivore. The dog and '
              ...
              'loads, protection, assisting police and military, companionship and, more\n'
              'recently, aiding disabled people and therapeutic roles. This influence on\n'
              'human society has given them the sobriquet of "man\'s best friend".')]
              

### Genesis

bla bla, intro to http://genesis.aksw.org/

```python
from mister_data.search.genesis import Genesis

engine = Genesis()
subject = "dog"
pprint(engine.query(subject))
pprint(engine.labels(subject))

```

sample raw output (truncated)

        [{'description': 'The domestic dog (Canis lupus familiaris or Canis '
                 'familiaris) is a domesticated canine which has been '
                 'selectively bred over millennia for various behaviours, '
                 'sensory capabilities, and physical attributes. Although '
                 'initially thought to have originated as an artificial '
                 'variant of an extant canid species (variously supposed as '
                 'being the dhole, golden jackal, or gray wolf), extensive '
                 'genetic studies undertaken during the 2010s indicate that '
                 'dogs diverged from an extinct wolf-like canid in Eurasia '
                 '40,000 years ago. Their long association with humans has led '
                 'to dogs being uniquely attuned to human behavior and are '
                 'able to thrive on a starch-rich diet which would be '
                 'inadequate for other canid species. Dogs are also the oldest '
                 'domesticated animal. Dogs vary widely in shape, size and '
                 'colours. Dogs perform many roles for people, such as '
                 'hunting, herding, pulling loads, protection, assisting '
                 'police and military, companionship and, more recently, '
                 'aiding handicapped individuals. This influence on human '
                 'society has given them the sobriquet, "man\'s best friend".',
          'image': 'http://commons.wikimedia.org/wiki/Special:FilePath/Collage_of_Nine_Dogs.jpg?width=300',
          'title': 'Dog',
          'url': 'http://dbpedia.org/resource/Dog'},
         
         ...
         
         {'description': 'Good Dog, Bad Dog is the fourth studio album by Over the '
                         'Rhine, released independently in 1996, and reissued with a '
                         'slightly altered track listing by Virgin/Backporch in 2000.',
          'image': 'http://placehold.it/350x150',
          'title': 'Good Dog Bad Dog',
          'url': 'http://dbpedia.org/resource/Good_Dog,_Bad_Dog'},
         {'description': 'Dog Mountain is a unique farm in St. Johnsbury, Vermont with '
                         '150 acres of scenic trails, trout ponds, dog sculptures, an '
                         'art gallery and the popular Dog Chapel. It was run by '
                         'Vermont artists Stephen Huneck and Gwen Huneck until their '
                         "deaths. Gwen's brother, Jonathan Ide of Fitchburg, "
                         'Wisconsin, is directing the business.',
          'image': 'http://placehold.it/350x150',
          'title': 'Dog Mountain Dog Park',
          'url': 'http://dbpedia.org/resource/Dog_Mountain_(dog_park)'},
         {'description': 'A hot dog (also spelled hotdog) is a cooked sausage, '
                         'traditionally grilled or steamed and served in a sliced bun '
                         'as a sandwich. Hot dog variants include the corn dog and '
                         'pigs in blankets. Typical hot dog garnishes include mustard, '
                         'ketchup, onions, mayonnaise, relish, coleslaw, cheese, '
                         'chili, olives, and sauerkraut. This kind of sausage was '
                         'culturally imported from Germany and popularized in the '
                         'United States, where it became a working-class street food '
                         'sold at hot dog stands and hot dog carts, and developed an '
                         'association with baseball and American culture. Hot dog '
                         'preparation and condiment styles vary regionally in the US. '
                         'Although linked in particular with New York City and New '
                         'York City cuisine, the hot dog became ubiquitous throughout '
                         'the United States during the 20th century, becoming an '
                         'important part of other regional cuisines, most notably '
                         "Chicago street cuisine. The hot dog's cultural traditions "
                         "include the Nathan's Hot Dog Eating Contest and the Oscar "
                         'Mayer Wienermobile.',
          'image': 'http://commons.wikimedia.org/wiki/Special:FilePath/Hot_dog_with_mustard.png?width=300',
          'title': 'Hot Dog',
          'url': 'http://dbpedia.org/resource/Hot_dog'},
         {'description': 'Dog breeds are dogs that have relatively uniform physical '
                         'characteristics developed under controlled conditions by '
                         'humans, with breeding animals selected for phenotypic traits '
                         'such as size, coat color, structure, and behavior. The '
                         'Fédération Cynologique Internationale recognizes over 400 '
                         'pure dog breeds. Other uses of the term breed when referring '
                         'to dogs may include pure breeds, cross-breeds, mixed breeds '
                         'and natural breeds.',
          'image': 'http://commons.wikimedia.org/wiki/Special:FilePath/Big_and_little_dog_1.jpg?width=300',
          'title': 'Dog Breed',
          'url': 'http://dbpedia.org/resource/Dog_breed'},
         {'description': 'A police dog, known as a "K-9" or "K9" (a homophone of '
                         '"canine") in some English-speaking countries, is a dog that '
                         'is specifically trained to assist police and other '
                         'law-enforcement personnel in their work. Their duties '
                         'include searching for drugs and explosives, searching for '
                         'lost people, looking for crime scene evidence, and '
                         'protecting their handlers. Police dogs must remember several '
                         'hand and verbal commands. The most commonly used breed is '
                         'the German Shepherd. In many common law jurisdictions, the '
                         'intentional injuring or killing of a police dog is a felony.',
          'image': 'http://commons.wikimedia.org/wiki/Special:FilePath/Swedish_police_dogs.jpg?width=300',
          'title': 'Police Dog',
          'url': 'http://dbpedia.org/resource/Police_dog'},
          
          ...
  
label triples output (truncated)

        [
        ...
        
         ('Dog Sled',
          'description',
          'A dog sled or dog sleigh is a sled pulled by one or more sled dogs used to '
          'travel over ice and through snow. Numerous types of sleds are used, '
          'depending on their function. They can be used for dog sled racing.'),
         ('Herding Dog', 'title', 'Herding Dog'),
         ('Herding Dog',
          'image',
          'http://commons.wikimedia.org/wiki/Special:FilePath/Kelpie_walking_across_the_backs_of_sheep.jpg?width=300'),
         ('Herding Dog', 'url', 'http://dbpedia.org/resource/Herding_dog'),
         ('Herding Dog',
          'description',
          'A herding dog, also known as a stock dog or working dog, is a type of '
          'pastoral dog that either has been trained in herding or belongs to breeds '
          'developed for herding. Their ability to be trained to act on the sound of a '
          'whistle or word of command is renowned throughout the world. Collies are '
          'recommended as herding dogs.'),
         ('Chihuahua Dog', 'title', 'Chihuahua Dog'),
         ('Chihuahua Dog',
          'image',
          'http://commons.wikimedia.org/wiki/Special:FilePath/Chihuahua1_bvdb.jpg?width=300'),
         ('Chihuahua Dog', 'url', 'http://dbpedia.org/resource/Chihuahua_(dog)'),
         ('Chihuahua Dog',
          'description',
          'The Chihuahua /tʃɪˈwɑːwɑː/ (Spanish: chihuahueño) is the smallest breed of '
          'dog and is named for the state of Chihuahua in Mexico. Chihuahuas come in a '
          'wide variety of sizes, head shapes, colors, and coat lengths.')]
  

### Openie

bla bla, intro to http://openie.allenai.org

NOTE: very slow, randomly fails, relies on bs4 webscrapping

```python
from mister_data.search.openie import Openie

engine = Openie()

pprint(engine.labels("bacteria"))

# more complex queries can be made
arg1 = "what"
rel = "kills"
arg2 = "bacteria"
corpora = ""
query = '?arg1=%s&rel=%s&arg2=%s&corpora=%s' % (arg1, rel, arg2, corpora)
result = engine.query(query)
```

raw (truncated)

        [{'answer': 'Antibiotic', 'relationship': 'kill'},
         {'answer': 'Yoghurt', 'relationship': 'contains'},
         {'answer': 'Antibiotic', 'relationship': 'destroy'},
         {'answer': 'Antibiotic', 'relationship': 'kill off'},
         ...
         ]
 
sample labels output


        [('Cholera', 'is caused by', 'bacteria'),
         ('Cholera', 'is an illness caused by', 'bacteria'),
         ('Cholera', 'is', 'bacteria'),
         ('Cholera', 'is a bacterial disease caused by', 'bacteria'),
         ('Plague (disease)', 'is caused by', 'bacteria'),
         ('Plague (disease)', 'is a bacterial disease caused by', 'bacteria'),
         ('Bacteria', 'called', 'bacteria'),
         ('Plague (disease)', 'is a bacterial infection caused by', 'bacteria'),
         ('Black Death', 'is caused by', 'bacteria')]
 
 
 
### Wordnet

bla bla, ntlk, bla wordnet intro

sample raw output

        {'antonyms': [],
         'definition': 'a member of the genus Canis (probably descended from the '
                       'common wolf) that has been domesticated by man since '
                       'prehistoric times; occurs in many breeds',
         'holonyms': ['canis', 'pack'],
         'hypernyms': ['canine', 'domestic animal'],
         'hyponyms': ['basenji',
                      'corgi',
                      'cur',
                      'dalmatian',
                      'great pyrenees',
                      'griffon',
                      'hunting dog',
                      'lapdog',
                      'leonberg',
                      'mexican hairless',
                      'newfoundland',
                      'pooch',
                      'poodle',
                      'pug',
                      'puppy',
                      'spitz',
                      'toy dog',
                      'working dog'],
         'lemmas': ['dog', 'domestic dog', 'Canis familiaris'],
         'root_hypernyms': ['entity']}
 
sample label triples output

        [('dog',
          'definition',
          'a member of the genus Canis (probably descended from the common wolf) that '
          'has been domesticated by man since prehistoric times; occurs in many '
          'breeds'),
         ('dog', 'synset', 'dog.n.01'),
         ('dog', 'synset', 'frump.n.01'),
         ('dog', 'synset', 'dog.n.03'),
         ('dog', 'synset', 'cad.n.01'),
         ('dog', 'synset', 'frank.n.02'),
         ('dog', 'synset', 'pawl.n.01'),
         ('dog', 'synset', 'andiron.n.01'),
         ('dog', 'lemma', 'dog'),
         ('dog', 'same as', 'dog'),
         ('dog', 'synonym', 'dog'),
         ('dog', 'lemma', 'domestic dog'),
         ('dog', 'same as', 'domestic dog'),
         ('dog', 'synonym', 'domestic dog'),
          ...
         ('dog', 'hyponym', 'toy dog'),
         ('dog', 'instance of', 'toy dog'),
         ('dog', 'hyponym', 'working dog'),
         ('dog', 'instance of', 'working dog'),
         ('dog', 'instance of', 'canine'),
         ('dog', 'hypernym', 'canine'),
         ('dog', 'label', 'canine'),
         ('dog', 'instance of', 'domestic animal'),
         ('dog', 'hypernym', 'domestic animal'),
         ('dog', 'label', 'domestic animal'),
         ('dog', 'instance of', 'entity'),
         ('dog', 'root_hypernym', 'entity'),
         ('dog', 'hypernym', 'entity')]
           

### Dictionary

Mostly an alternative to dictionary, downloads corpus if needed

bla bla, https://pypi.org/project/Vocabulary/ intro

```python
from mister_data.search.dictionary import Dictionary

engine = Dictionary()
subject = "dog"
pprint(engine.labels(subject))

```
        
label triples (truncated)

        [('dog', 'meaning', 'A hot dog.'),
         ('dog', 'meaning', 'A sexually aggressive man (cf. horny).'),
         ...
         ('dog',
          'meaning',
          'An animal, member of the genus Canis (probably descended from the common '
          'wolf) that has been domesticated for thousands of years; occurs in many '
          'breeds. Scientific name: Canis lupus familiaris.'),         
         ('dog',
          'meaning',
          'A common four-legged animal, especially kept by people as a pet or to hunt '
          'or guard things.'),
         ('dog', 'synonym', 'trace'),
         ('dog', 'synonym', 'spy'),
         ('dog', 'synonym', 'stalk'),
         ('dog', 'synonym', 'doggy'),
         ('dog', 'synonym', 'hound'),
         ('dog', 'synonym', 'follow'),
         ('dog', 'synonym', 'trail'),
         ...
         ('dog', 'usage_example', 'Me: [hello doggy]Dog: ([licks])Me: ghaaaaa'),
         ('dog', 'usage_example', '"omg [dogs] are so [perfect] [I love] them"'),
         ('dog', 'usage_example', '[Mom can] we [get a dog]'),
         ('dog', 'usage_example', "Dog- your [my best] friendI'll [die] [for you]."),
         ('dog', 'usage_example', '[i love] dog')
         ...
             

## Base Data model

A base data model was created to be used as reference

- Everything is represented as a MrDataThing
- MrDataThings have a unique URI and a list of properties
- MrDataProperties are also MrDataThings
- MrDataProperties also have a source and a target object

```python
from mister_data.data_models import MrDataThing, MrDataProperty

thing = MrDataThing("thing#1")
print(thing.has_for_property)  # list of properties

prop = MrDataProperty("some value")
print(prop.property_of)  # None / not assigned
print(prop.has_value)  # "some value"

```

### Individuals vs Classes

Individuals are instances of classes, they are something

Classes are "Concepts", they describe something

```python
from mister_data.data_models import MrDataThing

# Describe Concepts
class Animal(MrDataThing):
    uri = "mrdata:Animal"

dog = Animal("dog")
print(Animal.uri)  # class -> "mrdata:Animal"
print(dog.uri)  # individual -> "mrdata_ex:dog

```

### Properties

since MrDataProperties are also MrDataThings, properties also have classes and instances
 
only property instances can have values

```python

from mister_data.data_models import MrDataProperty


# Describe Properties
class Is_A(MrDataProperty):
    uri = "mrdata_prop:Is_A"

# MrDataSQLProperty classes
print(Is_A.uri)  # "mrdata_prop:Is_A"

# MrDataSQLProperty instances
prop = Is_A(Animal)
print(prop.uri)  # "mrdata_ex:Is_A"
print(prop.has_value)  # <class '__main__.Animal'>
print(prop.property_of)  # None , does not belong to any individuals
```

You may define properties for classes

- When classes have properties, all individuals of that class also have that property

```python

# Class Properties
class Dog(MrDataThing):
    uri = "mrdata:Dog"
    class_properties = [Is_A(Animal)]


print(Animal.class_properties)  # no class properties
print(Dog.class_properties)  # is_a Animal
```

Or we can assign properties for individuals only

- Individuals have at least their parent class properties
- Properties of individuals do not necessarily belong to their class

```python
class FourLeggedThing(MrDataThing):
    uri = "mrdata:FourLeggedThing"
    
dog.add_property(Is_A(FourLeggedThing))
print(dog.has_for_property)  # Is_A Animal, Is_A FourLeggedThing
print(dog.class_properties)  # Is_A Animal
```


Sometimes we want to only allow a single instance (per individual) for a property

- when a unique property is assigned to a individual it replaces properties with same uri

- if classes have unique properties individuals can not assign new properties with same uri

```python

# Unique/Functional property
class Age(UniqueProperty):
    uri = "mrdata_prop:Age"
    
cat = Cat("MyCat")
cat.add_property(Age(10))
print(cat.has_for_property)  # 1x age 10
# unique properties are replaced
cat.add_property(Age(6))
print(cat.has_for_property)  # 1x age 6
    
```

Properties can also be assigned to individuals when instantiated

```python
# assign on property creation

age = Age(10, cat)
assert age in cat.has_for_property
print(age.property_of)  # mrdata_ex:MyCat
try:
    age = Age(10, Cat)
except AssertionError:
    print("Can't assign to classes, must be declared")

```

### Everything is triples

- MrDataThings can always be expressed as triples
- MrDataThings are connected to MrDataProperties by "mrdata:has_property" 
- MrDataProperties are connected to values by "mrdata:has_value"



       'mrdata_ex:Mything', 'mrdata:has_property', 'mrdata_prop:some_prop'
       'mrdata_prop:some_prop', 'mrdata:has_value', 'value_of_prop'
       'mrdata_prop:some_prop#2', 'mrdata:has_value', 'mrdata_ex:MyThing#2'
    
    
#### Triples Vocabulary

Triples will use the following vocabulary, sufficient to express all 
relationships

- "mrdata:thing" -> class of things
- "mrdata:property" -> class of properties
- "mrdata:X" -> X is a class
- "mrdata_ex:X" -> X is an instance of a thing
- "mrdata_prop:X" -> X is an instance of a property
- "X:Y" -> class for property of a thing, X is an instance of a thing, Y is an instance of a property
- "mrdata:has_property" -> connects things to properties
- "mrdata:has_value" -> connects properties to values

```python
# Create Individuals
dog = Dog("jurebes")
dog.add_property(Age(6))
dog.add_property(Is_A(FourLeggedThing))
pprint(dog.as_triples())

```

will output the following triples

    [('mrdata_ex:jurebes', 'rdf:type', 'mrdata:Dog'),
    
     ('Is_A:Animal', 'rdf:type', 'mrdata_prop:Is_A'),
     ('Is_A:Animal', 'mrdata:has_value', 'mrdata:Animal'),
     ('mrdata_ex:jurebes', 'mrdata:has_property', 'Is_A:Animal'),
     
     ('jurebes:Age', 'rdf:type', 'mrdata_prop:Age'),
     ('jurebes:Age', 'mrdata:has_value', 6),
     ('mrdata_ex:jurebes', 'mrdata:has_property', 'jurebes:Age')]
     
this might look a bit confusing at first, remember properties are also things

Let's "read" these triples

    - "jurebes" is an instance of "Dog" thing
    
Being an animal is not exclusive to jurebes instance

    - "is_a_animal" is an instance of "is_a" property
    - "is_a_animal" has the value of "Animal" thing
    - "jurebes" has the property "is_a_animal"
  
Having "Jurebes Age" is exclusive to jurebes instance
  
    - "jurebes_age" is an instance of "age" property
    - "jurebes_age" has the value of 6
    - "jurebes" has the property "jurebes_age"
       
    

## Data Storage

To store data lots of options exist, it's not always clear what the best way is

MrData provides models to store data in several schemes

- MrData objects are considered equal if their triples are equal
- All MrData objects can be represented as triples
- All MrData objects have a method to convert to a different model

Bellow is an overview of each model type

NOTE: work in progress subject to change 

All models should expose similar apis as demonstrated, plus extra functionality

```python
from mister_data.data_models import MrDataProperty, MrDataThing, \
    UniqueProperty
from mister_data.data_models.sql import MrDataSQLThing, MrDataSQLProperty, \
    MrDataSQLConnection
from mister_data.data_models.skos import MrDataSkosProperty, MrDataSkosThing
from mister_data.data_models.owl import MrDataOwlProperty, MrDataOwlThing

expected_prop = [
    ('Related_to:Laura', 'rdf:type', 'mrdata_prop:Related_to'),
    ('mrdata_ex:Laura', 'rdf:type', 'mrdata:Cat'),
    ('Related_to:Laura', 'mrdata:has_value', 'mrdata_ex:Laura')
]

expected_dog = [
    ('mrdata_ex:jurebes', 'rdf:type', 'mrdata:Dog'),
    ('Related_to:Cat', 'rdf:type', 'mrdata_prop:Related_to'),
    ('Related_to:Cat', 'mrdata:has_value', 'mrdata:Cat'),
    ('mrdata_ex:jurebes', 'mrdata:has_property', 'Related_to:Cat'),
    ('jurebes:Laura', 'rdf:type', 'Related_to:Cat'),
    ('mrdata_ex:Laura', 'rdf:type', 'mrdata:Cat'),
    ('jurebes:Laura', 'mrdata:has_value', 'mrdata_ex:Laura'),
    ('mrdata_ex:jurebes', 'mrdata:has_property', 'jurebes:Laura')
]

expected_cat = [('mrdata_ex:Laura', 'rdf:type', 'mrdata:Cat')]

expected_class = [('mrdata:Mammal', 'rdf:type', 'mrdata:Animal')]

dog_uri = "mrdata_ex:jurebes"
cat_uri = "mrdata_ex:Laura"
mammal_uri = "mrdata:Mammal"
prop_uri = "Related_to:Laura"
prop_class_uri = "mrdata_prop:Related_to"

```

### SQL Data Model

A sqlAlchemy data model is provided

- MrDataSQLThing
- MrDataSQLProperty - values are strings
- MrDataSQLConnection - same as MrDataSQLProperty, but values are MrDataSQLThings

```python
class Related_to(MrDataSQLConnection):
    pass

class Animal(MrDataSQLThing):
    pass

class Mammal(Animal):
    pass

class Cat(Mammal):
    pass

class Dog(Mammal):
    class_properties = [Related_to(Cat)]

dog = Dog("jurebes")

assert dog.uri == dog_uri

cat = Cat("Laura")

assert cat.uri == cat_uri

mammal_class = Mammal()

assert mammal_class.uri == mammal_uri

prop = Related_to(cat)

assert Related_to().uri == prop_class_uri

assert prop.uri == prop_uri

assert mammal_class.as_triples() == expected_class

assert cat.as_triples() == expected_cat

assert prop.as_triples() == expected_prop

dog.add_property(prop)
# TODO fix this, WIP, DO NOT USE
return

assert dog.as_triples() == expected_dog  # WRONG
```


#### SQL Data Store

sqlite db - WIP - WIP - WIP

### OWL Data Model

ontology

```python
class Related_to(MrDataOwlProperty):
    pass

class Animal(MrDataOwlThing):
    pass

class Mammal(Animal):
    pass

class Cat(Mammal):
    pass

class Dog(Mammal):
    class_properties = [Related_to(Cat)]

dog = Dog("jurebes")

assert dog.uri == dog_uri

cat = Cat("Laura")

assert cat.uri == cat_uri

mammal_class = Mammal()

assert mammal_class.uri == mammal_uri

assert Related_to().uri == prop_class_uri

assert cat.as_triples() == expected_cat

prop = Related_to(cat)

assert prop.uri == prop_uri

assert prop.as_triples() == expected_prop

assert mammal_class.as_triples() == expected_class

dog.add_property(prop)
assert dog.as_triples() == expected_dog

# owl extras
class Pet(MrDataOwlThing):
    pass

dog.used_for = [Pet]

pprint(dog.deduced_triples())
"""
[('is_a:MrDataOwlThing', 'rdf:type', 'mrdata:property'),
 ('is_a:MrDataOwlThing', 'mrdata:has_value', 'mrdata:MrDataOwlThing'),
 ('mrdata_ex:jurebes', 'mrdata:has_property', 'is_a:MrDataOwlThing'),
 ('is_a:Animal', 'rdf:type', 'mrdata:property'),
 ('is_a:Animal', 'mrdata:has_value', 'mrdata:Animal'),
 ('mrdata_ex:jurebes', 'mrdata:has_property', 'is_a:Animal')]
 """
# TODO relationship mutated cat object!!!!
# since now its a shared object, how do i know which is which?
# result is not incorrect, but contains extra (valid) triples
return
assert cat.as_triples() == expected_cat  # ERROR

```

#### OWL Data Store

owlready db - WIP - WIP - WIP


### SKOS Data Model

```python
    class Related_to(MrDataSkosProperty):
        pass

    class Animal(MrDataSkosThing):
        pass

    class Mammal(Animal):
        pass

    class Cat(Mammal):
        pass

    class Dog(Mammal):
        class_properties = [Related_to(Cat)]

    dog = Dog("jurebes")
    assert dog.uri == dog_uri

    cat = Cat("Laura")
    assert cat.uri == cat_uri

    mammal_class = Mammal()
    assert mammal_class.uri == mammal_uri

    assert Related_to().uri == prop_class_uri

    assert cat.as_triples() == expected_cat

    assert mammal_class.as_triples() == expected_class

    prop = Related_to(cat)
    assert prop.uri == prop_uri

    assert prop.as_triples() == expected_prop

    dog.add_property(prop)
    assert set(dog.as_triples()) == set(expected_dog)

    ## skos extras
    dog.add_synonym("jureboso")
    dog.definition = "my dog"
    pprint(dog.deduced_triples())
    """
    [('jurebes:SkosBroader', 'rdf:type', 'mrdata_prop:SkosBroader'),
     ('mrdata:Mammal', 'rdf:type', 'mrdata:Animal'),
     ('jurebes:SkosBroader', 'mrdata:has_value', 'mrdata:Mammal'),
     ('mrdata_ex:jurebes', 'mrdata:has_property', 'jurebes:SkosBroader'),
     ('jurebes:SkosSynonym', 'rdf:type', 'mrdata_prop:SkosSynonym'),
     ('jurebes:SkosSynonym', 'mrdata:has_value', 'jureboso'),
     ('mrdata_ex:jurebes', 'mrdata:has_property', 'jurebes:SkosSynonym'),
     ('jurebes:SkosPrefLabel', 'rdf:type', 'mrdata_prop:SkosPrefLabel'),
     ('jurebes:SkosPrefLabel', 'mrdata:has_value', 'jurebes'),
     ('mrdata_ex:jurebes', 'mrdata:has_property', 'jurebes:SkosPrefLabel'),
     ('jurebes:SkosDefinition', 'rdf:type', 'mrdata_prop:SkosDefinition'),
     ('jurebes:SkosDefinition', 'mrdata:has_value', 'my dog'),
     ('mrdata_ex:jurebes', 'mrdata:has_property', 'jurebes:SkosDefinition')]
    """
```

#### SKOS Data Store

WIP WIP WIP


### RDF Data Model

NOT EVEN STARTED


#### RDF Data Store

rdflib graphs - WIP - WIP - WIP

## Queries

Now that we have several ways to store data, how can we query those databases?

- WIP - WIP - WIP

### SQL queries

- WIP - WIP - WIP

### SPARQL queries

- WIP - WIP - WIP


## Reasoning

bla bla la, EYE reasoner with raw trples, bla bla Hermit and Pellet for 
ontology, bla bla bla converting across models

## Related Projects

https://bitbucket.org/jibalamy/owlready2
https://github.com/cosminbasca/surfrdf
https://github.com/gjhiggins/RDFAlchemy
https://github.com/NatLibFi/Skosify
https://github.com/koenedaele/skosprovider
