from ebooklib import epub
import ebooklib
import os
import shutil
from io import StringIO
import nltk
import spacy
import time

from bs4 import BeautifulSoup

import string
import re
import pandas as pd
from tqdm.notebook import trange, tqdm

from collections import OrderedDict
from collections import Counter

# In[1]:
# Webpage navigation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def epub2thtml(epub_path):
    book = epub.read_epub(epub_path)
    chapters = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            chapters.append(item.get_content())

    return chapters


blacklist = [ '[document]',   'noscript', 'header',   'html', 'meta', 'head','input', 'script',   'style']


def chap2text(chap):
    output = ''
    soup = BeautifulSoup(chap, 'html.parser')
    text = soup.find_all(text=True)

    for t in text:
        if t.parent.name not in blacklist:
            output += '{} '.format(t)

    return output


def thtml2ttext(thtml):
    Output = []
    for html in thtml:
        text =  chap2text(html)
        Output.append(text)

    return Output

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    # allows for the more natural sorting of text (1, 2, 3, ... instead of 1, 10, 2, 3,...)
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split('(\d+)', text) ]

# In[1]:
'''
    PseudoCode
    1. Open epub file
    2. Get chapters of epub file
    3. Filter chapters (ignore front / back material)
    4. Get text of each chapter in book
    5. Split the text into words (split by whitespace)
    6. Filter word list to only get unique words
    7. Ignore capitalized words; ignore words with digits [0-9]
    8. Check that word is "new" - i.e. not already included in previous chapters or known vocabulary
    9. Make text file of new unique words
    10. Use selenium to retrieve English translations of words (Google translate or DeepL)
    11. Make dataframe of Dutch, English word pairs, and .mp3 file name - .csv file with AnkiApp / AnkiMobile structure
    12. Use selenium to retrieve media - audio of Dutch words
    13. Save audio in chapter specific subfolders
    14. Check that all media files are included
    15. Make zip file of each chapter subfolder - includes .mp3's and .csv file (AnkiApp specific)
    16. Use selenium to upload zip folders to AnkiApp website (https://web.ankiapp.com/#/import)
'''

# In[6]:
'''
    Multiple words at a time

    DeepL Translator is another (possibly better) option
    https://www.deepl.com/translator#nl/en/reden%0Aklimop%0Aandere%0Aontsnapt%0Aonvermijdelijk
'''

def translate_dutch_words(string_of_words):
    '''
        Input: string of words delimited by \n
            example: ik\nben\neen\nmens (ik ben een mens)
        Output: translated text delimited by \n
            example: I\nam\na\nperson (I am a person)
        limited to 5000 characters, including \n (\n = 1 character)
    '''
    # replace the return character '\n' with '%0A'
    # later it might be useful to replace the space character ' ' with '%20'
    assert (len(string_of_words) <= 5000), 'String is too long: > 5000 characters'
    str = string_of_words.replace('\n', '%0A')
    # use the modified string to make a url to retrieve the translated text
    # sl = source language, tl = target language
    # could make a dictionary of the possible source and target languages ...
    driver.get("https://translate.google.com/?sl=nl&tl=en&text={}&op=translate".format(str))
    # driver.get("https://www.deepl.com/translator#nl/en/{}".format(str))   # DeepL
    # <textarea dl-test="translator-target-input" <-- translated text appears in this field

    try:    # wait for the translated text to appear
        # "//div[@data-language='en']"
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-language-name='English']"))
        )

        translated_text = element.get_attribute('data-text')
    except:
        print('Could not locate element')
        translated_text = ''

    return translated_text


def Download_Word_MP3(word, language):
    text = driver.find_element(By.XPATH, "//textarea[@name='text']")

    text.send_keys(word)
    driver.find_element(By.NAME, "voice").send_keys(language + Keys.TAB + Keys.ENTER)

    element = wait.until(EC.element_to_be_clickable((By.XPATH,
                    "//a[@class='card__action' and text() = 'Download']")))
    overlay = wait.until(EC.invisibility_of_element_located((By.XPATH,
                    "//div[@class='overlay']")))

    element.click()


