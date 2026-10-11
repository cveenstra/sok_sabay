"""Assemble data/*.json (run: python3 scripts/build_data.py) from the verified Wiktionary / Wikipedia extracts.
Also builds data/letters.json, the Letters course.

Every item's romanisation comes from Wiktionary's WT romanisation for that exact
spelling (verified.json). The English gloss is one of the senses Wiktionary lists;
gloss_check() fails the build if a gloss shares no word with the Wiktionary senses.
"""
import json, re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'source')
V = json.load(open(os.path.join(SRC, 'verified.json')))
OUT = os.path.join(HERE, '..', 'data')

def wt(km):
    r = V[km]
    assert r['status'] == 'ok' and r['wt'], f'{km} not verified'
    return re.split(r'\s*[,/]\s*', r['wt'][0])[0].strip()

# (id, khmer, english, category, note)
ITEMS = [
    # greetings & politeness
    ('hello', 'សួស្តី', 'hello', 'greet', None),
    ('hello-formal', 'ជម្រាបសួរ', 'hello (formal)', 'greet', 'Said with a sampeah to elders, teachers and people you respect.'),
    ('good-morning', 'អរុណសួស្តី', 'good morning', 'greet', None),
    ('goodbye', 'លាហើយ', 'goodbye, see you', 'greet', None),
    ('goodbye-formal', 'ជម្រាបលា', 'goodbye (formal)', 'greet', None),
    ('see-you-later', 'លាសិនហើយ', 'see you later', 'greet', None),
    ('thank-you', 'អរគុណ', 'thank you', 'polite', None),
    ('sorry', 'សូមទោស', 'sorry, excuse me', 'polite', None),
    ('its-ok', 'មិនអីទេ', "it's all right", 'polite', None),
    ('no-problem', 'អត់អី', "no problem, you're welcome", 'polite', None),
    ('please', 'សូម', 'please', 'polite', 'Used at the start of a polite request.'),
    ('invite', 'អញ្ជើញ', 'please (invitation); to invite', 'polite', 'Also a reply to thanks: you are welcome.'),
    ('yes-m', 'បាទ', 'yes (said by men)', 'polite', 'Men say បាទ baat; women say ចាស caah.'),
    ('yes-f', 'ចាស', 'yes (said by women)', 'polite', 'Women say ចាស caah; men say បាទ baat.'),
    ('no', 'ទេ', 'no; question particle', 'polite', 'At the end of a sentence it also turns a statement into a yes/no question, or closes a negative.'),
    ('sampeah', 'សំពះ', 'to greet with palms pressed together', 'polite', 'The sampeah: palms together in front of the chest, fingers up, when meeting or leaving.'),
    ('well', 'សុខ', 'well, healthy, at peace', 'greet', None),
    ('happy', 'សប្បាយ', 'happy, having fun', 'greet', None),
    ('name', 'ឈ្មោះ', 'name; to be called', 'greet', None),
    # people & address
    ('i', 'ខ្ញុំ', 'I, me', 'people', None),
    ('you', 'អ្នក', 'you (to an equal)', 'people', None),
    ('bong', 'បង', 'older sibling; you (to someone older)', 'people', 'Used as "you" for someone a little older than you, and by a husband or older sibling as "I".'),
    ('oun', 'ប្អូន', 'younger sibling; you (to someone younger)', 'people', None),
    ('lok', 'លោក', 'sir; you (to a man, respectfully)', 'people', None),
    ('lok-srey', 'លោកស្រី', 'madam, Mrs.; you (to a woman of standing)', 'people', None),
    ('uncle', 'ពូ', 'uncle; you (to a man younger than your parents)', 'people', None),
    ('aunt', 'មីង', 'aunt; you (to a woman younger than your parents)', 'people', None),
    ('he-she', 'គាត់', 'he, she (polite)', 'people', None),
    ('we', 'យើង', 'we', 'people', None),
    ('they', 'ពួកគេ', 'they', 'people', None),
    ('teacher', 'គ្រូ', 'teacher', 'people', None),
    ('student', 'សិស្ស', 'student', 'people', None),
    ('friend', 'មិត្តភក្តិ', 'friend', 'people', None),
    ('man', 'ប្រុស', 'male, man', 'people', None),
    ('woman', 'ស្រី', 'female, woman', 'people', None),
    # family
    ('father', 'ឪពុក', 'father', 'family', 'Starts with the independent vowel ឪ.'),
    ('mother', 'ម្ដាយ', 'mother', 'family', None),
    ('child', 'កូន', 'child', 'family', None),
    ('husband', 'ប្ដី', 'husband', 'family', None),
    ('wife', 'ប្រពន្ធ', 'wife', 'family', None),
    ('family', 'គ្រួសារ', 'family', 'family', None),
    ('older-brother', 'បងប្រុស', 'older brother', 'family', None),
    ('older-sister', 'បងស្រី', 'older sister', 'family', None),
    ('younger-brother', 'ប្អូនប្រុស', 'younger brother', 'family', None),
    ('younger-sister', 'ប្អូនស្រី', 'younger sister', 'family', None),
    ('grandmother', 'យាយ', 'grandmother', 'family', None),
    ('grandfather', 'តា', 'grandfather', 'family', None),
    # numbers
    ('zero', 'សូន្យ', 'zero', 'number', None),
    ('one', 'មួយ', 'one', 'number', None),
    ('two', 'ពីរ', 'two', 'number', None),
    ('three', 'បី', 'three', 'number', None),
    ('four', 'បួន', 'four', 'number', None),
    ('five', 'ប្រាំ', 'five', 'number', None),
    ('six', 'ប្រាំមួយ', 'six', 'number', 'Literally "five one": Khmer counts 6–9 as five plus one to four.'),
    ('seven', 'ប្រាំពីរ', 'seven', 'number', 'Literally "five two".'),
    ('eight', 'ប្រាំបី', 'eight', 'number', 'Literally "five three".'),
    ('nine', 'ប្រាំបួន', 'nine', 'number', 'Literally "five four".'),
    ('ten', 'ដប់', 'ten', 'number', None),
    ('twenty', 'ម្ភៃ', 'twenty', 'number', None),
    ('thirty', 'សាមសិប', 'thirty', 'number', None),
    ('forty', 'សែសិប', 'forty', 'number', None),
    ('fifty', 'ហាសិប', 'fifty', 'number', None),
    ('sixty', 'ហុកសិប', 'sixty', 'number', None),
    ('seventy', 'ចិតសិប', 'seventy', 'number', None),
    ('eighty', 'ប៉ែតសិប', 'eighty', 'number', None),
    ('ninety', 'កៅសិប', 'ninety', 'number', None),
    ('hundred', 'រយ', 'hundred', 'number', None),
    ('thousand', 'ពាន់', 'thousand', 'number', None),
    ('number', 'លេខ', 'number', 'number', None),
    # food & drink
    ('rice', 'បាយ', 'cooked rice; meal', 'food', None),
    ('water', 'ទឹក', 'water', 'food', None),
    ('fish', 'ត្រី', 'fish', 'food', None),
    ('meat', 'សាច់', 'meat', 'food', None),
    ('vegetable', 'បន្លែ', 'vegetable', 'food', None),
    ('fruit', 'ផ្លែឈើ', 'fruit', 'food', None),
    ('food', 'ម្ហូប', 'food, dish', 'food', None),
    ('chicken', 'មាន់', 'chicken', 'food', None),
    ('chicken-meat', 'សាច់មាន់', 'chicken (meat)', 'food', None),
    ('beef', 'សាច់គោ', 'beef', 'food', None),
    ('pork', 'សាច់ជ្រូក', 'pork', 'food', None),
    ('coffee', 'កាហ្វេ', 'coffee', 'food', None),
    ('tea', 'តែ', 'tea', 'food', None),
    ('ice', 'ទឹកកក', 'ice', 'food', 'Literally "water + frozen".'),
    ('milk', 'ទឹកដោះគោ', "cow's milk", 'food', None),
    ('banana', 'ចេក', 'banana', 'food', None),
    ('mango', 'ស្វាយ', 'mango', 'food', None),
    ('coconut', 'ដូង', 'coconut', 'food', None),
    ('orange', 'ក្រូច', 'orange (fruit)', 'food', None),
    ('bread', 'នំបុ័ង', 'bread', 'food', None),
    ('noodle-soup', 'គុយទាវ', 'kuyteav (rice noodle soup)', 'food', None),
    ('soup', 'ស៊ុប', 'soup', 'food', None),
    ('delicious', 'ឆ្ងាញ់', 'delicious', 'food', None),
    ('sweet', 'ផ្អែម', 'sweet', 'food', None),
    ('spicy', 'ហឹរ', 'spicy', 'food', None),
    ('hungry', 'ឃ្លាន', 'hungry', 'food', None),
    ('thirsty', 'ស្រេក', 'thirsty', 'food', None),
    ('eat', 'ញ៉ាំ', 'to eat', 'food', 'Everyday, colloquial word.'),
    ('drink', 'ផឹក', 'to drink', 'food', None),
    ('restaurant', 'ភោជនីយដ្ឋាន', 'restaurant', 'food', None),
    # market & money
    ('market', 'ផ្សារ', 'market', 'market', None),
    ('buy', 'ទិញ', 'to buy', 'market', None),
    ('sell', 'លក់', 'to sell', 'market', None),
    ('money', 'លុយ', 'money', 'market', None),
    ('riel', 'រៀល', 'riel (Cambodian currency)', 'market', None),
    ('dollar', 'ដុល្លារ', 'dollar', 'market', None),
    ('price', 'ថ្លៃ', 'price; expensive', 'market', None),
    ('cheap', 'ថោក', 'cheap', 'market', None),
    ('how-much', 'ប៉ុន្មាន', 'how much? how many?', 'market', None),
    # time
    ('day', 'ថ្ងៃ', 'day; sun', 'time', None),
    ('today', 'ថ្ងៃនេះ', 'today', 'time', 'Literally "day this".'),
    ('yesterday', 'ម្សិលមិញ', 'yesterday', 'time', None),
    ('tomorrow', 'ស្អែក', 'tomorrow', 'time', None),
    ('now', 'ឥឡូវ', 'now', 'time', 'Starts with the independent vowel ឥ.'),
    ('morning', 'ព្រឹក', 'morning', 'time', None),
    ('evening', 'ល្ងាច', 'evening', 'time', None),
    ('night', 'យប់', 'night', 'time', None),
    ('hour', 'ម៉ោង', "hour; o'clock", 'time', None),
    ('minute', 'នាទី', 'minute', 'time', None),
    ('week', 'សប្តាហ៍', 'week', 'time', None),
    ('month', 'ខែ', 'month; moon', 'time', None),
    ('year', 'ឆ្នាំ', 'year', 'time', None),
    ('age', 'អាយុ', 'age; to be ... years old', 'time', None),
    ('monday', 'ថ្ងៃច័ន្ទ', 'Monday', 'days', None),
    ('tuesday', 'ថ្ងៃអង្គារ', 'Tuesday', 'days', None),
    ('wednesday', 'ថ្ងៃពុធ', 'Wednesday', 'days', None),
    ('thursday', 'ថ្ងៃព្រហស្បតិ៍', 'Thursday', 'days', None),
    ('friday', 'ថ្ងៃសុក្រ', 'Friday', 'days', None),
    ('saturday', 'ថ្ងៃសៅរ៍', 'Saturday', 'days', None),
    ('sunday', 'ថ្ងៃអាទិត្យ', 'Sunday', 'days', None),
    # directions & places & transport
    ('left', 'ឆ្វេង', 'left', 'directions', None),
    ('right', 'ស្ដាំ', 'right', 'directions', None),
    ('straight', 'ត្រង់', 'straight', 'directions', None),
    ('stop', 'ឈប់', 'to stop', 'directions', None),
    ('near', 'ជិត', 'near', 'directions', None),
    ('far', 'ឆ្ងាយ', 'far', 'directions', None),
    ('road', 'ផ្លូវ', 'road, street', 'directions', None),
    ('return', 'ត្រឡប់', 'to return, go back', 'directions', None),
    ('wait', 'រង់ចាំ', 'to wait', 'directions', None),
    ('at', 'នៅ', 'to be at; at; to live', 'directions', None),
    ('where', 'ឯណា', 'where', 'question', None),
    ('which', 'ណា', 'where? which?', 'question', None),
    ('from', 'ពី', 'from', 'directions', None),
    ('house', 'ផ្ទះ', 'house, home', 'places', None),
    ('hotel', 'សណ្ឋាគារ', 'hotel', 'places', None),
    ('toilet', 'បង្គន់', 'toilet', 'places', None),
    ('school', 'សាលារៀន', 'school', 'places', None),
    ('pagoda', 'វត្ត', 'wat, pagoda, Buddhist temple', 'places', None),
    ('city', 'ទីក្រុង', 'city', 'places', None),
    ('phnom-penh', 'ភ្នំពេញ', 'Phnom Penh', 'places', None),
    ('siem-reap', 'សៀមរាប', 'Siem Reap', 'places', None),
    ('angkor-wat', 'អង្គរវត្ត', 'Angkor Wat', 'places', None),
    ('cambodia', 'កម្ពុជា', 'Cambodia', 'places', None),
    ('car', 'ឡាន', 'car', 'transport', None),
    ('motorbike', 'ម៉ូតូ', 'motorbike', 'transport', None),
    ('bicycle', 'កង់', 'bicycle; wheel', 'transport', None),
    ('bus', 'ឡានក្រុង', 'bus', 'transport', 'Literally "car + city".'),
    ('airplane', 'យន្តហោះ', 'airplane', 'transport', None),
    ('boat', 'ទូក', 'boat', 'transport', None),
    ('go', 'ទៅ', 'to go', 'transport', None),
    ('come', 'មក', 'to come', 'transport', None),
    ('walk', 'ដើរ', 'to walk', 'transport', None),
    # verbs
    ('want', 'ចង់', 'to want', 'verb', None),
    ('like', 'ចូលចិត្ត', 'to like', 'verb', None),
    ('love', 'ស្រឡាញ់', 'to love', 'verb', None),
    ('know', 'ដឹង', 'to know (a fact)', 'verb', None),
    ('know-how', 'ចេះ', 'to know how to, can', 'verb', None),
    ('understand', 'យល់', 'to understand', 'verb', None),
    ('speak', 'និយាយ', 'to speak', 'verb', None),
    ('study', 'រៀន', 'to study, learn', 'verb', None),
    ('work', 'ធ្វើការ', 'to work', 'verb', None),
    ('sleep', 'ដេក', 'to sleep, lie down', 'verb', None),
    ('look', 'មើល', 'to look, watch', 'verb', None),
    ('listen', 'ស្ដាប់', 'to listen; to understand (speech)', 'verb', None),
    ('write', 'សរសេរ', 'to write', 'verb', None),
    ('read', 'អាន', 'to read (aloud)', 'verb', None),
    ('help', 'ជួយ', 'to help', 'verb', None),
    ('have', 'មាន', 'to have; there is', 'verb', None),
    ('be', 'ជា', 'to be; to be well', 'verb', None),
    ('believe', 'ជឿ', 'to believe', 'verb', None),
    ('play', 'លេង', 'to play, have fun', 'verb', None),
    ('can', 'បាន', 'can; to get; did', 'verb', None),
    # describing
    ('good', 'ល្អ', 'good', 'adj', None),
    ('big', 'ធំ', 'big', 'adj', None),
    ('small', 'តូច', 'small', 'adj', None),
    ('beautiful', 'ស្អាត', 'beautiful; clean', 'adj', None),
    ('hot', 'ក្ដៅ', 'hot', 'adj', None),
    ('cold', 'ត្រជាក់', 'cold', 'adj', None),
    ('many', 'ច្រើន', 'many, much', 'adj', None),
    ('few', 'តិច', 'few, a little', 'adj', None),
    ('very', 'ណាស់', 'very', 'adj', 'Comes after the word it intensifies: ល្អណាស់ = very good.'),
    ('sick', 'ឈឺ', 'sick; to hurt', 'adj', None),
    ('a-little', 'បន្តិច', 'a little bit', 'adj', None),
    ('again', 'ម្ដងទៀត', 'again, once more', 'adj', None),
    # questions & grammar words
    ('what', 'អ្វី', 'what', 'question', None),
    ('what-colloquial', 'អី', 'what (casual)', 'question', None),
    ('who', 'នរណា', 'who', 'question', None),
    ('when', 'ពេលណា', 'when', 'question', None),
    ('why', 'ហេតុអ្វី', 'why', 'question', None),
    ('question-marker', 'តើ', 'question marker (polite, at the start)', 'question', None),
    ('this', 'នេះ', 'this', 'question', None),
    ('that', 'នោះ', 'that', 'question', None),
    ('not', 'មិន', 'not (before the verb)', 'question', 'Negative sentences wrap the verb: មិន + verb + ទេ.'),
    ('not-colloquial', 'អត់', 'not, no (casual)', 'question', None),
    ('already', 'ហើយ', 'already; and then', 'question', None),
    ('will', 'នឹង', 'will (future)', 'question', None),
    ('some', 'ខ្លះ', 'some', 'question', None),
    # language
    ('khmer', 'ខ្មែរ', 'Khmer, Cambodian', 'language', None),
    ('language', 'ភាសា', 'language', 'language', None),
    ('english', 'អង់គ្លេស', 'English; England', 'language', None),
    ('letter', 'អក្សរ', 'letter, script, alphabet', 'language', None),
    ('dog', 'ឆ្កែ', 'dog', 'animal', None),
    ('cat', 'ឆ្មា', 'cat', 'animal', None),
]

