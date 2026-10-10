"""Assemble data/*.json (run: python3 scripts/build_data.py) from the verified Wiktionary / Wikipedia extracts.

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

# Compound numbers, written per Wikipedia (Khmer language § Numerals: "intermediate
# numbers are formed by compounding the above elements"). Romanisation = the WT forms of the parts.
COMPOUND_NUMBERS = [
    ('eleven', ['ដប់', 'មួយ'], 11),
    ('fifteen', ['ដប់', 'ប្រាំ'], 15),
    ('twenty-one', ['ម្ភៃ', 'មួយ'], 21),
    ('one-hundred', ['មួយ', 'រយ'], 100),
    ('one-thousand', ['មួយ', 'ពាន់'], 1000),
]
NUMBER_VALUES = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8,
                 'nine': 9, 'ten': 10, 'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
                 'eighty': 80, 'ninety': 90}

STOP = set('to a an the of be is (said by) (formal) (casual) you i and or'.split())
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
for iid, parts, value in COMPOUND_NUMBERS:
    names = {11: 'eleven', 15: 'fifteen', 21: 'twenty-one', 100: 'one hundred', 1000: 'one thousand'}
    items.append({'id': iid, 'km': ''.join(parts), 'rom': ' '.join(wt(p) for p in parts), 'en': names[value], 'cat': 'number',
                  'value': value, 'digits': digits(value), 'src': 'composed: Wikipedia Khmer language § Numerals (compounding); parts from Wiktionary',
                  'note': ' + '.join(f'{p} {wt(p)}' for p in parts)})

by_km = {it['km']: it['id'] for it in items}
if problems:
    print('\n'.join(problems)); sys.exit(1)

# ---- sentences: (id, tokens (Khmer), English, source) ----
WP = 'wikipedia:Khmer language § Syntax'
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
    ('very-pretty', ['ស្រី', 'នោះ', 'ស្អាត', 'ណាស់'], 'That girl is very pretty.', 'wikipedia:Khmer language § Adjectives and adverbs'),
    ('this-morning', ['ព្រឹក', 'នេះ', 'បង', 'ទៅ', 'ណា', 'ខ្លះ'], 'Where are you going this morning?', 'wiktionary:ព្រឹក (usage example)'),
    ('two-dogs', ['ឆ្កែ', 'ពីរ'], 'two dogs', 'wikipedia:Khmer language § Nouns and pronouns'),
    # Composed by substituting verified words into the attested patterns above.
    ('want-rice', ['ខ្ញុំ', 'ចង់', 'ញ៉ាំ', 'បាយ'], 'I want to eat rice.', 'composed: pattern ខ្ញុំ ចង់ + verb (' + WP + ')'),
    ('want-coffee', ['ខ្ញុំ', 'ចង់', 'ផឹក', 'កាហ្វេ'], 'I want to drink coffee.', 'composed: pattern ខ្ញុំ ចង់ + verb (' + WP + ')'),
    ('want-market', ['ខ្ញុំ', 'ចង់', 'ទៅ', 'ផ្សារ'], 'I want to go to the market.', 'composed: pattern ទៅ + place (' + WP + ')'),
    ('learn-khmer', ['ខ្ញុំ', 'ចង់', 'រៀន', 'ភាសា', 'ខ្មែរ'], 'I want to learn Khmer.', 'composed: pattern ខ្ញុំ ចង់ + verb (' + WP + ')'),
    ('very-delicious', ['ឆ្ងាញ់', 'ណាស់'], 'Very delicious!', 'composed: pattern adjective + ណាស់ (wikipedia:Khmer language § Adjectives and adverbs)'),
    ('very-expensive', ['ថ្លៃ', 'ណាស់'], 'Very expensive!', 'composed: pattern adjective + ណាស់ (wikipedia:Khmer language § Adjectives and adverbs)'),
    ('where-market', ['តើ', 'ផ្សារ', 'នៅ', 'ឯណា'], 'Where is the market?', 'composed: pattern of "where is the toilet" (wiktionary)'),
    ('im-thirsty', ['ខ្ញុំ', 'ស្រេក'], "I'm thirsty.", "composed: pattern of \"I'm hungry\" (wiktionary)"),
    ('like-kuyteav', ['ខ្ញុំ', 'ចូលចិត្ត', 'គុយទាវ'], 'I like kuyteav (noodle soup).', 'composed: subject + verb + object (' + WP + ')'),
]
sentences = []
for sid, toks, en, src in SENTENCES:
    missing = [t for t in toks if t not in by_km]
    if missing: problems.append(f'sentence {sid}: tokens not items: {missing}'); continue
    sentences.append({'id': sid, 'tokens': [by_km[t] for t in toks], 'en': en, 'src': src})

# ---- script ----
cons_raw = [c for c in json.load(open(os.path.join(SRC, 'consonants_raw.json'))) if c['char'] not in ('ឝ', 'ឞ')]  # two obsolete letters
consonants = [{'id': f'c{i+1:02d}', 'char': c['char'], 'name': c['name_ungegn'], 'ipa_name': c['ipa_name'],
               'ipa': c['ipa'], 'value': c['value_ungegn'], 'series': c['series']} for i, c in enumerate(cons_raw)]
vow_raw = [v for v in json.load(open(os.path.join(SRC, 'vowels_raw.json'))) if v['vowel'] != '(none)']
vowels = [{'id': f'v{i+1:02d}', 'char': '◌' + v['vowel'], 'example': v['example'], 'ipa_a': v['ipa_a'],
           'ipa_o': v['ipa_o'], 'rom_a': v['ungegn_a'], 'rom_o': v['ungegn_o']} for i, v in enumerate(vow_raw)]
digit_words = ['សូន្យ', 'មួយ', 'ពីរ', 'បី', 'បួន', 'ប្រាំ', 'ប្រាំមួយ', 'ប្រាំពីរ', 'ប្រាំបី', 'ប្រាំបួន']
digit_list = [{'id': f'd{n}', 'char': chr(0x17E0 + n), 'value': n, 'word': digit_words[n], 'word_rom': wt(digit_words[n]),
               'word_item': by_km[digit_words[n]]} for n in range(10)]

# ---- course ----
C = lambda *chars: [c['id'] for c in consonants if c['char'] in chars]
Vw = lambda *signs: [v['id'] for v in vowels if v['char'][1:] in signs]
I = lambda *kms: [by_km[k] for k in kms]
S = lambda *ids: list(ids)
course = {'units': [
    {'id': 'u1', 'title': 'The Khmer script', 'subtitle': 'Consonants, their two series, and vowel signs', 'km': 'ក ខ គ', 'lessons': [
        {'id': 'script-1', 'title': 'Consonants 1', 'icon': 'ក', 'consonants': C('ក', 'ខ', 'គ', 'ឃ', 'ង', 'ច', 'ឆ', 'ជ'),
         'tip': 'Every consonant has an inherent vowel. a-series letters (like ក kâ) read with â [ɑː]; o-series letters (like គ kô) read with ô [ɔː].'},
        {'id': 'script-2', 'title': 'Consonants 2', 'icon': 'ញ', 'consonants': C('ឈ', 'ញ', 'ដ', 'ឋ', 'ឌ', 'ឍ', 'ណ', 'ត'),
         'tip': 'ឋ, ឌ and ឍ are rare and appear mostly in words borrowed from Pali and Sanskrit.'},
        {'id': 'script-3', 'title': 'Consonants 3', 'icon': 'ប', 'consonants': C('ថ', 'ទ', 'ធ', 'ន', 'ប', 'ផ', 'ព', 'ភ'),
         'tip': 'ប bâ is [ɓ] before a vowel, but [p] at the end of a syllable.'},
        {'id': 'script-4', 'title': 'Consonants 4', 'icon': 'ស', 'consonants': C('ម', 'យ', 'រ', 'ល', 'វ', 'ស', 'ហ', 'ឡ', 'អ'),
         'tip': 'អ ’â stands for a glottal stop and is the letter vowel signs are written on when a word starts with a vowel sound.'},
        {'id': 'vowels-1', 'title': 'Vowel signs 1', 'icon': 'អា', 'vowels': Vw('ា', 'ិ', 'ី', 'ឹ', 'ឺ', 'ុ', 'ូ', 'ួ'),
         'tip': 'A vowel sign sounds different on a-series and o-series consonants. ា after ក is [aː]; after គ it is [iːə].'},
        {'id': 'vowels-2', 'title': 'Vowel signs 2', 'icon': 'អៅ', 'vowels': Vw('ើ', 'ឿ', 'ៀ', 'េ', 'ែ', 'ៃ', 'ោ', 'ៅ'),
         'tip': 'Vowel signs can sit before, above, below or around the consonant, but are always read after it.'},
    ]},
    {'id': 'u2', 'title': 'Greetings & politeness', 'subtitle': 'Hello, thank you, yes and no', 'km': 'សួស្តី', 'lessons': [
        {'id': 'greet-1', 'title': 'Hello & goodbye', 'icon': '👋', 'items': I('សួស្តី', 'ជម្រាបសួរ', 'អរុណសួស្តី', 'លាហើយ', 'ជម្រាបលា', 'លាសិនហើយ'),
         'tip': 'ជម្រាបសួរ is the respectful hello, usually said with a sampeah: palms together in front of the chest.'},
        {'id': 'greet-2', 'title': 'Thank you & sorry', 'icon': '🙏', 'items': I('អរគុណ', 'សូមទោស', 'មិនអីទេ', 'អត់អី', 'សូម', 'អញ្ជើញ', 'សំពះ'),
         'sentences': S('thanks-a-lot')},
        {'id': 'greet-3', 'title': 'Yes & no', 'icon': '✅', 'items': I('បាទ', 'ចាស', 'ទេ', 'មិន', 'អត់'),
         'tip': 'Men say បាទ baat for yes; women say ចាស caah.'},
        {'id': 'greet-4', 'title': 'You & me', 'icon': '🧑', 'items': I('ខ្ញុំ', 'អ្នក', 'បង', 'ប្អូន', 'លោក', 'លោកស្រី', 'ពូ', 'មីង'),
         'tip': 'Khmer uses family words for "you". Call someone a bit older បង bɑɑng, someone younger ប្អូន pʼoun, a man you respect លោក look.'},
        {'id': 'greet-5', 'title': 'How are you?', 'icon': '😊', 'items': I('សុខ', 'សប្បាយ', 'ជា', 'ឈ្មោះ', 'អ្វី', 'តើ'),
         'sentences': S('how-are-you', 'im-fine', 'whats-your-name'),
         'tip': 'សុខសប្បាយ sok sapbaay means "well and happy". Ask it as a question by adding ជាទេ.'},
    ]},
    {'id': 'u3', 'title': 'Numbers', 'subtitle': 'Khmer digits and counting to a thousand', 'km': '១ ២ ៣', 'lessons': [
        {'id': 'num-1', 'title': 'One to five', 'icon': '១', 'digits': ['d0', 'd1', 'd2', 'd3', 'd4', 'd5'], 'items': I('សូន្យ', 'មួយ', 'ពីរ', 'បី', 'បួន', 'ប្រាំ'),
         'tip': 'Khmer has its own digits, ០ to ៩, written just like Western numbers: ១២ is 12.'},
        {'id': 'num-2', 'title': 'Six to ten', 'icon': '៦', 'digits': ['d6', 'd7', 'd8', 'd9'], 'items': I('ប្រាំមួយ', 'ប្រាំពីរ', 'ប្រាំបី', 'ប្រាំបួន', 'ដប់'),
         'tip': 'Six to nine are "five-one" to "five-four": ប្រាំ pram + មួយ muəy = 6.'},
        {'id': 'num-3', 'title': 'Tens', 'icon': '៣០', 'items': I('ម្ភៃ', 'សាមសិប', 'សែសិប', 'ហាសិប', 'ហុកសិប', 'ចិតសិប', 'ប៉ែតសិប', 'កៅសិប')},
        {'id': 'num-4', 'title': 'Bigger numbers', 'icon': '១០០', 'items': I('រយ', 'ពាន់', 'លេខ', 'ដប់មួយ', 'ដប់ប្រាំ', 'ម្ភៃមួយ', 'មួយរយ', 'មួយពាន់'),
         'tip': 'Numbers in between are built from the parts: ម្ភៃ mphɨy (20) + មួយ muəy (1) = 21.'},
    ]},
    {'id': 'u4', 'title': 'Food & market', 'subtitle': 'Order, taste and pay', 'km': 'ម្ហូប', 'lessons': [
        {'id': 'food-1', 'title': 'Food basics', 'icon': '🍚', 'items': I('បាយ', 'ទឹក', 'ត្រី', 'សាច់', 'បន្លែ', 'ផ្លែឈើ', 'ម្ហូប')},
        {'id': 'food-2', 'title': 'Meat & drinks', 'icon': '☕', 'items': I('មាន់', 'សាច់មាន់', 'សាច់គោ', 'សាច់ជ្រូក', 'កាហ្វេ', 'តែ', 'ទឹកកក', 'ទឹកដោះគោ')},
        {'id': 'food-3', 'title': 'Fruit & dishes', 'icon': '🥭', 'items': I('ចេក', 'ស្វាយ', 'ដូង', 'ក្រូច', 'នំបុ័ង', 'គុយទាវ', 'ស៊ុប', 'ភោជនីយដ្ឋាន')},
        {'id': 'food-4', 'title': 'Hungry & thirsty', 'icon': '😋', 'items': I('ញ៉ាំ', 'ផឹក', 'ឃ្លាន', 'ស្រេក', 'ឆ្ងាញ់', 'ផ្អែម', 'ហឹរ'),
         'sentences': S('im-hungry', 'im-thirsty', 'want-rice', 'want-coffee', 'very-delicious', 'like-kuyteav')},
        {'id': 'food-5', 'title': 'At the market', 'icon': '🛒', 'items': I('ផ្សារ', 'ទិញ', 'លក់', 'លុយ', 'រៀល', 'ដុល្លារ', 'ថ្លៃ', 'ថោក', 'ប៉ុន្មាន'),
         'sentences': S('how-much', 'very-expensive', 'want-market'),
         'tip': 'ថ្លៃ thlay is both "price" and "expensive", so ថ្លៃប៉ុន្មាន? is "how much?".'},
    ]},
    {'id': 'u5', 'title': 'Family & people', 'subtitle': 'Parents, siblings and friends', 'km': 'គ្រួសារ', 'lessons': [
        {'id': 'fam-1', 'title': 'Parents & children', 'icon': '👪', 'items': I('ឪពុក', 'ម្ដាយ', 'កូន', 'ប្ដី', 'ប្រពន្ធ', 'គ្រួសារ')},
        {'id': 'fam-2', 'title': 'Brothers & sisters', 'icon': '👫', 'items': I('បងប្រុស', 'បងស្រី', 'ប្អូនប្រុស', 'ប្អូនស្រី', 'ប្រុស', 'ស្រី'),
         'tip': 'Khmer names siblings by age first: បង older, ប្អូន younger, then ប្រុស male or ស្រី female.'},
        {'id': 'fam-3', 'title': 'Elders & friends', 'icon': '🧓', 'items': I('យាយ', 'តា', 'មិត្តភក្តិ', 'គាត់', 'យើង', 'ពួកគេ', 'គ្រូ', 'សិស្ស')},
    ]},
    {'id': 'u6', 'title': 'Time & days', 'subtitle': 'Today, tomorrow and the week', 'km': 'ថ្ងៃ', 'lessons': [
        {'id': 'time-1', 'title': 'Today & tomorrow', 'icon': '🌅', 'items': I('ថ្ងៃ', 'ថ្ងៃនេះ', 'ម្សិលមិញ', 'ស្អែក', 'ឥឡូវ', 'ព្រឹក', 'ល្ងាច', 'យប់'),
         'sentences': S('went-yesterday', 'school-tomorrow')},
        {'id': 'time-2', 'title': 'Clock & calendar', 'icon': '🕗', 'items': I('ម៉ោង', 'នាទី', 'សប្តាហ៍', 'ខែ', 'ឆ្នាំ', 'អាយុ')},
        {'id': 'time-3', 'title': 'Days of the week', 'icon': '📅', 'items': I('ថ្ងៃច័ន្ទ', 'ថ្ងៃអង្គារ', 'ថ្ងៃពុធ', 'ថ្ងៃព្រហស្បតិ៍', 'ថ្ងៃសុក្រ', 'ថ្ងៃសៅរ៍', 'ថ្ងៃអាទិត្យ'),
         'tip': 'Every day starts with ថ្ងៃ thngay, "day".'},
    ]},
    {'id': 'u7', 'title': 'Getting around', 'subtitle': 'Directions, places and transport', 'km': 'ផ្លូវ', 'lessons': [
        {'id': 'go-1', 'title': 'Directions', 'icon': '🧭', 'items': I('ឆ្វេង', 'ស្ដាំ', 'ត្រង់', 'ឈប់', 'ជិត', 'ឆ្ងាយ', 'ផ្លូវ', 'ត្រឡប់')},
        {'id': 'go-2', 'title': 'Places', 'icon': '🏯', 'items': I('ផ្ទះ', 'សណ្ឋាគារ', 'បង្គន់', 'សាលារៀន', 'វត្ត', 'ទីក្រុង', 'នៅ', 'ឯណា'),
         'sentences': S('where-toilet', 'where-market')},
        {'id': 'go-3', 'title': 'Cambodia', 'icon': '🛕', 'items': I('កម្ពុជា', 'ភ្នំពេញ', 'សៀមរាប', 'អង្គរវត្ត', 'ខ្មែរ', 'មក', 'ពី'),
         'sentences': S('where-from')},
        {'id': 'go-4', 'title': 'Transport', 'icon': '🛵', 'items': I('ឡាន', 'ម៉ូតូ', 'កង់', 'ឡានក្រុង', 'យន្តហោះ', 'ទូក', 'ទៅ', 'ដើរ', 'រង់ចាំ'),
         'sentences': S('where-going', 'stroll')},
    ]},
    {'id': 'u8', 'title': 'Everyday sentences', 'subtitle': 'Verbs, describing words, questions', 'km': 'និយាយ', 'lessons': [
        {'id': 'verb-1', 'title': 'Wants & feelings', 'icon': '❤️', 'items': I('ចង់', 'ចូលចិត្ត', 'ស្រឡាញ់', 'ដឹង', 'យល់', 'ជឿ', 'លេង'),
         'sentences': S('dont-understand', 'dont-know', 'dont-believe'),
         'tip': 'To say "not", wrap the verb: មិន + verb + ទេ. ខ្ញុំមិនយល់ទេ = I don\'t understand.'},
        {'id': 'verb-2', 'title': 'Daily actions', 'icon': '📖', 'items': I('រៀន', 'ធ្វើការ', 'ដេក', 'មើល', 'ស្ដាប់', 'សរសេរ', 'អាន', 'ជួយ'),
         'sentences': S('can-you-understand', 'learn-khmer')},
        {'id': 'verb-3', 'title': 'Describing things', 'icon': '✨', 'items': I('ល្អ', 'ធំ', 'តូច', 'ស្អាត', 'ក្ដៅ', 'ត្រជាក់', 'ច្រើន', 'តិច', 'ណាស់', 'ឈឺ'),
         'sentences': S('very-pretty'),
         'tip': 'Describing words come after the noun, and ណាស់ nah ("very") after the describing word.'},
        {'id': 'verb-4', 'title': 'Questions', 'icon': '❓', 'items': I('នរណា', 'ពេលណា', 'ហេតុអ្វី', 'អី', 'ណា', 'នេះ', 'នោះ', 'ខ្លះ', 'ហើយ', 'នឹង'),
         'sentences': S('already-left', 'this-morning'),
         'tip': 'Question words go where the answer would go: លោកទៅណា? "you go where?" = Where are you going?'},
        {'id': 'verb-5', 'title': 'Speaking Khmer', 'icon': '🗣️', 'items': I('និយាយ', 'ភាសា', 'អង់គ្លេស', 'ចេះ', 'អក្សរ', 'មាន', 'បាន', 'បន្តិច', 'ម្ដងទៀត'),
         'sentences': S('speak-english', 'cant-speak-khmer')},
        {'id': 'verb-6', 'title': 'Animals & more', 'icon': '🐕', 'items': I('ឆ្កែ', 'ឆ្មា', 'មាន់', 'ត្រី', 'ពីរ', 'ធំ'),
         'sentences': S('two-dogs')},
    ]},
]}

# compound numbers were added after by_km was first built; add any missing ids
for it in items: by_km[it['km']] = it['id']
if problems:
    print('\n'.join(problems)); sys.exit(1)
os.makedirs(OUT, exist_ok=True)
dump = lambda name, obj: json.dump(obj, open(f'{OUT}/{name}', 'w'), ensure_ascii=False, indent=1)
dump('items.json', {'items': items})
dump('sentences.json', {'sentences': sentences})
dump('script.json', {'source': 'Wikipedia: Khmer script (consonant and dependent vowel tables, UNGEGN + IPA); Khmer numerals',
                     'consonants': consonants, 'vowels': vowels, 'digits': digit_list})
dump('course.json', course)
print(f'items {len(items)}, sentences {len(sentences)}, consonants {len(consonants)}, vowels {len(vowels)}, lessons {sum(len(u["lessons"]) for u in course["units"])}')
