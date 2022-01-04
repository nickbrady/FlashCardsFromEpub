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

from collections import OrderedDict

# In[1]:
# Webpage navigation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

audio_folder = "/Users/nicholasbrady/Documents/Post-Doc/Dutch/Books/Vocabulary/Audio/"# + Lesson_Name + "/"
try:
    os.makedirs(audio_folder)
except:
    pass
chromeOptions = webdriver.ChromeOptions()
prefs = {"download.default_directory" : audio_folder}
chromeOptions.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chromeOptions)
driver.set_page_load_timeout(10)
wait = WebDriverWait(driver, 10)



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
    2. Get text of each chapter in book
    3. split the text into words (split by whitespace)
    4. Filter word list to only get unique words
    5. Ignore capitalized words
    6. Check that word is "new" - i.e. not already included in previous chapters
    7. Make text file of new unique words
    8. Use selenium to retrieve english translations of words (google translate or DeepL)
    9. Make dataframe of Dutch, English word pairs
    10. Use selenium to retrieve media - audio of Dutch words
    11. Save audio in chapter specific subfolders
    12. Make .csv file with AnkiApp / AnkiMobile structure
    13. Check that all media files are included
    14. Make zip file of each chapter subfolder - includes .mp3's and .csv file (AnkiApp specific)
    15. Use selenium to upload these zip folders to AnkiApp website (https://web.ankiapp.com/#/import)
'''

# In[1]:
input_path = '/Users/nicholasbrady/Documents/Post-Doc/Dutch/Books/'
book_ = 'Harry Potter en de Vuurbeker by Rowling, Joanne Kathleen.epub'

chapters = epub2thtml(os.path.join(input_path, book_) )

# In[3]:
# open epub file
input_path = '/Users/nicholasbrady/Documents/Post-Doc/Dutch/Books/'
book_ = 'Harry Potter en de Vuurbeker by Rowling, Joanne Kathleen.epub'

chapters = epub2thtml(os.path.join(input_path, book_) )

Vocabulary_dir = '/Users/nicholasbrady/Documents/Post-Doc/Dutch/Books/Vocabulary/'

# get the text of each chapter and filter for new unique words
# new unique words are output to .txt file
ch_number = 0
unique_words = []
for chapter in chapters:
    len_list_old = len(unique_words)
    chapter_text = chap2text(chapter)

    # remove punctuation
    chapter_text = re.sub(r'[^\w\s]', '', chapter_text)
    words = chapter_text.split()

    # don't include table of contents, front / back material
    # filter just to get chapters
    if not(words):
        continue
    if words[0] != 'Hoofdstuk':
        continue

    # get unique words
    unique_words = list(OrderedDict.fromkeys(unique_words + words))

    '''Remove strings that contain digits [0-9]'''
    unique_words = [x for x in unique_words if not any(x1.isdigit() for x1 in x)]
    ''' Remove capitalized words '''
    unique_words = [x for x in unique_words if not any(x1.isupper() for x1 in x)]

    ''' Make .txt file of new words for each chapter '''
    ch_number += 1
    word_list = unique_words[len_list_old:]
    textfile = open(Vocabulary_dir + "HP_4_Hoofdstuk_{}.txt".format(ch_number), "w")
    for word in word_list:
        textfile.write(word + "\n")
    textfile.close()

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
    except:
        print('Could not locate element')

    translated_text = element.get_attribute('data-text')

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

# In[11]:
'''Retrieve English Translations of Dutch Words'''
# get a list of the files
# files contain the chapter specific new unique words
file_list = []
for file in os.listdir(Vocabulary_dir):
    if file.startswith("HP_4_"):
        if "_NL_ENG.txt" not in file:
            file_list.append(file)

file_list.sort(key=natural_keys)

# In[12]:

# retrieve English translations of Dutch words (up to 5000 characters) using 'translate_dutch_words'
# files that contain more than 5000 characters are systematically split into segments and then concatenated
for file in file_list:
    filename, extension = os.path.splitext(Vocabulary_dir + file)
    _file_PAIR = filename + "_NL_ENG.txt"

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
    df = pd.read_table(Vocabulary_dir + file, header=None)
    df.columns = ['Nederlands']
    df_ = pd.read_table(StringIO(eng_translation), header=None)
    df['English'] = df_

    # print dataframe to CSV file
    df.to_csv(_file_PAIR, index=False, header=False, encoding='utf-8-sig')

# In[13]:
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
    audio_files = os.listdir(audio_folder) + os.listdir(audio_folder + chapter_name)
    audio_files = [x for x in audio_files if '.mp3' in x]
    audio_files = [os.path.splitext(mp3)[0] for mp3 in audio_files]
    audio_files.sort(key=natural_keys)

    words = [x for x in words if x not in audio_files]
    words.sort(key=natural_keys)

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
            shutil.move(audio_folder + '{}.mp3'.format(word), audio_folder + chapter_name)
        except:
            pass


    df = pd.read_csv(Vocabulary_dir + 'HP_4_Hoofdstuk_1_NL_ENG.txt', header=None)
    df.columns = ['Nederlands', 'English']

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

    df.to_csv(audio_folder + chapter_name + '/{}_NL_ENG_MP3.csv'.format(chapter_name), index=False, header=False)

# In[5]:
'''
Use selenium web navigation to retrieve Google Translate translations of Dutch words

Translations can be done
    1) 1 word at a time
    2) Multiple words at a time (<5000 characters)
    3) Document upload - if we do this many times, it gets flagged and we have to complete "Not a Robot"