NUMBER_VALUES = {}

# Round 2 (October 2026): more topics. Same rule: spelling, romanisation and meaning
# must match the word's Wiktionary entry, or the build fails.
ITEMS += [
    # greetings
    ('good-night', 'រាត្រីសួស្ដី', 'good night', 'greet', None),
    ('sorry-som', 'សុំទោស', 'sorry, excuse me (everyday)', 'polite', 'More everyday than សូមទោស.'),
    ('welcome', 'ស្វាគមន៍', 'welcome', 'greet', None),
    ('good-luck', 'សំណាងល្អ', 'good luck', 'greet', None),
    ('you-intimate', 'ឯង', 'you (to a close friend or someone younger)', 'people', 'Starts with the independent vowel ឯ.'),
    ('person', 'មនុស្ស', 'person, human being', 'people', None),
    ('guest', 'ភ្ញៀវ', 'guest', 'people', None),
    ('grandchild', 'ចៅ', 'grandchild', 'family', None),
    ('parents', 'ឪពុកម្ដាយ', 'parents', 'family', 'Literally "father mother".'),
    ('young', 'ក្មេង', 'young; child', 'family', None),
    # body & health
    ('head', 'ក្បាល', 'head', 'body', None),
    ('eye', 'ភ្នែក', 'eye', 'body', None),
    ('ear', 'ត្រចៀក', 'ear', 'body', None),
    ('nose', 'ច្រមុះ', 'nose', 'body', None),
    ('mouth', 'មាត់', 'mouth', 'body', None),
    ('tooth', 'ធ្មេញ', 'tooth', 'body', None),
    ('tongue', 'អណ្ដាត', 'tongue', 'body', None),
    ('hand', 'ដៃ', 'hand, arm', 'body', None),
    ('foot', 'ជើង', 'foot, leg', 'body', 'Also the name for a subscript letter: its "foot".'),
    ('body', 'ខ្លួន', 'body; oneself', 'body', None),
    ('belly', 'ពោះ', 'belly', 'body', None),
    ('back', 'ខ្នង', 'back', 'body', None),
    ('hair', 'សក់', 'hair', 'body', None),
    ('face', 'មុខ', 'face', 'body', None),
    ('neck', 'ក', 'neck', 'body', 'Also the first letter of the alphabet.'),
    ('finger', 'ម្រាមដៃ', 'finger', 'body', None),
    ('heart', 'បេះដូង', 'heart', 'body', None),
    ('blood', 'ឈាម', 'blood', 'body', None),
    ('skin', 'ស្បែក', 'skin', 'body', None),
    ('bone', 'ឆ្អឹង', 'bone', 'body', None),
    ('shoulder', 'ស្មា', 'shoulder', 'body', None),
    ('knee', 'ជង្គង់', 'knee', 'body', None),
    ('doctor-pet', 'ពេទ្យ', 'doctor', 'health', None),
    ('doctor', 'គ្រូពេទ្យ', 'medical doctor', 'health', None),
    ('physician', 'វេជ្ជបណ្ឌិត', 'medical doctor (formal)', 'health', None),
    ('hospital', 'មន្ទីរពេទ្យ', 'hospital', 'health', None),
    ('medicine', 'ថ្នាំ', 'medicine', 'health', None),
    ('fever', 'គ្រុន', 'fever; to have a fever', 'health', None),
    ('cough', 'ក្អក', 'to cough', 'health', None),
    ('pharmacy', 'ឱសថស្ថាន', 'pharmacy', 'health', 'Starts with the independent vowel ឱ.'),
    ('headache', 'ឈឺក្បាល', 'headache; to have a headache', 'health', 'Literally "hurt head".'),
    # weather & nature
    ('weather', 'អាកាសធាតុ', 'weather', 'weather', None),
    ('rain', 'ភ្លៀង', 'rain; to rain', 'weather', None),
    ('wind', 'ខ្យល់', 'wind', 'weather', None),
    ('cloud', 'ពពក', 'cloud', 'weather', None),
    ('sky', 'មេឃ', 'sky', 'weather', None),
    ('sun', 'ព្រះអាទិត្យ', 'the sun', 'weather', None),
    ('moon', 'ព្រះច័ន្ទ', 'moon', 'weather', None),
    ('star', 'ផ្កាយ', 'star', 'weather', None),
    ('season', 'រដូវ', 'season', 'weather', None),
    ('thunder', 'ផ្គរ', 'thunder', 'weather', None),
    ('flood', 'ទឹកជំនន់', 'flood', 'weather', None),
    ('feel-cold', 'រងា', 'to be cold, to feel cold', 'weather', None),
    ('tree', 'ដើមឈើ', 'tree', 'nature', None),
    ('flower', 'ផ្កា', 'flower', 'nature', None),
    ('river', 'ទន្លេ', 'large river', 'nature', None),
    ('sea', 'សមុទ្រ', 'sea, ocean', 'nature', None),
    ('mountain', 'ភ្នំ', 'mountain, hill', 'nature', None),
    ('lake', 'បឹង', 'lake', 'nature', None),
    ('forest', 'ព្រៃ', 'forest, jungle', 'nature', None),
    ('earth', 'ដី', 'earth, land, soil', 'nature', None),
    ('stone', 'ថ្ម', 'stone', 'nature', None),
    ('rice-field', 'ស្រែ', 'rice field', 'nature', None),
    ('island', 'កោះ', 'island', 'nature', None),
    ('beach', 'ឆ្នេរ', 'beach, shore', 'nature', None),
    # colours & clothes
    ('colour', 'ពណ៌', 'colour', 'colour', 'Ends with the mark ៌, which is silent here.'),
    ('red', 'ក្រហម', 'red', 'colour', None),
    ('blue', 'ខៀវ', 'blue', 'colour', None),
    ('green', 'បៃតង', 'green', 'colour', None),
    ('yellow', 'លឿង', 'yellow', 'colour', None),
    ('white', 'ស', 'white', 'colour', 'Also a letter of the alphabet.'),
    ('black', 'ខ្មៅ', 'black', 'colour', None),
    ('grey', 'ប្រផេះ', 'grey', 'colour', None),
    ('pink', 'ផ្កាឈូក', 'lotus flower; pink', 'colour', 'Pink is ពណ៌ផ្កាឈូក, "lotus colour".'),
    ('gold', 'មាស', 'gold', 'colour', None),
    ('shirt', 'អាវ', 'shirt', 'clothes', None),
    ('trousers', 'ខោ', 'trousers', 'clothes', None),
    ('shoes', 'ស្បែកជើង', 'shoes', 'clothes', 'Literally "skin + foot".'),
    ('hat', 'មួក', 'hat', 'clothes', None),
    ('glasses', 'វ៉ែនតា', 'glasses', 'clothes', None),
    ('wallet', 'កាបូប', 'wallet, bag', 'clothes', None),
    ('size', 'ទំហំ', 'size', 'clothes', None),
    ('wear', 'ស្លៀក', 'to wear (below the waist)', 'clothes', None),
    # shopping
    ('silver', 'ប្រាក់', 'money; silver', 'market', None),
    ('value', 'តម្លៃ', 'price, value', 'market', None),
    ('discount', 'បញ្ចុះតម្លៃ', 'to lower the price, to discount', 'market', None),
    ('add', 'ថែម', 'to add; more', 'market', None),
    ('exchange', 'ដូរ', 'to exchange', 'market', None),
    ('take', 'យក', 'to take', 'market', None),
    ('give', 'ឲ្យ', 'to give', 'market', 'Starts with the independent vowel ឲ.'),
    ('spend', 'ចាយ', 'to spend (money)', 'market', None),
    ('too-much', 'ពេក', 'too, too much', 'market', 'ថ្លៃពេក = too expensive.'),
    ('customer', 'អតិថិជន', 'customer', 'market', None),
    ('seller', 'អ្នកលក់', 'salesperson', 'market', None),
    ('kilo', 'គីឡូ', 'kilogram', 'market', None),
    ('half', 'កន្លះ', 'half', 'market', None),
    ('all', 'ទាំងអស់', 'all', 'market', None),
    ('supermarket', 'ផ្សារទំនើប', 'supermarket', 'market', None),
    ('pay', 'បង់', 'to pay', 'market', None),
    # work & school
    ('job', 'ការងារ', 'work, job', 'work', None),
    ('office', 'ការិយាល័យ', 'office', 'work', None),
    ('company', 'ក្រុមហ៊ុន', 'company', 'work', None),
    ('salary', 'ប្រាក់ខែ', 'salary', 'work', None),
    ('boss', 'ចៅហ្វាយ', 'boss', 'work', None),
    ('farmer', 'កសិករ', 'farmer', 'work', None),
    ('police', 'ប៉ូលិស', 'police', 'work', None),
    ('cook-person', 'ចុងភៅ', 'cook', 'work', None),
    ('worker', 'កម្មករ', 'worker', 'work', None),
    ('soldier', 'ទាហាន', 'soldier', 'work', None),
    ('fisherman', 'អ្នកនេសាទ', 'fisherman', 'work', None),
    ('meet', 'ប្រជុំ', 'to meet, have a meeting', 'work', None),
    ('computer', 'កុំព្យូទ័រ', 'computer', 'things', None),
    ('telephone', 'ទូរស័ព្ទ', 'telephone', 'things', None),
    ('book', 'សៀវភៅ', 'book', 'school', None),
    ('paper', 'ក្រដាស', 'paper', 'school', None),
    ('pen', 'ប៊ិច', 'pen', 'school', None),
    ('pencil', 'ខ្មៅដៃ', 'pencil', 'school', None),
    ('table', 'តុ', 'table, desk', 'things', None),
    ('chair', 'កៅអី', 'chair', 'things', None),
    ('teacher-full', 'គ្រូបង្រៀន', 'teacher (school)', 'school', None),
    ('teach', 'បង្រៀន', 'to teach', 'school', None),
    ('class', 'ថ្នាក់', 'class, grade', 'school', None),
    # feelings
    ('angry', 'ខឹង', 'angry', 'feeling', None),
    ('afraid', 'ខ្លាច', 'afraid', 'feeling', None),
    ('tired', 'ហត់', 'tired, out of breath', 'feeling', None),
    ('weary', 'នឿយ', 'tired, exhausted', 'feeling', None),
    ('exhausted', 'អស់កម្លាំង', 'tired, exhausted', 'feeling', None),
    ('bored', 'អផ្សុក', 'bored', 'feeling', None),
    ('surprised', 'ភ្ញាក់ផ្អើល', 'surprised', 'feeling', None),
    ('worried', 'ព្រួយ', 'worried', 'feeling', None),
    ('shy', 'អៀន', 'shy, embarrassed', 'feeling', None),
    ('glad', 'រីករាយ', 'glad, happy', 'feeling', None),
    ('heart-mind', 'ចិត្ត', 'heart (feelings), mind', 'feeling', None),
    ('smile', 'ញញឹម', 'to smile', 'feeling', None),
    ('laugh', 'សើច', 'to laugh', 'feeling', None),
    ('cry', 'យំ', 'to cry', 'feeling', None),
    ('miss', 'នឹក', 'to miss (someone)', 'feeling', None),
    # little words
    ('how', 'ម៉េច', 'how; why (casual)', 'question', None),
    ('or', 'ឬ', 'or', 'question', 'An independent vowel used as a whole word.'),
    ('true', 'មែន', 'true, really', 'question', None),
    ('isnt-it', 'មែនទេ', 'right? really?', 'question', None),
    ('also', 'ផង', 'also, too', 'question', None),
    ('also-dae', 'ដែរ', 'also, too, likewise', 'question', None),
    ('more', 'ទៀត', 'more, again', 'question', None),
    ('and', 'និង', 'and', 'question', None),
    ('with', 'ជាមួយ', 'with', 'question', None),
    ('for', 'សម្រាប់', 'for', 'question', None),
    ('because', 'ព្រោះ', 'because', 'question', None),
    ('if', 'ប្រសិនបើ', 'if', 'question', None),
    ('but', 'ប៉ុន្តែ', 'but', 'question', None),
    ('can-able', 'អាច', 'to be able to, can', 'question', None),
    ('say', 'ថា', 'to say; that', 'verb', None),
    # home
    ('room', 'បន្ទប់', 'room', 'home', None),
    ('door', 'ទ្វារ', 'door', 'home', None),
    ('window', 'បង្អួច', 'window', 'home', None),
    ('bed', 'គ្រែ', 'bed', 'home', None),
    ('kitchen', 'ផ្ទះបាយ', 'kitchen', 'home', 'Literally "house + rice".'),
    ('bathroom', 'បន្ទប់ទឹក', 'bathroom', 'home', 'Literally "room + water".'),
    ('fire', 'ភ្លើង', 'fire; light; electricity', 'home', None),
    ('fan', 'កង្ហារ', 'fan (electric)', 'home', None),
    ('television', 'ទូរទស្សន៍', 'television', 'home', None),
    ('plate', 'ចាន', 'plate, bowl', 'home', None),
    ('spoon', 'ស្លាបព្រា', 'spoon', 'home', None),
    ('fork', 'សម', 'fork', 'home', None),
    ('chopsticks', 'ចង្កឹះ', 'chopstick', 'home', None),
    ('glass', 'កែវ', 'glass', 'home', None),
    ('knife', 'កាំបិត', 'knife', 'home', None),
    ('pot', 'ឆ្នាំង', 'cooking pot', 'home', None),
    # animals
    ('cow', 'គោ', 'cow, ox', 'animal', None),
    ('pig', 'ជ្រូក', 'pig', 'animal', None),
    ('duck', 'ទា', 'duck', 'animal', None),
    ('horse', 'សេះ', 'horse', 'animal', None),
    ('elephant', 'ដំរី', 'elephant', 'animal', None),
    ('monkey', 'ស្វា', 'monkey', 'animal', None),
    ('snake', 'ពស់', 'snake', 'animal', None),
    ('buffalo', 'ក្របី', 'water buffalo', 'animal', None),
    ('animal', 'សត្វ', 'animal', 'animal', None),
    ('bird', 'បក្សី', 'bird', 'animal', None),
    ('mouse', 'កណ្ដុរ', 'mouse, rat', 'animal', None),
    ('mosquito', 'មូស', 'mosquito', 'animal', None),
    # more food
    ('raw-rice', 'អង្ករ', 'rice (uncooked)', 'food', None),
    ('sugar', 'ស្ករ', 'sugar', 'food', None),
    ('salt', 'អំបិល', 'salt', 'food', None),
    ('chili', 'ម្ទេស', 'chili pepper', 'food', None),
    ('onion', 'ខ្ទឹម', 'onion, garlic', 'food', None),
    ('fish-sauce', 'ទឹកត្រី', 'fish sauce', 'food', 'Literally "water + fish".'),
    ('prahok', 'ប្រហុក', 'prahok (fermented fish paste)', 'food', None),
    ('porridge', 'បបរ', 'rice porridge', 'food', None),
    ('cake', 'នំ', 'cake, pastry, dessert', 'food', None),
    ('alcohol', 'ស្រា', 'alcohol, wine', 'food', None),
    ('papaya', 'ល្ហុង', 'papaya', 'food', None),
    ('pineapple', 'ម្នាស់', 'pineapple', 'food', None),
    ('watermelon', 'ឪឡឹក', 'watermelon', 'food', None),
    ('crab', 'ក្ដាម', 'crab', 'food', None),
    ('shrimp', 'បង្គា', 'shrimp, prawn', 'food', None),
    ('sour', 'ជូរ', 'sour', 'food', None),
    ('salty', 'ប្រៃ', 'salty', 'food', None),
    ('bitter', 'ល្វីង', 'bitter', 'food', None),
    ('full', 'ឆ្អែត', 'full (after eating)', 'food', None),
    ('meal', 'អាហារ', 'food, meal', 'food', None),
    # time
    ('january', 'មករា', 'January', 'month', None),
    ('february', 'កុម្ភៈ', 'February', 'month', 'Ends with the mark ៈ.'),
    ('march', 'មីនា', 'March', 'month', None),
    ('april', 'មេសា', 'April', 'month', None),
    ('may', 'ឧសភា', 'May', 'month', 'Starts with the independent vowel ឧ.'),
    ('june', 'មិថុនា', 'June', 'month', None),
    ('july', 'កក្កដា', 'July', 'month', None),
    ('august', 'សីហា', 'August', 'month', None),
    ('september', 'កញ្ញា', 'September', 'month', None),
    ('october', 'តុលា', 'October', 'month', None),
    ('november', 'វិច្ឆិកា', 'November', 'month', None),
    ('december', 'ធ្នូ', 'December', 'month', None),
    ('noon', 'ថ្ងៃត្រង់', 'noon', 'time', None),
    ('afternoon', 'រសៀល', 'afternoon', 'time', None),
    ('soon', 'ឆាប់', 'quick, soon', 'time', None),
    ('slow', 'យឺត', 'slow', 'time', None),
    ('before', 'មុន', 'before', 'time', None),
    ('after', 'ក្រោយ', 'after, behind', 'time', None),
    ('done', 'រួច', 'to finish, be done', 'time', None),
    ('always', 'ជានិច្ច', 'always', 'time', None),
    ('sometimes', 'ពេលខ្លះ', 'sometimes', 'time', None),
    ('once', 'ម្ដង', 'one time, once', 'time', None),
    ('time', 'ពេល', 'time, moment', 'time', None),
    # directions & travel
    ('above', 'ខាងលើ', 'above, upstairs', 'directions', None),
    ('in-front', 'ខាងមុខ', 'in front', 'directions', None),
    ('behind', 'ខាងក្រោយ', 'behind', 'directions', None),
    ('inside', 'ក្នុង', 'in, inside', 'directions', None),
    ('outside', 'ក្រៅ', 'outside', 'directions', None),
    ('turn', 'បត់', 'to turn', 'directions', None),
    ('station', 'ស្ថានីយ', 'station', 'places', None),
    ('ticket', 'សំបុត្រ', 'ticket; letter', 'places', None),
    ('passport', 'លិខិតឆ្លងដែន', 'passport', 'places', None),
    ('bank', 'ធនាគារ', 'bank', 'places', None),
    ('post-office', 'ប្រៃសណីយ៍', 'post office', 'places', None),
    ('map', 'ផែនទី', 'map', 'places', None),
    ('country', 'ប្រទេស', 'country', 'places', None),
    ('village', 'ភូមិ', 'village', 'places', None),
    ('province', 'ខេត្ត', 'province', 'places', None),
    ('correct', 'ត្រូវ', 'correct, right; must', 'adj', None),
    ('wrong', 'ខុស', 'wrong', 'adj', None),
    # verbs
    ('do', 'ធ្វើ', 'to do, to make', 'verb', None),
    ('see', 'ឃើញ', 'to see', 'verb', None),
    ('know-person', 'ស្គាល់', 'to know (someone)', 'verb', None),
    ('remember', 'ចាំ', 'to remember; to wait', 'verb', None),
    ('forget', 'ភ្លេច', 'to forget', 'verb', None),
    ('think', 'គិត', 'to think', 'verb', None),
    ('need', 'ត្រូវការ', 'to need', 'verb', None),
    ('ask', 'សួរ', 'to ask', 'verb', None),
    ('answer', 'ឆ្លើយ', 'to answer', 'verb', None),
    ('tell', 'ប្រាប់', 'to tell', 'verb', None),
    ('call', 'ហៅ', 'to call', 'verb', None),
    ('open', 'បើក', 'to open; to drive', 'verb', None),
    ('close', 'បិទ', 'to close', 'verb', None),
    ('enter', 'ចូល', 'to enter', 'verb', None),
    ('go-out', 'ចេញ', 'to go out, to leave', 'verb', None),
    ('sit', 'អង្គុយ', 'to sit', 'verb', None),
    ('stand', 'ឈរ', 'to stand', 'verb', None),
    ('run', 'រត់', 'to run', 'verb', None),
    ('swim', 'ហែលទឹក', 'to swim', 'verb', None),
    ('bathe', 'ងូតទឹក', 'to bathe, take a shower', 'verb', None),
    ('wash', 'លាង', 'to wash', 'verb', None),
    ('cook', 'ចំអិន', 'to cook', 'verb', None),
    ('ride', 'ជិះ', 'to ride', 'verb', None),
    ('live', 'រស់', 'to live, be alive', 'verb', None),
    ('receive', 'ទទួល', 'to receive', 'verb', None),
    ('send', 'ផ្ញើ', 'to send', 'verb', None),
    ('look-for', 'រក', 'to look for', 'verb', None),
    ('lose', 'បាត់', 'to be lost, missing', 'verb', None),
    ('use', 'ប្រើ', 'to use', 'verb', None),
    ('begin', 'ចាប់ផ្ដើម', 'to begin', 'verb', None),
    ('finish', 'បញ្ចប់', 'to finish', 'verb', None),
    ('marry', 'រៀបការ', 'to get married', 'verb', None),
    ('translate', 'បកប្រែ', 'to translate', 'language', None),
    # describing
    ('new', 'ថ្មី', 'new', 'adj', None),
    ('old', 'ចាស់', 'old', 'adj', None),
    ('long', 'វែង', 'long', 'adj', None),
    ('short', 'ខ្លី', 'short (in length)', 'adj', None),
    ('tall', 'ខ្ពស់', 'tall, high', 'adj', None),
    ('low', 'ទាប', 'low, short', 'adj', None),
    ('fat', 'ធាត់', 'fat', 'adj', None),
    ('thin', 'ស្គម', 'thin', 'adj', None),
    ('fast', 'លឿន', 'fast', 'adj', None),
    ('easy', 'ងាយ', 'easy', 'adj', None),
    ('difficult', 'ពិបាក', 'difficult', 'adj', None),
    ('important', 'សំខាន់', 'important', 'adj', None),
    ('quiet', 'ស្ងាត់', 'quiet', 'adj', None),
    ('busy', 'រវល់', 'busy', 'adj', None),
    ('free', 'ទំនេរ', 'free, not busy', 'adj', None),
    ('fresh', 'ស្រស់', 'fresh', 'adj', None),
    ('dirty', 'កខ្វក់', 'dirty', 'adj', None),
    ('heavy', 'ធ្ងន់', 'heavy', 'adj', None),
    ('light', 'ស្រាល', 'light (in weight)', 'adj', None),
    ('real', 'ពិត', 'true, real', 'adj', None),
    ('really', 'ពិតជា', 'certainly, surely', 'adj', None),
    ('same', 'ដូចគ្នា', 'the same', 'adj', None),
    ('different', 'ផ្សេង', 'different', 'adj', None),
    ('wet', 'សើម', 'wet, damp', 'adj', None),
    ('dry', 'ស្ងួត', 'dry', 'adj', None),
    ('bright', 'ភ្លឺ', 'bright', 'adj', None),
    ('dark', 'ងងឹត', 'dark', 'adj', None),
    # language
    ('word', 'ពាក្យ', 'word', 'language', None),
    ('sentence', 'ប្រយោគ', 'sentence', 'language', None),
    ('chinese', 'ចិន', 'China; Chinese', 'language', None),
    ('french', 'បារាំង', 'France; French', 'language', None),
    ('vietnam', 'វៀតណាម', 'Vietnam; Vietnamese', 'language', None),
    ('thai', 'ថៃ', 'Thai; Thailand', 'language', None),
    ('america', 'អាមេរិក', 'America', 'language', None),
    # big numbers
    ('ten-thousand', 'ម៉ឺន', 'ten thousand', 'number', None),
    ('hundred-thousand', 'សែន', 'hundred thousand', 'number', None),
    ('million', 'លាន', 'million', 'number', None),
]
NUMBER_VALUES.update({'ten-thousand': 10000, 'hundred-thousand': 100000, 'million': 1000000})

