# Flash Cards From Epub
Create native language flashcards from an epub document.

Flashcards are word by word translations and include audio media.\
Word by word translations are taken from Google Translate (DeepL is another good option).\
mp3 files of the words are created using soundoftext.com

Flashcards are formatted specifically for AnkiApp (https://www.ankiapp.com/)

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
