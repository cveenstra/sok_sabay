# Sources

Everything in `data/` was checked against a published source before it went in. Anything I couldn't confirm was left out (see the end of this file). Wiktionary and Wikipedia text is CC BY-SA 4.0, so the course data is shared under the same licence, with attribution here.

## Words and phrases (`data/items.json`)

- **Spelling, meaning and romanisation:** every item's Khmer spelling was looked up on English Wiktionary. Its `rom` field is the **WT romanisation** that Wiktionary gives for that exact spelling, and its English gloss is one of the senses Wiktionary lists. Each item records its page in `src` (for example `wiktionary:អរគុណ`).
- **Build check:** the build fails if a gloss shares no word with the Wiktionary senses.
- **Compound numbers:** 11, 15, 21, 100 and 1,000 are built from verified parts. Wikipedia's [Khmer language § Numerals](https://en.wikipedia.org/wiki/Khmer_language#Numerals) says intermediate numbers are formed by compounding. Their `src` says `composed`.
- **Spelling variants:** where Wiktionary files a word under a variant, the course uses the spelling that has the full entry. Examples are ស្ដាំ, ស្ដាប់ and ក្ដៅ, written with subscript ដ rather than ត.

## Script (`data/script.json`)

- **Consonants and dependent vowels:** parsed from the consonant and dependent-vowel tables in Wikipedia's [Khmer script](https://en.wikipedia.org/wiki/Khmer_script) article.
  - Letter names use **UNGEGN** transliteration, plus IPA. The a/o series is taken from the UNGEGN name: names ending in *â* are a-series, *ô* are o-series.
  - The two obsolete letters ឝ and ឞ are excluded, leaving the 33 modern consonants: 15 a-series and 18 o-series.
- **Subscripts:** each consonant's subscript form (coeng + letter) comes from the same consonant table; ឡ has none. The example word for each is the shortest course word containing it.
- **Independent vowels:** from the article's independent-vowel table (UNGEGN + IPA). ឨ (obsolete) and ឩ (no UNGEGN form given) are left out, leaving 12.
- **Marks (diacritics):** the Khmer names, UNGEGN names and functions come from the article's diacritics table. The one-line summaries in the app are paraphrases of its "Function" column. Nine are taught: ំ ះ ៈ ់ ៉ ៊ ៍ ៌ ័.
- **Vowels with ំ and ះ:** the eight combinations in the article's "Modification by diacritics" table, read for both series.
- **Syllables in the Letters lessons** (for example ក + ា = *ka* [kaː]) are built by the spelling rule: the consonant's UNGEGN value and first IPA value, plus the vowel's a- or o-series value from the table. They show how the script works, not the irregular pronunciation of every real word. Real words in the Letters lessons are course words, so they carry their own Wiktionary romanisation.
- `scripts/parse_script_extra.py` re-extracts these tables from the article's wikitext.
- **Numerals:** the digits ០–៩ and number words come from Wikipedia's [Khmer numerals](https://en.wikipedia.org/wiki/Khmer_numerals) and Khmer language articles. `scripts/check-data.mjs` checks that each digit is the right Unicode code point (U+17E0 + value).

## Grammar notes and sentences (`data/sentences.json`)

Sentence patterns follow Wikipedia's [Khmer language § Syntax](https://en.wikipedia.org/wiki/Khmer_language#Syntax):
- subject-verb-object order
- មិន … ទេ negation
- ទេ / ណា questions
- ហើយ (already) and នឹង (will)
- describing words after the noun, and ណាស់ "very"

Each sentence's romanisation is joined from its words' WT forms.

- **Attested** sentences appear as given in one of these:
  - a Wiktionary entry or usage example
  - a Khmer translation on an English Wiktionary phrasebook page (for example "how are you", "where is the toilet", "I don't know", "how much")
  - an interlinear example in the Wikipedia article
- **Composed** sentences put verified words into one of those attested patterns, for example ខ្ញុំ ចង់ + verb. They are marked `composed` in `src`, and a correction from a native speaker is very welcome.

