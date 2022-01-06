# FlashCardsFromEpub
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
5. split the text into words (split by whitespace)
6. Filter word list to only get unique words
7. Ignore capitalized words
8. Check that word is "new" - i.e. not already included in previous chapters
9. Make text file of new unique words
10. Use selenium to retrieve english translations of words (google translate or DeepL)
11. Make dataframe of Dutch, English word pairs
12. Use selenium to retrieve media - audio of Dutch words
13. Save audio in chapter specific subfolders
14. Make .csv file with AnkiApp / AnkiMobile structure
15. Check that all media files are included
16. Make zip file of each chapter subfolder - includes .mp3's and .csv file (AnkiApp specific)
17. Use selenium to upload these zip folders to AnkiApp website (https://web.ankiapp.com/#/import)