# Compound numbers, written per Wikipedia (Khmer language § Numerals: "intermediate
# numbers are formed by compounding the above elements"). Romanisation = the WT forms of the parts.
COMPOUND_NUMBERS = [
    ('eleven', ['ដប់', 'មួយ'], 11, 'eleven'),
    ('fifteen', ['ដប់', 'ប្រាំ'], 15, 'fifteen'),
    ('twenty-one', ['ម្ភៃ', 'មួយ'], 21, 'twenty-one'),
    ('one-hundred', ['មួយ', 'រយ'], 100, 'one hundred'),
    ('one-thousand', ['មួយ', 'ពាន់'], 1000, 'one thousand'),
]
NUMBER_VALUES.update({'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8,
                 'nine': 9, 'ten': 10, 'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
                 'eighty': 80, 'ninety': 90, 'hundred': 100, 'thousand': 1000})

STOP = set('to a an the of be is (said by) (formal) (casual) you i and or one'.split())
def gloss_check(km, en):
    senses = ' '.join(V[km]['defs']).lower()
    words = [w for w in re.findall(r"[a-z']+", en.lower()) if w not in STOP and len(w) > 2]
    hits = [w for w in words if w in senses or w.rstrip('s') in senses]
    return bool(hits) or not words

def digits(n): return ''.join(chr(0x17E0 + int(c)) for c in str(n))