| Khmer | Romanisation | English | Status |
|---|---|---|---|
| សុខសប្បាយជាទេ | sok sapbaay ciə tei | How are you? | attested |
| ខ្ញុំសុខសប្បាយ | khñom sok sapbaay | I'm fine. | attested |
| អរគុណច្រើន | ʼɑɑ kun craən | Thank you very much. | attested |
| តើអ្នកឈ្មោះអ្វី | taə nĕək chmŭəh ʼvəy | What is your name? | attested |
| ខ្ញុំឃ្លាន | khñom khliən | I'm hungry. | attested |
| តើបង្គន់នៅឯណា | taə bɑngkŭən nɨw ʼae naa | Where is the toilet? | attested |
| ខ្ញុំមិនយល់ទេ | khñom mɨn yŭəl tei | I don't understand. | attested |
| ខ្ញុំមិនដឹងទេ | khñom mɨn dəng tei | I don't know. | attested |
| ថ្លៃប៉ុន្មាន | thlay ponmaan | How much (does it cost)? | attested |
| តើអ្នកនិយាយភាសាអង់គ្លេសទេ | taə nĕək niyiəy phiəsaa ʼɑngkleih tei | Do you speak English? | attested |
| ខ្ញុំមិនចេះនិយាយភាសាខ្មែរទេ | khñom mɨn ceh niyiəy phiəsaa khmae tei | I can't speak Khmer. | attested |
| តើអ្នកមកពីណា | taə nĕək mɔɔk pii naa | Where are you from? | attested |
| ខ្ញុំចង់ទៅដើរលេង | khñom cɑng tɨw daə leeng | I want to go for a stroll. | attested |
| ខ្ញុំមិនជឿទេ | khñom mɨn cɨə tei | I don't believe it. | attested |
| គាត់ទៅម្សិលមិញ | kŏət tɨw msəl mɨñ | He went yesterday. | attested |
| គាត់ទៅហើយ | kŏət tɨw haəy | He has already left. | attested |
| ស្អែកខ្ញុំនឹងទៅសាលារៀន | sʼaek khñom nɨng tɨw saalaa riən | Tomorrow I will go to school. | attested |
| លោកទៅណា | look tɨw naa | Where are you going? | attested |
| លោកស្ដាប់បានទេ | look sdap baan tei | Can you understand? | attested |
| ស្រីនោះស្អាតណាស់ | srəy nuh sʼaat nah | That girl is very pretty. | attested |
| ព្រឹកនេះបងទៅណាខ្លះ | prɨk nih bɑɑng tɨw naa khlah | Where are you going this morning? | attested |
| ឆ្កែពីរ | chkae pii | two dogs | attested |
| ម៉ោងប៉ុន្មានហើយ | maong ponmaan haəy | What time is it? | attested |
| តើអ្នកមានអាយុប៉ុន្មានហើយ | taə nĕək miən ʼaayuʼ ponmaan haəy | How old are you? | attested |
| ខ្ញុំត្រូវការគ្រូពេទ្យ | khñom trəw kaa kruu pɛɛt | I need a doctor. | attested |
| ជួយហៅប៉ូលិសមក | cuəy haw poulih mɔɔk | Call the police! | attested |
| តើអ្នករស់នៅឯណា | taə nĕək rŭəh nɨw ʼae naa | Where do you live? | attested |
| ខ្ញុំឈឺ | khñom chɨɨ | I'm sick. | attested |
| ខ្ញុំរងា | khñom rɔngiə | I'm cold. | attested |
| នឹកឯង | nɨk ʼaeng | I miss you. | attested |
| ខ្ញុំអស់កម្លាំង | khñom ʼɑh kɑmlang | I'm tired. | attested |
| ខ្ញុំចង់ញ៉ាំបាយ | khñom cɑng ñam baay | I want to eat rice. | composed |
| ខ្ញុំចង់ផឹកកាហ្វេ | khñom cɑng phək kaafee | I want to drink coffee. | composed |
| ខ្ញុំចង់ទៅផ្សារ | khñom cɑng tɨw phsaa | I want to go to the market. | composed |
| ខ្ញុំចង់រៀនភាសាខ្មែរ | khñom cɑng riən phiəsaa khmae | I want to learn Khmer. | composed |
| ឆ្ងាញ់ណាស់ | chngañ nah | Very delicious! | composed |
| ថ្លៃណាស់ | thlay nah | Very expensive! | composed |
| តើផ្សារនៅឯណា | taə phsaa nɨw ʼae naa | Where is the market? | composed |
| ខ្ញុំស្រេក | khñom sreek | I'm thirsty. | composed |
| ខ្ញុំចូលចិត្តគុយទាវ | khñom coul cət kuy tiəw | I like kuyteav (noodle soup). | composed |
| តើមន្ទីរពេទ្យនៅឯណា | taə mŭəntii pɛɛt nɨw ʼae naa | Where is the hospital? | composed |
| តើធនាគារនៅឯណា | taə thĕəʼniəkiə nɨw ʼae naa | Where is the bank? | composed |
| ខ្ញុំត្រូវការទឹក | khñom trəw kaa tɨk | I need water. | composed |
| ខ្ញុំត្រូវការថ្នាំ | khñom trəw kaa thnam | I need medicine. | composed |
| ខ្ញុំឈឺក្បាល | khñom chɨɨ kbaal | I have a headache. | composed |
| ខ្ញុំហត់ | khñom hɑt | I'm tired (out of breath). | composed |
| ខ្ញុំខ្លាច | khñom khlaac | I'm afraid. | composed |
| ខ្ញុំរវល់ | khñom rɔvŭəl | I'm busy. | composed |
| ខ្ញុំចង់ទិញមួក | khñom cɑng tɨñ muək | I want to buy a hat. | composed |
| អាវនេះថ្លៃពេក | ʼaaw nih thlay peik | This shirt is too expensive. | composed |
| ថ្ងៃនេះក្ដៅណាស់ | thngay nih kdaw nah | It is very hot today. | composed |
| ផ្សារឆ្ងាយទេ | phsaa chngaay tei | Is the market far? | composed |
| ឆ្មាពីរ | chmaa pii | two cats | composed |
| ខ្ញុំចូលចិត្តពណ៌ក្រហម | khñom coul cət pɔə krɑhɑɑm | I like the colour red. | composed |
| ដំរីធំណាស់ | dɑmrəy thom nah | The elephant is very big. | composed |
| ខ្ញុំជាគ្រូបង្រៀន | khñom ciə kruu bɑngriən | I am a teacher. | composed |
| តើអ្នកចង់ផឹកកាហ្វេទេ | taə nĕək cɑng phək kaafee tei | Do you want to drink coffee? | composed |
| សូមបើកទ្វារ | soum baək tviə | Please open the door. | composed |

