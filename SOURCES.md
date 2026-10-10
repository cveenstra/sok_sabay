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
| ខ្ញុំចង់ញ៉ាំបាយ | khñom cɑng ñam baay | I want to eat rice. | composed |
| ខ្ញុំចង់ផឹកកាហ្វេ | khñom cɑng phək kaafee | I want to drink coffee. | composed |
| ខ្ញុំចង់ទៅផ្សារ | khñom cɑng tɨw phsaa | I want to go to the market. | composed |
| ខ្ញុំចង់រៀនភាសាខ្មែរ | khñom cɑng riən phiəsaa khmae | I want to learn Khmer. | composed |
| ឆ្ងាញ់ណាស់ | chngañ nah | Very delicious! | composed |
| ថ្លៃណាស់ | thlay nah | Very expensive! | composed |
| តើផ្សារនៅឯណា | taə phsaa nɨw ʼae naa | Where is the market? | composed |
| ខ្ញុំស្រេក | khñom sreek | I'm thirsty. | composed |
| ខ្ញុំចូលចិត្តគុយទាវ | khñom coul cət kuy tiəw | I like kuyteav (noodle soup). | composed |

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
- **Audio:** no recorded audio is used. The app only speaks through a Khmer (km) voice the browser itself provides.