items, problems = [], []
for iid, km, en, cat, note in ITEMS:
    if km not in V or V[km]['status'] != 'ok':
        problems.append(f'{iid}: {km} not verified'); continue
    if not gloss_check(km, en):
        problems.append(f'{iid}: gloss "{en}" not found in Wiktionary senses: {V[km]["defs"][:3]}')
    it = {'id': iid, 'km': km, 'rom': wt(km), 'en': en, 'cat': cat, 'src': f'wiktionary:{km}'}
    ipa = V[km].get('ipa') or []
    if ipa: it['ipa'] = ipa[0]
    if note: it['note'] = note
    if iid in NUMBER_VALUES:
        it['value'] = NUMBER_VALUES[iid]; it['digits'] = digits(NUMBER_VALUES[iid])
    items.append(it)
for iid, parts, value, name in COMPOUND_NUMBERS:
    items.append({'id': iid, 'km': ''.join(parts), 'rom': ' '.join(wt(p) for p in parts), 'en': name, 'cat': 'number',
                  'value': value, 'digits': digits(value), 'src': 'composed: Wikipedia Khmer language § Numerals (compounding); parts from Wiktionary',
                  'note': ' + '.join(f'{p} {wt(p)}' for p in parts)})
ids = [it['id'] for it in items]
dupes = {i for i in ids if ids.count(i) > 1}
if dupes: problems.append(f'duplicate item ids: {dupes}')
by_km = {}
for it in items: by_km.setdefault(it['km'], it['id'])
if problems:
    print('\n'.join(problems)); sys.exit(1)

