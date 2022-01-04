import os
import re
import shutil

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

Vocabulary_dir = '/Users/nicholasbrady/Documents/Post-Doc/Dutch/Books/Vocabulary/'
audio_folder = "/Users/nicholasbrady/Documents/Post-Doc/Dutch/Books/Vocabulary/Audio/"

file_list = []
for file in os.listdir(Vocabulary_dir):
    if file.startswith("HP_4_"):
        if "_NL_ENG.txt" not in file:
            file_list.append(file)

file_list.sort(key=natural_keys)

for chapter in file_list:

    file_ = open(Vocabulary_dir + chapter, 'r')
    file_text = file_.read()
    word_list = file_text.split('\n')
    word_list.sort(key=natural_keys)
    # remove empty words
    word_list = list(filter(None, word_list))

    filename = os.path.splitext(chapter)[0]

    csv_file = False


    mp3_list = os.listdir(audio_folder + filename)
    # check that chapter .csv file is in audio subfolder
    if '{}_NL_ENG_MP3.csv'.format(filename) in mp3_list:
        csv_file = True

    mp3_list = [x for x in mp3_list if '.mp3' in x]
    mp3_list = [os.path.splitext(x)[0] for x in mp3_list]
    mp3_list.sort(key=natural_keys)

    if word_list == mp3_list:
        print('No missing mp3\'s in {}'.format(filename))
        if csv_file:
            print(os.getcwd())
            shutil.make_archive(audio_folder + filename, 'zip', audio_folder + filename)
    else:
        missing_words = [x for x in word_list if x not in mp3_list]
        # print(missing_words)
        # re-run the get mp3 function