def check_word_list_mp3s(word_list, directory):
    '''
        Check that .mp3 exists for all words in word_list
        looks for mp3's in directory
    '''
    mp3_list = os.listdir(directory)

    mp3_list = [x for x in mp3_list if '.mp3' in x]
    mp3_list = [os.path.splitext(x)[0] for x in mp3_list]
    mp3_list.sort(key=natural_keys)

    if word_list == mp3_list:
        missing_words = False
    else:
        missing_words = [x for x in word_list if x not in mp3_list]

    return missing_words

# In[1]:
input_path = '/Users/nicholasbrady/Documents/Post-Doc/Dutch/Books/'
book_ = 'Harry Potter en De Orde van de Feniks by Rowling, Joanne Kathleen.epub'
book_ = 'Harry Potter en de Vuurbeker by Rowling, Joanne Kathleen.epub'

chapters = epub2thtml(os.path.join(input_path, book_) )

# In[2]:
Vocabulary_dir = '/Users/nicholasbrady/Documents/Post-Doc/Dutch/Books/Vocabulary/HarryPotterEnDeOrdeVanFeniks/'
Vocabulary_dir = '/Users/nicholasbrady/Documents/Post-Doc/Dutch/Books/Vocabulary/'


# load existing vocabulary list
Vocabulary_list = []

# HP_4_dir = '/Users/nicholasbrady/Documents/Post-Doc/Dutch/Books/Vocabulary/'
# for file in os.listdir(HP_4_dir):
#     if file.startswith("HP_4_"):
#         if "_NL_ENG.txt" not in file:
#             textfile = open(HP_4_dir + file, "r")
#             file_text = textfile.read()
#             word_list = file_text.split('\n')
#
#             Vocabulary_list += word_list


# get the text of each chapter and filter for new unique words
# new unique words are output to .txt file
ch_number = 0
for chapter in chapters:
    chapter_text = chap2text(chapter)

    # remove punctuation
    chapter_text = re.sub(r'[^\w\s]', '', chapter_text)
    # get list of individual words
    words = chapter_text.split()

    # don't include table of contents, front / back material
    # filter just to get chapters
    if not(words):
        continue
    if words[0] != 'Hoofdstuk':
        continue

    # get unique words
    new_words = list(OrderedDict.fromkeys(words))
    # remove words that are already in our vocabulary list
    new_words = [x for x in new_words if x not in Vocabulary_list]
    # Remove strings that contain digits [0-9]
    new_words = [x for x in new_words if not any(x1.isdigit() for x1 in x)]
    # Remove capitalized words
    new_words = [x for x in new_words if not any(x1.isupper() for x1 in x)]

    # add new_words to Vocabulary_list
    Vocabulary_list += new_words

    # Make .txt file of new words for each chapter
    ch_number += 1
    textfile = open(Vocabulary_dir + "HP_4_Hoofdstuk_{}.txt".format(ch_number), "w")
    for word in new_words:
        textfile.write(word + "\n")
    textfile.close()

# In[3]:
'''Retrieve English Translations of Dutch Words'''
# get a list of the files
# files contain the chapter specific new unique words
file_list = os.listdir(Vocabulary_dir)
file_list = [x for x in file_list if '.txt' in x]
file_list.sort(key=natural_keys)

audio_dir = Vocabulary_dir + 'Audio/'

try:
    os.makedirs(audio_dir)
except:
    pass

for file in file_list:
    filename, extension = os.path.splitext(file)
    try:
        os.makedirs(audio_dir + filename)
    except:
        pass

chromeOptions = webdriver.ChromeOptions()
prefs = {"download.default_directory" : audio_dir}
chromeOptions.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chromeOptions)
driver.set_page_load_timeout(10)
wait = WebDriverWait(driver, 10)

# add a check for redirect for Google translate or use DeepL.com