# ---- sentences: (id, tokens (Khmer), English, source) ----
WP = 'wikipedia:Khmer language § Syntax'
WPA = 'wikipedia:Khmer language § Adjectives and adverbs'
SENTENCES = [
    ('how-are-you', ['សុខ', 'សប្បាយ', 'ជា', 'ទេ'], 'How are you?', 'wiktionary:how are you (Khmer translation)'),
    ('im-fine', ['ខ្ញុំ', 'សុខ', 'សប្បាយ'], "I'm fine.", "wiktionary:I'm fine (Khmer translation)"),
    ('thanks-a-lot', ['អរគុណ', 'ច្រើន'], 'Thank you very much.', 'wiktionary:thank you very much (Khmer translation)'),
    ('whats-your-name', ['តើ', 'អ្នក', 'ឈ្មោះ', 'អ្វី'], 'What is your name?', 'wiktionary:ឈ្មោះ (usage example)'),
    ('im-hungry', ['ខ្ញុំ', 'ឃ្លាន'], "I'm hungry.", "wiktionary:I'm hungry (Khmer translation)"),
    ('where-toilet', ['តើ', 'បង្គន់', 'នៅ', 'ឯណា'], 'Where is the toilet?', 'wiktionary:where is the toilet (Khmer translation)'),
    ('dont-understand', ['ខ្ញុំ', 'មិន', 'យល់', 'ទេ'], "I don't understand.", 'wiktionary:ខ្ញុំមិនយល់ទេ'),
    ('dont-know', ['ខ្ញុំ', 'មិន', 'ដឹង', 'ទេ'], "I don't know.", "wiktionary:I don't know (Khmer translation)"),
    ('how-much', ['ថ្លៃ', 'ប៉ុន្មាន'], 'How much (does it cost)?', 'wiktionary:how much (Khmer translation)'),
    ('speak-english', ['តើ', 'អ្នក', 'និយាយ', 'ភាសា', 'អង់គ្លេស', 'ទេ'], 'Do you speak English?', 'wiktionary:do you speak English (Khmer translation)'),
    ('cant-speak-khmer', ['ខ្ញុំ', 'មិន', 'ចេះ', 'និយាយ', 'ភាសា', 'ខ្មែរ', 'ទេ'], "I can't speak Khmer.", "wiktionary:I don't speak (Khmer translation)"),
    ('where-from', ['តើ', 'អ្នក', 'មក', 'ពី', 'ណា'], 'Where are you from?', 'wiktionary:where are you from (Khmer translation)'),
    ('stroll', ['ខ្ញុំ', 'ចង់', 'ទៅ', 'ដើរ', 'លេង'], 'I want to go for a stroll.', WP + ' (verb phrase)'),
    ('dont-believe', ['ខ្ញុំ', 'មិន', 'ជឿ', 'ទេ'], "I don't believe it.", WP + ' (negation)'),
    ('went-yesterday', ['គាត់', 'ទៅ', 'ម្សិលមិញ'], 'He went yesterday.', WP + ' (past time)'),
    ('already-left', ['គាត់', 'ទៅ', 'ហើយ'], 'He has already left.', WP + ' (perfective ហើយ)'),
    ('school-tomorrow', ['ស្អែក', 'ខ្ញុំ', 'នឹង', 'ទៅ', 'សាលារៀន'], 'Tomorrow I will go to school.', WP + ' (future នឹង)'),
    ('where-going', ['លោក', 'ទៅ', 'ណា'], 'Where are you going?', WP + ' (questions)'),
    ('can-you-understand', ['លោក', 'ស្ដាប់', 'បាន', 'ទេ'], 'Can you understand?', WP + ' (questions)'),
    ('very-pretty', ['ស្រី', 'នោះ', 'ស្អាត', 'ណាស់'], 'That girl is very pretty.', WPA),
    ('this-morning', ['ព្រឹក', 'នេះ', 'បង', 'ទៅ', 'ណា', 'ខ្លះ'], 'Where are you going this morning?', 'wiktionary:ព្រឹក (usage example)'),
    ('two-dogs', ['ឆ្កែ', 'ពីរ'], 'two dogs', 'wikipedia:Khmer language § Nouns and pronouns'),
    # Round 2, attested: Wiktionary phrasebook translations, split into course words.
    ('what-time', ['ម៉ោង', 'ប៉ុន្មាន', 'ហើយ'], 'What time is it?', 'wiktionary:what time is it (Khmer translation)'),
    ('how-old', ['តើ', 'អ្នក', 'មាន', 'អាយុ', 'ប៉ុន្មាន', 'ហើយ'], 'How old are you?', 'wiktionary:how old are you (Khmer translation)'),
    ('need-doctor', ['ខ្ញុំ', 'ត្រូវការ', 'គ្រូពេទ្យ'], 'I need a doctor.', 'wiktionary:I need a doctor (Khmer translation)'),
    ('call-police', ['ជួយ', 'ហៅ', 'ប៉ូលិស', 'មក'], 'Call the police!', 'wiktionary:call the police (Khmer translation)'),
    ('where-live', ['តើ', 'អ្នក', 'រស់', 'នៅ', 'ឯណា'], 'Where do you live?', 'wiktionary:where do you live (Khmer translation)'),
    ('im-sick', ['ខ្ញុំ', 'ឈឺ'], "I'm sick.", "wiktionary:I'm sick (Khmer translation)"),
    ('im-cold', ['ខ្ញុំ', 'រងា'], "I'm cold.", "wiktionary:I'm cold (Khmer translation)"),
    ('miss-you', ['នឹក', 'ឯង'], 'I miss you.', 'wiktionary:I miss you (Khmer translation)'),
    ('im-exhausted', ['ខ្ញុំ', 'អស់កម្លាំង'], "I'm tired.", "wiktionary:I'm tired (Khmer translation)"),
    # Composed by substituting verified words into the attested patterns above.
    ('want-rice', ['ខ្ញុំ', 'ចង់', 'ញ៉ាំ', 'បាយ'], 'I want to eat rice.', 'composed: pattern ខ្ញុំ ចង់ + verb (' + WP + ')'),
    ('want-coffee', ['ខ្ញុំ', 'ចង់', 'ផឹក', 'កាហ្វេ'], 'I want to drink coffee.', 'composed: pattern ខ្ញុំ ចង់ + verb (' + WP + ')'),
    ('want-market', ['ខ្ញុំ', 'ចង់', 'ទៅ', 'ផ្សារ'], 'I want to go to the market.', 'composed: pattern ទៅ + place (' + WP + ')'),
    ('learn-khmer', ['ខ្ញុំ', 'ចង់', 'រៀន', 'ភាសា', 'ខ្មែរ'], 'I want to learn Khmer.', 'composed: pattern ខ្ញុំ ចង់ + verb (' + WP + ')'),
    ('very-delicious', ['ឆ្ងាញ់', 'ណាស់'], 'Very delicious!', 'composed: pattern adjective + ណាស់ (' + WPA + ')'),
    ('very-expensive', ['ថ្លៃ', 'ណាស់'], 'Very expensive!', 'composed: pattern adjective + ណាស់ (' + WPA + ')'),
    ('where-market', ['តើ', 'ផ្សារ', 'នៅ', 'ឯណា'], 'Where is the market?', 'composed: pattern of "where is the toilet" (wiktionary)'),
    ('im-thirsty', ['ខ្ញុំ', 'ស្រេក'], "I'm thirsty.", "composed: pattern of \"I'm hungry\" (wiktionary)"),
    ('like-kuyteav', ['ខ្ញុំ', 'ចូលចិត្ត', 'គុយទាវ'], 'I like kuyteav (noodle soup).', 'composed: subject + verb + object (' + WP + ')'),
    ('where-hospital', ['តើ', 'មន្ទីរពេទ្យ', 'នៅ', 'ឯណា'], 'Where is the hospital?', 'composed: pattern of "where is the toilet" (wiktionary)'),
    ('where-bank', ['តើ', 'ធនាគារ', 'នៅ', 'ឯណា'], 'Where is the bank?', 'composed: pattern of "where is the toilet" (wiktionary)'),
    ('need-water', ['ខ្ញុំ', 'ត្រូវការ', 'ទឹក'], 'I need water.', 'composed: pattern of "I need a doctor" (wiktionary)'),
    ('need-medicine', ['ខ្ញុំ', 'ត្រូវការ', 'ថ្នាំ'], 'I need medicine.', 'composed: pattern of "I need a doctor" (wiktionary)'),
    ('have-headache', ['ខ្ញុំ', 'ឈឺក្បាល'], 'I have a headache.', "composed: pattern of \"I'm sick\" (wiktionary)"),
    ('im-tired', ['ខ្ញុំ', 'ហត់'], "I'm tired (out of breath).", "composed: pattern of \"I'm hungry\" (wiktionary)"),
    ('im-afraid', ['ខ្ញុំ', 'ខ្លាច'], "I'm afraid.", "composed: pattern of \"I'm hungry\" (wiktionary)"),
    ('im-busy', ['ខ្ញុំ', 'រវល់'], "I'm busy.", "composed: pattern of \"I'm hungry\" (wiktionary)"),
    ('want-buy-hat', ['ខ្ញុំ', 'ចង់', 'ទិញ', 'មួក'], 'I want to buy a hat.', 'composed: pattern ខ្ញុំ ចង់ + verb (' + WP + ')'),
    ('shirt-expensive', ['អាវ', 'នេះ', 'ថ្លៃ', 'ពេក'], 'This shirt is too expensive.', 'composed: noun + នេះ + adjective (' + WPA + ')'),
    ('hot-today', ['ថ្ងៃនេះ', 'ក្ដៅ', 'ណាស់'], 'It is very hot today.', 'composed: pattern adjective + ណាស់ (' + WPA + ')'),
    ('market-far', ['ផ្សារ', 'ឆ្ងាយ', 'ទេ'], 'Is the market far?', 'composed: yes/no question with ទេ (' + WP + ')'),
    ('two-cats', ['ឆ្មា', 'ពីរ'], 'two cats', 'composed: pattern of "two dogs" (wikipedia:Khmer language § Nouns and pronouns)'),
    ('like-red', ['ខ្ញុំ', 'ចូលចិត្ត', 'ពណ៌', 'ក្រហម'], 'I like the colour red.', 'composed: subject + verb + object (' + WP + ')'),
    ('elephant-big', ['ដំរី', 'ធំ', 'ណាស់'], 'The elephant is very big.', 'composed: pattern adjective + ណាស់ (' + WPA + ')'),
    ('im-teacher', ['ខ្ញុំ', 'ជា', 'គ្រូបង្រៀន'], 'I am a teacher.', 'composed: noun + ជា + noun (wiktionary:ជា, "to be")'),
    ('want-coffee-q', ['តើ', 'អ្នក', 'ចង់', 'ផឹក', 'កាហ្វេ', 'ទេ'], 'Do you want to drink coffee?', 'composed: pattern of "do you speak English" (wiktionary)'),
    ('open-door', ['សូម', 'បើក', 'ទ្វារ'], 'Please open the door.', 'composed: សូម + verb, a polite request (wiktionary:សូម)'),
]
sentences = []
for sid, toks, en, src in SENTENCES:
    missing = [t for t in toks if t not in by_km]
    if missing: problems.append(f'sentence {sid}: tokens not items: {missing}'); continue
    sentences.append({'id': sid, 'tokens': [by_km[t] for t in toks], 'en': en, 'src': src})

# ---- script (Wikipedia: Khmer script) ----
cons_raw = [c for c in json.load(open(os.path.join(SRC, 'consonants_raw.json'))) if c['char'] not in ('ឝ', 'ឞ')]  # two obsolete letters
consonants = []
for i, c in enumerate(cons_raw):
    con = {'id': f'c{i+1:02d}', 'char': c['char'], 'name': c['name_ungegn'], 'ipa_name': c['ipa_name'],
           'ipa': c['ipa'], 'value': c['value_ungegn'], 'series': c['series']}
    if c['subscript'] != c['char']: con['sub'] = '◌' + c['subscript']  # ឡ has no subscript form
    consonants.append(con)