## Address terms and politeness

Glosses and usage notes come from each word's Wiktionary entry:
- បង, ប្អូន, លោក, លោកស្រី, ពូ and មីង, including their use as "you"
- បាទ (men's yes) and ចាស (women's yes)
- សំពះ, the sampeah greeting: palms together in front of the chest, as a sign of respect when meeting or leaving

## Checked and left out

- **តុកតុក:** Wiktionary gives it as a variant of តុកៗ, "knock knock", not "tuk-tuk", so the word is not in the course.
- **ភាសាខ្មែរ "Khmer language":** this has no entry of its own (it redirects to ខ្មែរ). The course builds it from ភាសា + ខ្មែរ inside sentences instead.
- **No Wiktionary entry, not used:**
  - ពងមាន់ (chicken egg)
  - ជីតា (grandfather; តា is used instead)
  - ព្រលានយន្តហោះ (airport)
  - ចង់បាន
  - គិតលុយ
  - យឺតៗ
  - រួចរាល់
  - ផ្អែមល្ហែម
- **Phrasebook translations not used:**
  - The "you're welcome" page lists one Khmer form whose romanisation doesn't match its spelling.
  - "Nice to meet you" has no Khmer translation.
- **Round 2 (October 2026), no Wiktionary entry, not used:**
  - រដូវវស្សា (rainy season) and រដូវប្រាំង (dry season); រដូវ "season" is used
  - អ្នកបើកបរ (driver), អ្នកជិតខាង (neighbour)
  - សប្បាយចិត្ត (happy), ពិបាកចិត្ត (troubled), សោកសៅ (sad), ខកចិត្ត (disappointed)
  - យ៉ាងម៉េច (how), ប៉ុណ្ណា (how much), ហើយនិង (and)
  - អាម៉ុក (amok), ស្រាបៀរ (beer), ធុរេន (durian), ម្ហូបអាហារ (food)
  - រាល់ថ្ងៃ (every day), ខាងក្រោម (below), ពាក់កណ្ដាល (half); កន្លះ "half" is used
  - រាត្រីសួស្តី, សាយ័ណ្ហសួស្តី, ទិវាសួស្តី (good night / evening / afternoon with ត). Good night is in, under the spelling Wiktionary files: រាត្រីសួស្ដី
  - សូមស្វាគមន៍ (welcome); ស្វាគមន៍ is used. ត្រូវហើយ (that's right). ខួបកំណើត (birthday)
- **Round 2, checked but the meaning didn't match:**
  - ហាង: Wiktionary gives "hot, pungent", not "shop"
  - ត្នោត: Wiktionary gives "sugar palm", not "brown"
  - ហេតុអី and ចម្អិន are only listed as alternative forms. ហេតុអ្វី "why" and ចំអិន "to cook" are used instead.
- **Left out on purpose:** តែ "but, only" (the course already has តែ "tea"); ពង "egg" (Wiktionary lists blister and boil first).
- **Audio:** no recorded audio is used. The app only speaks through a Khmer (km) voice the browser itself provides.