'''

for o, _file_ in enumerate(file_list):
    if o < 23:
        continue

    filename, extension = os.path.splitext(Vocabulary_dir + _file_)
    _file_ENG = filename + "_ENG.txt"
    _file_PAIR = filename + "_NL_ENG.txt"
    # Go to Google translate website
    driver.get("https://translate.google.com/")
    # Select the Document button
    element = driver.find_element(By.XPATH, "//button[@aria-label='Document translation']")
    element.click()
    # find the "Browse Your Computer" button
    element = driver.find_element(By.XPATH, "//input[@id='i37']")
    # upload the desired document
    element.send_keys(Vocabulary_dir + _file_)
    # select the "Translate" button
    element = driver.find_element(By.XPATH, "//button[@jsname='vSSGHe']")
    element.click()
    # retrieve the translated text
    translated_text = driver.find_element(By.TAG_NAME, 'body').text
    # write translated text to file
    textfile = open(_file_ENG, "w")
    textfile.write(translated_text)
    textfile.close()

    # Use pandas to construct ordered pairs of Dutch words, English words
    words = pd.read_table(Vocabulary_dir + _file_, header=None)
    _df = pd.read_table(_file_ENG, header=None)
    words.columns = ['Nederlands']
    words['English'] = _df
    # write words as comma-separated-values
    words.to_csv(_file_PAIR, index=False, header=False)

    # remove _ENG file
    os.remove(_file_ENG)



# In[13]:
'''
    Retrieve .mp3 sound of Dutch words
'''

# audio_files = os.listdir(audio_folder)
# audio_files.sort(key=natural_keys)
# audio_files.remove('.DS_Store')
# audio_files = [os.path.splitext(mp3)[0] for mp3 in audio_files]

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
    audio_files = os.listdir(audio_folder) + os.listdir(audio_folder + chapter_name)
    audio_files = [x for x in audio_files if '.mp3' in x]
    audio_files = [os.path.splitext(mp3)[0] for mp3 in audio_files]
    audio_files.sort(key=natural_keys)

    words = [x for x in words if x not in audio_files]
    words.sort(key=natural_keys)

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
            shutil.move(audio_folder + '{}.mp3'.format(word), audio_folder + chapter_name)
        except:
            pass


    df = pd.read_csv(Vocabulary_dir + 'HP_4_Hoofdstuk_1_NL_ENG.txt', header=None)
    df.columns = ['Nederlands', 'English']

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

    df.to_csv(audio_folder + chapter_name + '/{}_NL_ENG_MP3.csv'.format(chapter_name), index=False, header=False)

# In[5]:
# Data frame structure AnkiMobile - comma-separated-values need be saved as .txt file
# Front[sound:Front.mp3], Back
# df['Nederlands'] = df['Nederlands'] + df['mp3']
# df.to_csv(Vocabulary_dir + 'HP_4_Hoofdstuk_1_NL_ENG_MP3.txt', columns=['Nederlands', 'English'], index=False, header=False)

# Data frame structure AnkiApp - need to save as .csv file
# Front, Back, Tags, Image(front), Image(back), Sound(front), Sound(back)
df['Tags'] = ''
df['Image(front)'] = ''
df['Image(back)'] = ''
df['mp3(back)'] = ''

cols = ['Nederlands', 'English', 'Tags', 'Image(front)', 'Image(back)', 'mp3', 'mp3(back)']
df = df[cols]

df.to_csv(Vocabulary_dir + 'HP_4_Hoofdstuk_1_NL_ENG_MP3.csv', index=False, header=False)

# In[6]:
# Make subfolder for each chapter in audio_folder
for chapter in file_list:
    filename, extension = os.path.splitext(chapter)
    try:
        os.makedirs(audio_folder + filename)
    except:
        pass

# Move existing mp3's to their correct folder
audio_files = os.listdir(audio_folder)
audio_files = [x for x in audio_files if '.mp3' in x]
audio_files.sort(key=natural_keys)

file_ = open(Vocabulary_dir + file_list[37-1], 'r')
file_text = file_.read()

words = file_text.split('\n')
# remove empty words
words = list(filter(None, words))

for word in words:
    shutil.move(audio_folder + word + '.mp3', audio_folder + 'HP_4_Hoofdstuk_37/')

# In[4]:
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

# In[5]:
'''
    Determine the part of speech for each word in a chapter
'''
doc = nlp(chapter_text)
for o, token in enumerate(doc):
    if o < 30:
        print(token.text, token.pos_, token.dep_)