vow_raw = [v for v in json.load(open(os.path.join(SRC, 'vowels_raw.json'))) if v['vowel'] != '(none)']
vowels = [{'id': f'v{i+1:02d}', 'char': '◌' + v['vowel'], 'example': v['example'], 'ipa_a': v['ipa_a'],
           'ipa_o': v['ipa_o'], 'rom_a': v['ungegn_a'], 'rom_o': v['ungegn_o']} for i, v in enumerate(vow_raw)]
digit_words = ['សូន្យ', 'មួយ', 'ពីរ', 'បី', 'បួន', 'ប្រាំ', 'ប្រាំមួយ', 'ប្រាំពីរ', 'ប្រាំបី', 'ប្រាំបួន']
digit_list = [{'id': f'd{n}', 'char': chr(0x17E0 + n), 'value': n, 'word': digit_words[n], 'word_rom': wt(digit_words[n]),
               'word_item': by_km[digit_words[n]]} for n in range(10)]

combo_raw = json.load(open(os.path.join(SRC, 'combos_raw.json')))
combos = []
for i, k in enumerate(combo_raw):
    sign = k['combo'].replace('អ', '', 1)
    note = 'The ំ adds a final m and shortens the vowel.' if 'ំ' in sign else 'The ះ adds a final h.'
    combos.append({'id': f'k{i+1:02d}', 'char': '◌' + sign, 'sign': sign, 'example': k['combo'], 'ipa_a': k['ipa_a'], 'ipa_o': k['ipa_o'],
                   'rom_a': k['ungegn_a'], 'rom_o': k['ungegn_o'], 'note': note})

def example_with(chars):
    hits = [it for it in items if any(c in it['km'] for c in chars) and it.get('src', '').startswith('wiktionary')]
    hits.sort(key=lambda it: (len(it['km']), it['km']))
    return {'km': hits[0]['km'], 'rom': hits[0]['rom'], 'en': hits[0]['en'], 'item': hits[0]['id']} if hits else None

ind_raw = json.load(open(os.path.join(SRC, 'independent_raw.json')))
independents = []
for i, v in enumerate(r for r in ind_raw if r['ungegn'] != 'not given'):
    iv = {'id': f'i{i+1:02d}', 'chars': v['chars'], 'rom': v['ungegn'], 'ipa': v['ipa']}
    ex = example_with(v['chars'])
    if ex: iv['example'] = ex
    independents.append(iv)

MARK_SUMMARY = {  # short paraphrases of the "Function" column of Wikipedia's diacritics table
    'ំ': 'Adds a final m sound and makes the vowel nasal and short.',
    'ះ': 'Adds a final h sound after the vowel.',
    'ៈ': 'Shows a short vowel followed by a glottal stop.',
    '៉': 'Turns some o-series letters (ង ញ ម យ រ វ) into a-series. On ប it gives a p sound.',
    '៊': 'Turns some a-series letters (ស ហ ប អ) into o-series.',
    '់': 'Written over a final consonant: shortens the vowel before it.',
    '៌': 'In Sanskrit loanwords. The letter under it and the mark itself are usually silent.',
    '៍': 'Written over a final consonant to show it is silent.',
    '័': 'In some Sanskrit and Pali loanwords: marks a particular short vowel.',
}
diac_raw = {d['char']: d for d in json.load(open(os.path.join(SRC, 'diacritics_raw.json')))}
marks = []
for i, ch in enumerate(['ំ', 'ះ', 'ៈ', '់', '៉', '៊', '៍', '៌', '័']):
    d = diac_raw[ch]
    m = {'id': f'm{i+1:02d}', 'char': ch, 'shown': '◌' + ch, 'name_km': d['name_km'].split(' ')[0],
         'name_rom': re.split(r'["“]', d['name_rom'])[0].strip() if ch != '៌' else d['name_rom'].split(' ')[0], 'summary': MARK_SUMMARY[ch]}
    ex = example_with([ch])
    if ex: m['example'] = ex
    marks.append(m)

for c in consonants:  # an example word for each subscript
    if 'sub' in c:
        ex = example_with(['្' + c['char']])
        if ex: c['cluster'] = ex

# ---- letters course: small sets, Duolingo "Letters" style ----
C = lambda *chars: [c['id'] for c in consonants if c['char'] in chars]
Vw = lambda *signs: [v['id'] for v in vowels if v['char'][1:] in signs]
K = lambda *signs: [k['id'] for k in combos if k['sign'] in signs]
IV = lambda *chars: [v['id'] for v in independents if v['chars'][0] in chars]
M = lambda *chars: [m['id'] for m in marks if m['char'] in chars]
# subscripts, most frequent in course words first
from collections import Counter
sub_freq = Counter(ch for it in items for ch in re.findall(r'្(.)', it['km']))
subs_ranked = [c['id'] for c in sorted((c for c in consonants if 'sub' in c and 'cluster' in c), key=lambda c: -sub_freq[c['char']])][:15]
letter_groups = [
    {'id': 'a1', 'title': 'ក ខ ច ឆ', 'consonants': C('ក', 'ខ', 'ច', 'ឆ'), 'tip': 'These are a-series consonants: on their own they are read with â [ɑː]. ក is kâ, ខ is khâ.'},
    {'id': 'a2', 'title': 'ដ ត ថ ប', 'consonants': C('ដ', 'ត', 'ថ', 'ប'), 'tip': 'ដ dâ and ត tâ look alike: ដ has a curl at the top.'},
    {'id': 'a3', 'title': 'ផ ស ហ អ', 'consonants': C('ផ', 'ស', 'ហ', 'អ'), 'tip': 'អ is a glottal stop. Vowels that start a word are written on it.'},
    {'id': 'a4', 'title': 'ឋ ណ ឡ', 'consonants': C('ឋ', 'ណ', 'ឡ'), 'tip': 'Rarer a-series letters, mostly in borrowed words.'},
    {'id': 'o1', 'title': 'គ ឃ ង ជ', 'consonants': C('គ', 'ឃ', 'ង', 'ជ'), 'tip': 'o-series consonants are read with ô [ɔː]. គ kô sounds like ក kâ but with the o-series vowel.'},
    {'id': 'o2', 'title': 'ឈ ញ ទ ធ', 'consonants': C('ឈ', 'ញ', 'ទ', 'ធ')},
    {'id': 'o3', 'title': 'ន ព ភ ម', 'consonants': C('ន', 'ព', 'ភ', 'ម')},
    {'id': 'o4', 'title': 'យ រ ល វ', 'consonants': C('យ', 'រ', 'ល', 'វ')},
    {'id': 'o5', 'title': 'ឌ ឍ', 'consonants': C('ឌ', 'ឍ'), 'tip': 'Two rare o-series letters, mostly in Pali and Sanskrit words.'},
    {'id': 'v1', 'title': '◌ា ◌ិ ◌ី ◌ឹ', 'vowels': Vw('ា', 'ិ', 'ី', 'ឹ'), 'tip': 'A vowel sign reads one way after an a-series consonant and another after an o-series one.'},
    {'id': 'v2', 'title': '◌ឺ ◌ុ ◌ូ ◌ួ', 'vowels': Vw('ឺ', 'ុ', 'ូ', 'ួ')},
    {'id': 'v3', 'title': '◌ើ ◌ឿ ◌ៀ ◌េ', 'vowels': Vw('ើ', 'ឿ', 'ៀ', 'េ'), 'tip': 'Some vowel signs are written before the consonant, but they are still read after it.'},
    {'id': 'v4', 'title': '◌ែ ◌ៃ ◌ោ ◌ៅ', 'vowels': Vw('ែ', 'ៃ', 'ោ', 'ៅ')},
    {'id': 'k1', 'title': '◌ំ ◌ាំ ◌ុំ', 'combos': K('ំ', 'ាំ', 'ុំ'), 'tip': 'The small circle ំ adds a final m.'},
    {'id': 'k2', 'title': '◌ះ ◌ិះ ◌ុះ ◌េះ ◌ោះ', 'combos': K('ះ', 'ិះ', 'ុះ', 'េះ', 'ោះ'), 'tip': 'The two small circles ះ add a final h.'},
    {'id': 'm1', 'title': '◌់ ◌៉ ◌៊', 'marks': M('់', '៉', '៊'), 'tip': 'Marks written above a letter change its sound.'},
    {'id': 'm2', 'title': '◌៍ ◌ៈ ◌៌ ◌័', 'marks': M('៍', 'ៈ', '៌', '័')},
    {'id': 'i1', 'title': 'ឥ ឦ ឧ ឪ', 'indep': IV('ឥ', 'ឦ', 'ឧ', 'ឪ'), 'tip': 'Independent vowels stand alone, without a consonant. A few are common: ឥឡូវ "now", ឪពុក "father".'},
    {'id': 'i2', 'title': 'ឫ ឬ ឭ ឮ', 'indep': IV('ឫ', 'ឬ', 'ឭ', 'ឮ')},
    {'id': 'i3', 'title': 'ឯ ឰ ឱ ឳ', 'indep': IV('ឯ', 'ឰ', 'ឱ', 'ឳ')},
    {'id': 's1', 'title': 'Subscripts 1', 'subs': subs_ranked[0:5], 'tip': 'In a cluster, the second consonant is written as a small "foot" under the first.'},
    {'id': 's2', 'title': 'Subscripts 2', 'subs': subs_ranked[5:10]},
    {'id': 's3', 'title': 'Subscripts 3', 'subs': subs_ranked[10:15]},
    {'id': 'n1', 'title': '០ ១ ២ ៣ ៤', 'digits': ['d0', 'd1', 'd2', 'd3', 'd4'], 'tip': 'Khmer digits work just like Western ones: ១២ is 12.'},
    {'id': 'n2', 'title': '៥ ៦ ៧ ៨ ៩', 'digits': ['d5', 'd6', 'd7', 'd8', 'd9']},
]
for g in letter_groups:
    if g['id'].startswith('s'):
        g['title'] = 'Subscripts ' + ' '.join(next(c['sub'] for c in consonants if c['id'] == sid) for sid in g['subs'])
letters = {'sections': [
    {'title': 'Consonants: a-series', 'note': 'On their own they are read with â [ɑː].', 'groups': ['a1', 'a2', 'a3', 'a4']},
    {'title': 'Consonants: o-series', 'note': 'On their own they are read with ô [ɔː].', 'groups': ['o1', 'o2', 'o3', 'o4', 'o5']},
    {'title': 'Vowel signs', 'note': 'Each reads two ways, depending on the series of the consonant.', 'groups': ['v1', 'v2', 'v3', 'v4']},
    {'title': 'Vowels with ំ and ះ', 'groups': ['k1', 'k2']},
    {'title': 'Marks', 'groups': ['m1', 'm2']},
    {'title': 'Independent vowels', 'groups': ['i1', 'i2', 'i3']},
    {'title': 'Subscripts', 'note': 'Consonant clusters: the second letter is written under the first.', 'groups': ['s1', 's2', 's3']},
    {'title': 'Numerals', 'groups': ['n1', 'n2']},
], 'groups': letter_groups}