# In[4]:
# retrieve English translations of Dutch words (up to 5000 characters) using 'translate_dutch_words'
# files that contain more than 5000 characters are systematically split into segments and then concatenated
for file in file_list:
    filename, extension = os.path.splitext(file)

    file_ = open(Vocabulary_dir + file, 'r')
    file_text = file_.read()

    # Google translate has a 5000 character limit, if the number of characters is > 5000 file is split up
    ind0 = 0
    eng_translation = ''
    while ind0 + 5000 < len(file_text):
        # find the first '\n' before 5000
        ind_ = file_text[ind0 + 5000::-1].find('\n')
        segment = file_text[ind0:ind0+5000-ind_]
        ind0 = ind0 + 5000 - ind_

        eng_translation += translate_dutch_words(segment)
        eng_translation += '\n'

    eng_translation += translate_dutch_words(file_text[ind0:])

    # make dataframe of word pairs (Nederlands, English)
    # df = pd.read_table(Vocabulary_dir + file, header=None)
    df = pd.read_table(StringIO(file_text), header=None)
    df.columns = ['Nederlands']
    df_ = pd.read_table(StringIO(eng_translation), header=None)
    df['English'] = df_

    mp3_list = ['{}.mp3'.format(word) for word in df['Nederlands']]

    df['mp3'] = mp3_list

    # Data frame structure AnkiApp - need to save as .csv file
    # Front, Back, Tags, Image(front), Image(back), Sound(front), Sound(back)
    df['Tags'] = ''
    df['Image(front)'] = ''
    df['Image(back)'] = ''
    df['mp3(back)'] = ''

    cols = ['Nederlands', 'English', 'Tags', 'Image(front)', 'Image(back)', 'mp3', 'mp3(back)']
    df = df[cols]

    df.to_csv(audio_dir + filename + '/{}_NL_ENG_MP3.csv'.format(filename), index=False, header=False)
    # df.to_csv(_file_PAIR, index=False, header=False, encoding='utf-8-sig') # AnkiMobile

# In[5]:
'''
    Retrieve .mp3 sound of Dutch words
    use website soundoftext.com
'''

language = 'dutch'

for chapter_file in file_list:
    chapter_name = os.path.splitext(chapter_file)[0]
    file_ = open(Vocabulary_dir + chapter_file, 'r')
    file_text = file_.read()

    words = file_text.split('\n')
    # remove empty words
    words = list(filter(None, words))
    # remove words where the mp3 has already been downloaded

    # make a list of the mp3 files that already exist
    # check the chapter subfolder as well as the main audio folder
    audio_files = os.listdir(audio_dir) + os.listdir(audio_dir + chapter_name)
    audio_files = [x for x in audio_files if '.mp3' in x]
    audio_files = [os.path.splitext(mp3)[0] for mp3 in audio_files]
    audio_files.sort(key=natural_keys)

    words = [x for x in words if x not in audio_files]
    words.sort(key=natural_keys)

    if not words:
        pass

    else:
        driver.get('https://soundoftext.com/')

        for word in words:
            try:    # timeout errors happen, just continue
                Download_Word_MP3(word, language)
            except:
                pass

        time.sleep(5)
    # files gets saved to audio folder, then we need to move it to the proper folder
    words = file_text.split('\n')
    # remove empty words
    words = list(filter(None, words))
    for word in words:
        try:
            shutil.move(audio_dir + '{}.mp3'.format(word), audio_dir + chapter_name)
        except:
            pass

# In[6]:
'''
    Check that everything has been downloaded
'''
zip_files = os.listdir(audio_dir)
zip_files = [x for x in zip_files if '.zip' in x]
zip_files.sort(key=natural_keys)

for chapter in file_list:
    # if the zip file exists, assume it has all the necessary information
    chapter_name = os.path.splitext(chapter)[0]
    if '{}.zip'.format(chapter_name) in zip_files:
        continue

    file_ = open(Vocabulary_dir + chapter, 'r')
    file_text = file_.read()
    word_list = file_text.split('\n')
    word_list.sort(key=natural_keys)
    # remove empty words
    word_list = list(filter(None, word_list))

    _files_ = os.listdir(audio_dir + chapter_name)
    csv_file = False
    if '{}_NL_ENG_MP3.csv'.format(chapter_name) in _files_:
        csv_file = True

    missing_words = check_word_list_mp3s(word_list, audio_dir + chapter_name)

    if not(missing_words) and csv_file:
        print('No missing mp3\'s in {}'.format(chapter_name))
        shutil.make_archive(audio_dir + chapter_name, 'zip', audio_dir + chapter_name)

    else:
        print('{} Missing Words:'.format(chapter_name))
        print(missing_words)