# ---- word course: topics split into lessons of at most four new words ----
UNITS = [
    ('u1', 'Hello!', 'Greetings, thanks, yes and no', 'សួស្តី', [
        ('Hello & thanks', '👋', ['សួស្តី', 'អរគុណ', 'លាហើយ'], 'Start here: three words. Each one is shown on a card before you practise it.'),
        ('Yes & no', '✅', ['បាទ', 'ចាស', 'ទេ', 'អត់អី'], 'Men say បាទ baat for yes; women say ចាស caah.'),
        ('Sorry & please', '🙏', ['សូមទោស', 'សុំទោស', 'មិនអីទេ', 'សូម', 'អញ្ជើញ'], None),
        ('Respectful greetings', '🪷', ['ជម្រាបសួរ', 'ជម្រាបលា', 'សំពះ', 'អរុណសួស្តី', 'រាត្រីសួស្ដី', 'លាសិនហើយ', 'ស្វាគមន៍', 'សំណាងល្អ'],
         'ជម្រាបសួរ is the respectful hello, said with a sampeah: palms together in front of the chest.'),
        ('How are you?', '😊', ['សុខ', 'សប្បាយ', 'ជា', 'ឈ្មោះ'], 'សុខសប្បាយ sok sapbaay means "well and happy".'),
    ]),
    ('u2', 'You & me', 'Saying I, you, he and she', 'ខ្ញុំ', [
        ('I & you', '🧑', ['ខ្ញុំ', 'អ្នក', 'ឯង', 'យើង'], None),
        ('Family words for "you"', '🫶', ['បង', 'ប្អូន', 'លោក', 'លោកស្រី', 'ពូ', 'មីង'],
         'Khmer uses family words for "you": បង for someone a bit older, ប្អូន for someone younger.'),
        ('Other people', '👥', ['គាត់', 'ពួកគេ', 'មនុស្ស', 'ភ្ញៀវ', 'ប្រុស', 'ស្រី'], None),
        ('Who & what', '❔', ['តើ', 'អ្វី', 'នរណា', 'មិត្តភក្តិ'], 'តើ at the start of a sentence makes it a polite question.'),
    ]),
    ('u3', 'Numbers', 'Khmer digits and counting to a million', '១ ២ ៣', [
        ('Zero to three', '០', ['សូន្យ', 'មួយ', 'ពីរ', 'បី'], 'Khmer has its own digits, ០ to ៩.', ['d0', 'd1', 'd2', 'd3']),
        ('Four to seven', '៤', ['បួន', 'ប្រាំ', 'ប្រាំមួយ', 'ប្រាំពីរ'], 'Six and seven are "five-one" and "five-two".', ['d4', 'd5', 'd6', 'd7']),
        ('Eight to ten', '៨', ['ប្រាំបី', 'ប្រាំបួន', 'ដប់', 'លេខ'], None, ['d8', 'd9']),
        ('Tens', '២០', ['ម្ភៃ', 'សាមសិប', 'សែសិប', 'ហាសិប', 'ហុកសិប', 'ចិតសិប', 'ប៉ែតសិប', 'កៅសិប'], None),
        ('Hundreds & more', '១០០', ['រយ', 'ពាន់', 'ម៉ឺន', 'សែន', 'លាន'], 'ម៉ឺន is ten thousand and សែន a hundred thousand: Khmer has single words for both.'),
        ('Building numbers', '២១', ['ដប់មួយ', 'ដប់ប្រាំ', 'ម្ភៃមួយ', 'មួយរយ', 'មួយពាន់', 'កន្លះ'], 'Numbers in between are built from the parts: ម្ភៃ (20) + មួយ (1) = 21.'),
    ]),
    ('u4', 'Food & drink', 'Order, taste and eat', 'ម្ហូប', [
        ('Rice & water', '🍚', ['បាយ', 'ទឹក', 'ម្ហូប', 'អាហារ'], 'បាយ is cooked rice, and also "a meal".'),
        ('Meat & fish', '🍗', ['ត្រី', 'សាច់', 'មាន់', 'សាច់មាន់', 'សាច់គោ', 'សាច់ជ្រូក', 'ក្ដាម', 'បង្គា'], 'សាច់ means meat: សាច់ + គោ (cow) = beef.'),
        ('Fruit & vegetables', '🥭', ['បន្លែ', 'ផ្លែឈើ', 'ចេក', 'ស្វាយ', 'ដូង', 'ក្រូច', 'ល្ហុង', 'ម្នាស់', 'ឪឡឹក'], None),
        ('Drinks', '☕', ['កាហ្វេ', 'តែ', 'ទឹកកក', 'ទឹកដោះគោ', 'ស្រា'], None),
        ('In the kitchen', '🧂', ['អង្ករ', 'ស្ករ', 'អំបិល', 'ម្ទេស', 'ខ្ទឹម', 'ទឹកត្រី', 'ប្រហុក'], None),
        ('Dishes', '🍜', ['នំបុ័ង', 'គុយទាវ', 'ស៊ុប', 'បបរ', 'នំ', 'ភោជនីយដ្ឋាន'], None),
        ('Tastes', '😋', ['ឆ្ងាញ់', 'ណាស់', 'ផ្អែម', 'ហឹរ', 'ជូរ', 'ប្រៃ', 'ល្វីង'], 'ណាស់ "very" comes after the describing word: ឆ្ងាញ់ណាស់ = very delicious.'),
        ('Hungry & full', '🍽️', ['ញ៉ាំ', 'ផឹក', 'ឃ្លាន', 'ស្រេក', 'ឆ្អែត'], None),
    ]),
    ('u5', 'Shopping', 'Prices, paying and bargaining', 'ផ្សារ', [
        ('At the market', '🛒', ['ផ្សារ', 'ទិញ', 'លក់', 'លុយ', 'ប្រាក់'], None),
        ('Prices', '💵', ['រៀល', 'ដុល្លារ', 'ថ្លៃ', 'ថោក', 'ប៉ុន្មាន', 'តម្លៃ'], 'ថ្លៃ is both "price" and "expensive", so ថ្លៃប៉ុន្មាន? is "how much?".'),
        ('Bargaining', '🤝', ['បញ្ចុះតម្លៃ', 'ពេក', 'ថែម', 'ដូរ', 'យក', 'ឲ្យ', 'បង់', 'ចាយ'], None),
        ('At the shop', '🏬', ['ផ្សារទំនើប', 'អតិថិជន', 'អ្នកលក់', 'គីឡូ', 'ទាំងអស់'], None),
    ]),
    ('u6', 'Colours & clothes', 'Red, blue, shirts and shoes', 'ពណ៌', [
        ('Colours', '🎨', ['ពណ៌', 'ក្រហម', 'ខៀវ', 'បៃតង', 'លឿង', 'ស', 'ខ្មៅ', 'ប្រផេះ', 'ផ្កាឈូក', 'មាស'], 'Colours often follow ពណ៌ "colour": ពណ៌ក្រហម = the colour red.'),
        ('Clothes', '👕', ['អាវ', 'ខោ', 'ស្បែកជើង', 'មួក', 'វ៉ែនតា', 'កាបូប', 'ទំហំ', 'ស្លៀក'], None),
    ]),
    ('u7', 'Family', 'Parents, brothers and sisters', 'គ្រួសារ', [
        ('Parents & children', '👪', ['ឪពុក', 'ម្ដាយ', 'ឪពុកម្ដាយ', 'កូន', 'ប្ដី', 'ប្រពន្ធ', 'គ្រួសារ'], None),
        ('Brothers & sisters', '👫', ['បងប្រុស', 'បងស្រី', 'ប្អូនប្រុស', 'ប្អូនស្រី'], 'Siblings are named by age first: បង older, ប្អូន younger, then ប្រុស male or ស្រី female.'),
        ('Old & young', '🧓', ['យាយ', 'តា', 'ចៅ', 'ក្មេង'], None),
    ]),
    ('u8', 'Body & health', 'Head to toe, and seeing a doctor', 'ខ្លួន', [
        ('Head & face', '🙂', ['ក្បាល', 'មុខ', 'ភ្នែក', 'ត្រចៀក', 'ច្រមុះ', 'មាត់', 'ធ្មេញ', 'អណ្ដាត', 'សក់'], None),
        ('Arms & legs', '🦵', ['ខ្លួន', 'ក', 'ដៃ', 'ជើង', 'ម្រាមដៃ', 'ស្មា', 'ជង្គង់', 'ពោះ', 'ខ្នង'], None),
        ('Inside the body', '🫀', ['បេះដូង', 'ឈាម', 'ស្បែក', 'ឆ្អឹង'], None),
        ('Feeling sick', '🤒', ['ឈឺ', 'ឈឺក្បាល', 'គ្រុន', 'ក្អក'], None),
        ('Seeing a doctor', '🏥', ['ពេទ្យ', 'គ្រូពេទ្យ', 'វេជ្ជបណ្ឌិត', 'មន្ទីរពេទ្យ', 'ថ្នាំ', 'ឱសថស្ថាន'], None),
    ]),
    ('u9', 'Time', 'Days, months and the clock', 'ពេល', [
        ('Today & tomorrow', '🌅', ['ថ្ងៃ', 'ថ្ងៃនេះ', 'ម្សិលមិញ', 'ស្អែក', 'ឥឡូវ'], None),
        ('Times of day', '🌇', ['ព្រឹក', 'ថ្ងៃត្រង់', 'រសៀល', 'ល្ងាច', 'យប់'], None),
        ('The clock', '🕗', ['ម៉ោង', 'នាទី', 'ពេល', 'សប្តាហ៍', 'ខែ', 'ឆ្នាំ', 'អាយុ'], None),
        ('Days of the week', '📅', ['ថ្ងៃច័ន្ទ', 'ថ្ងៃអង្គារ', 'ថ្ងៃពុធ', 'ថ្ងៃព្រហស្បតិ៍', 'ថ្ងៃសុក្រ', 'ថ្ងៃសៅរ៍', 'ថ្ងៃអាទិត្យ'], 'Every day starts with ថ្ងៃ thngay, "day".'),
        ('Months', '🗓️', ['មករា', 'កុម្ភៈ', 'មីនា', 'មេសា', 'ឧសភា', 'មិថុនា', 'កក្កដា', 'សីហា', 'កញ្ញា', 'តុលា', 'វិច្ឆិកា', 'ធ្នូ'], None),
        ('Before & after', '⏱️', ['មុន', 'ក្រោយ', 'ឆាប់', 'យឺត', 'រួច', 'ជានិច្ច', 'ពេលខ្លះ', 'ម្ដង', 'ម្ដងទៀត'], None),
    ]),
    ('u10', 'Weather & nature', 'Rain, sun, rivers and trees', 'អាកាសធាតុ', [
        ('Weather', '⛅', ['អាកាសធាតុ', 'ភ្លៀង', 'ខ្យល់', 'ពពក', 'មេឃ', 'ផ្គរ', 'ទឹកជំនន់', 'រដូវ'], None),
        ('Sun & stars', '☀️', ['ព្រះអាទិត្យ', 'ព្រះច័ន្ទ', 'ផ្កាយ', 'ភ្លឺ', 'ងងឹត'], None),
        ('Hot & cold', '🌡️', ['ក្ដៅ', 'ត្រជាក់', 'រងា', 'សើម', 'ស្ងួត'], None),
        ('Nature', '🌳', ['ដើមឈើ', 'ផ្កា', 'ទន្លេ', 'សមុទ្រ', 'ភ្នំ', 'បឹង', 'ព្រៃ', 'ដី', 'ថ្ម', 'ស្រែ', 'កោះ', 'ឆ្នេរ'], None),
    ]),
    ('u11', 'Getting around', 'Directions, places and transport', 'ផ្លូវ', [
        ('Directions', '🧭', ['ឆ្វេង', 'ស្ដាំ', 'ត្រង់', 'បត់', 'ឈប់', 'ត្រឡប់'], None),
        ('Where is it?', '📍', ['នៅ', 'ឯណា', 'ណា', 'ជិត', 'ឆ្ងាយ', 'ពី'], None),
        ('In & out', '↔️', ['ខាងលើ', 'ខាងមុខ', 'ខាងក្រោយ', 'ក្នុង', 'ក្រៅ'], None),
        ('Places', '🏯', ['ផ្ទះ', 'សណ្ឋាគារ', 'បង្គន់', 'សាលារៀន', 'វត្ត', 'ទីក្រុង', 'ផ្លូវ', 'ធនាគារ', 'ប្រៃសណីយ៍', 'ស្ថានីយ'], None),
        ('Cambodia', '🛕', ['កម្ពុជា', 'ភ្នំពេញ', 'សៀមរាប', 'អង្គរវត្ត', 'ខ្មែរ', 'ប្រទេស', 'ភូមិ', 'ខេត្ត', 'ផែនទី'], None),
        ('Transport', '🛵', ['ឡាន', 'ម៉ូតូ', 'កង់', 'ឡានក្រុង', 'យន្តហោះ', 'ទូក', 'ជិះ'], None),
        ('Travelling', '🧳', ['ទៅ', 'មក', 'ដើរ', 'រង់ចាំ', 'សំបុត្រ', 'លិខិតឆ្លងដែន'], None),
    ]),
    ('u12', 'At home', 'Rooms, things and the kitchen', 'ផ្ទះ', [
        ('Rooms', '🏠', ['បន្ទប់', 'ទ្វារ', 'បង្អួច', 'គ្រែ', 'ផ្ទះបាយ', 'បន្ទប់ទឹក'], None),
        ('Things', '💡', ['ភ្លើង', 'កង្ហារ', 'ទូរទស្សន៍', 'ទូរស័ព្ទ', 'កុំព្យូទ័រ', 'តុ', 'កៅអី'], None),
        ('Plates & spoons', '🥢', ['ចាន', 'ស្លាបព្រា', 'សម', 'ចង្កឹះ', 'កែវ', 'កាំបិត', 'ឆ្នាំង'], None),
    ]),
    ('u13', 'Animals', 'On the farm and in the wild', 'សត្វ', [
        ('On the farm', '🐄', ['សត្វ', 'គោ', 'ជ្រូក', 'ទា', 'សេះ', 'ក្របី'], None),
        ('Wild & at home', '🐘', ['ដំរី', 'ស្វា', 'ពស់', 'បក្សី', 'កណ្ដុរ', 'មូស', 'ឆ្កែ', 'ឆ្មា'], None),
    ]),
    ('u14', 'Work & school', 'Jobs, the office and the classroom', 'ការងារ', [
        ('Jobs', '👩‍🌾', ['កសិករ', 'ប៉ូលិស', 'ទាហាន', 'ចុងភៅ', 'កម្មករ', 'អ្នកនេសាទ'], None),
        ('At work', '💼', ['ការងារ', 'ធ្វើការ', 'ការិយាល័យ', 'ក្រុមហ៊ុន', 'ប្រាក់ខែ', 'ចៅហ្វាយ', 'ប្រជុំ'], None),
        ('At school', '📚', ['គ្រូ', 'គ្រូបង្រៀន', 'សិស្ស', 'រៀន', 'បង្រៀន', 'ថ្នាក់', 'សៀវភៅ', 'ក្រដាស', 'ប៊ិច', 'ខ្មៅដៃ'], None),
        ('Languages', '🗣️', ['ភាសា', 'អង់គ្លេស', 'និយាយ', 'ចេះ', 'អក្សរ', 'ពាក្យ', 'ប្រយោគ', 'បកប្រែ', 'ចិន', 'បារាំង', 'វៀតណាម', 'ថៃ', 'អាមេរិក'], None),
    ]),
    ('u15', 'Feelings', 'Happy, tired, afraid', 'ចិត្ត', [
        ('How I feel', '😊', ['រីករាយ', 'ព្រួយ', 'ខឹង', 'ខ្លាច'], None),
        ('Tired', '😴', ['ហត់', 'នឿយ', 'អស់កម្លាំង', 'អផ្សុក'], None),
        ('Heart & mind', '💗', ['ចិត្ត', 'ចូលចិត្ត', 'ស្រឡាញ់', 'នឹក', 'ភ្ញាក់ផ្អើល', 'អៀន'], 'Many feeling words are built on ចិត្ត "heart": ចូលចិត្ត "to like" is literally "enter the heart".'),
        ('Smile & cry', '😄', ['ញញឹម', 'សើច', 'យំ'], None),
    ]),
    ('u16', 'Little words', 'Questions, this and that, and, but', 'នេះ', [
        ('Question words', '❓', ['ពេលណា', 'ហេតុអ្វី', 'ម៉េច', 'អី'], 'Question words go where the answer would go: លោកទៅណា? "you go where?"'),
        ('This & that', '👉', ['នេះ', 'នោះ', 'ខ្លះ', 'មែន', 'មែនទេ', 'ពិត', 'ពិតជា'], None),
        ('And, or, but', '🔗', ['និង', 'ឬ', 'ជាមួយ', 'សម្រាប់', 'ព្រោះ', 'ប្រសិនបើ', 'ប៉ុន្តែ', 'ផង', 'ដែរ', 'ទៀត'], None),
        ('Not, already, will', '⏳', ['មិន', 'អត់', 'ហើយ', 'នឹង', 'បាន', 'អាច', 'ត្រូវ', 'ខុស'], 'To say "not", wrap the verb: មិន + verb + ទេ.'),
    ]),
    ('u17', 'Everyday verbs', 'Want, know, go and do', 'ធ្វើ', [
        ('Want & know', '❤️', ['ចង់', 'ដឹង', 'យល់', 'ជឿ', 'ស្គាល់', 'ចាំ', 'ភ្លេច', 'គិត', 'ត្រូវការ'], None),
        ('Talking', '💬', ['សួរ', 'ឆ្លើយ', 'ប្រាប់', 'ហៅ', 'ថា', 'ស្ដាប់', 'សរសេរ', 'អាន', 'មើល', 'ឃើញ'], None),
        ('Doing', '🔧', ['ធ្វើ', 'ជួយ', 'មាន', 'ប្រើ', 'រក', 'បាត់', 'ទទួល', 'ផ្ញើ', 'ចាប់ផ្ដើម', 'បញ្ចប់', 'លេង'], None),
        ('Moving', '🏃', ['ចូល', 'ចេញ', 'អង្គុយ', 'ឈរ', 'រត់', 'ហែលទឹក', 'បើក', 'បិទ'], None),
        ('Daily life', '🛁', ['ដេក', 'ងូតទឹក', 'លាង', 'ចំអិន', 'រស់', 'រៀបការ'], None),
    ]),
    ('u18', 'Describing things', 'Big, new, easy, many', 'ល្អ', [
        ('Big & small', '📏', ['ល្អ', 'ធំ', 'តូច', 'វែង', 'ខ្លី', 'ខ្ពស់', 'ទាប'], 'Describing words come after the noun, and ណាស់ "very" comes after the describing word.'),
        ('New & old', '✨', ['ស្អាត', 'ចាស់', 'ថ្មី', 'ធាត់', 'ស្គម', 'ស្រស់', 'កខ្វក់'], None),
        ('Easy & hard', '🧩', ['ងាយ', 'ពិបាក', 'សំខាន់', 'ស្ងាត់', 'រវល់', 'ទំនេរ', 'លឿន'], None),
        ('How much', '⚖️', ['ច្រើន', 'តិច', 'បន្តិច', 'ធ្ងន់', 'ស្រាល', 'ដូចគ្នា', 'ផ្សេង'], None),
    ]),
]

def chunk(lst, first_max=4):
    n = max(1, -(-len(lst) // 4))
    if len(lst) <= first_max: return [lst]
    size, extra = divmod(len(lst), n)
    out, i = [], 0
    for k in range(n):
        step = size + (1 if k < extra else 0)
        out.append(lst[i:i + step]); i += step
    return out

course = {'units': []}
introduced, order = set(), []
for uid, title, sub, ukm, groups in UNITS:
    unit = {'id': uid, 'title': title, 'subtitle': sub, 'km': ukm, 'lessons': []}
    for g in groups:
        gtitle, icon, kms, tip = g[0], g[1], g[2], g[3]
        digs = g[4] if len(g) > 4 else []
        ids_ = []
        for k in kms:
            if k not in by_km: problems.append(f'{uid}/{gtitle}: {k} is not a verified item'); continue
            if by_km[k] in introduced: problems.append(f'{uid}/{gtitle}: {k} already introduced'); continue
            ids_.append(by_km[k]); introduced.add(by_km[k])
        parts = chunk(ids_)
        for pi, part in enumerate(parts):
            lid = f'{uid}-{len(unit["lessons"]) + 1}'
            lesson = {'id': lid, 'title': gtitle + (f' {pi + 1}' if len(parts) > 1 else ''), 'icon': icon, 'items': part}
            if pi == 0 and tip: lesson['tip'] = tip
            if pi == 0 and digs: lesson['digits'] = digs
            unit['lessons'].append(lesson); order.append((lesson, set(introduced) - set().union(*[]) ))
    course['units'].append(unit)

# Place each sentence in the first lesson after which all its words have been taught (at most two per lesson).
seen, placed = set(), {}
flat = [l for u in course['units'] for l in u['lessons']]
for l in flat:
    seen |= set(l['items'])
    room = 2
    for s in sentences:
        if s['id'] in placed or room == 0: continue
        if all(t in seen for t in s['tokens']):
            l.setdefault('sentences', []).append(s['id']); placed[s['id']] = l['id']; room -= 1
for s in sentences:
    if s['id'] not in placed: problems.append(f"sentence {s['id']}: some words are never taught: {[t for t in s['tokens'] if t not in seen]}")
untaught = [it['id'] for it in items if it['id'] not in introduced]
if untaught: print('note: verified but not in a lesson:', untaught)

if problems:
    print('\n'.join(problems)); sys.exit(1)
os.makedirs(OUT, exist_ok=True)
dump = lambda name, obj: json.dump(obj, open(f'{OUT}/{name}', 'w'), ensure_ascii=False, indent=1)
dump('items.json', {'items': items})
dump('sentences.json', {'sentences': sentences})
dump('script.json', {'source': 'Wikipedia: Khmer script (consonant, subscript, dependent vowel, independent vowel and diacritic tables, UNGEGN + IPA); Khmer numerals',
                     'consonants': consonants, 'vowels': vowels, 'combos': combos, 'independents': independents, 'marks': marks, 'digits': digit_list})
dump('course.json', course)
dump('letters.json', letters)
print(f'items {len(items)}, sentences {len(sentences)}, units {len(course["units"])}, lessons {len(flat)}, letter groups {len(letter_groups)}, '
      f'combos {len(combos)}, independents {len(independents)}, marks {len(marks)}, subscripts taught {sum(len(g.get("subs", [])) for g in letter_groups)}')