# In[7]:
'''
    Upload zip file to AnkiApp
'''

for zip_ in zip_files[12:]:
    driver.get('https://web.ankiapp.com/#/import')

    # select Choose File
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[(@type='file') and (@accept='.csv,.zip')]"))
    )
    element.send_keys(audio_dir + zip_)

    # Click Begin Import
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Begin Import')]"))
    )
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    # special click, element.click() doesn't work on this page
    driver.execute_script("arguments[0].click();",element)

    # click "OK" after success message comes up
    element = WebDriverWait(driver, 600).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'OK')]"))
    )
    element.click()


# In[8]:
# The following sets of code are used to identify the name of the flash card deck
# AnkiApp just saves the imported deck as CSV {Date}

search_words = ['verslaggeefstertje', 'ik', 'hij', 'met', 'waarschijnlijk']

def search_word_in_chapter(search_words, file_list):
    for _ in file_list:
        temp = pd.read_table(_, header=None)
        for s_word in search_words:
            if s_word in temp[0].values:
                print(_, '\t', s_word)

search_word_in_chapter(search_words, file_list)



# In[9]:
file_list = os.listdir(Vocabulary_dir)
file_list = [x for x in file_list if '.txt' in x]
file_list.sort(key=natural_keys)

len_list = []
for _ in file_list:
    temp = pd.read_table(_, header=None)
    len_list.append(len(temp))

df = pd.DataFrame(file_list)
df['Num_Words'] = len_list

print(df.sort_values(by=['Num_Words']))


# In[10]:
'''
    Do something slightly different, let's sort the words in terms of how frequently they appear in the text
    Load and join the text from all the chapters
    remove punctuation
    split individual words into a list
    Use Counter from collections to do a frequency count

    This seems to make a lot of sense from a value perspective
    If we assume that the words that appear most frequently are the most valuable (or most useful) then it makes sense to prioritize learning those words. In addition, from a learning perspective this also makes sense - we are probably more likely to actually learn the words that appear more often, as opposed to the words that only appear a few times
'''

input_path = '/Users/nicholasbrady/Documents/Post-Doc/Dutch/Books/'
book_ = 'Harry Potter en de Vuurbeker by Rowling, Joanne Kathleen.epub'

chapters = epub2thtml(os.path.join(input_path, book_) )

# In[12]:
# Join all chapter text into one string =)
full_text = []
for chapter in chapters:
    chapter_text = chap2text(chapter)

    chapter_text = re.sub(r'[^\w\s]', '', chapter_text)
    # get list of individual words
    words = chapter_text.split()

    if not(words):
        continue
    if words[0] != 'Hoofdstuk':
        continue

    full_text += words

# In[13]:
_ = Counter(full_text).most_common()

print(len(_))

for element in _:
    (word, count) = element

    capitalized = [l.isupper() for l in word]
    capitalized = any(capitalized)

    digit = [l.isdigit() for l in word]
    digit = any(digit)

    if (capitalized or digit):
        _.remove(element)

print(len(_))



# In[40]:
'''
    Advanced features that can be incorporated in the future
'''
# In[41]:
'''
    Determine the part of speech for each word in a sentence
    https://github.com/evanmiltenburg/Dutch-tagger
    https://spacy.io/
'''

nlp = spacy.load("nl_core_news_sm")

dutch_sentence = 'Alle vogels zijn nesten begonnen, behalve ik en jij.'
doc = nlp(dutch_sentence)
for token in doc:
    print(token.text, token.pos_, token.dep_)

# In[42]:
'''
    Determine the part of speech for each word in a chapter
'''
doc = nlp(chapter_text)
for o, token in enumerate(doc):
    if o < 30:
        print(token.text, token.pos_, token.dep_)
