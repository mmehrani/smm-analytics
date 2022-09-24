# Description
This part of the total project is dedicated to compute brand personlity by Aaker measures.

## Usage
### Personality detection
Hopefully, this part can be started externally from the other parts. To do so, start <algorithm.py> file and rename the 'example_dataset.csv' to your own file name. Please note that it is necessary that your file should include a "text" column.

*Please note that it is necessary to download [checkpoint-17315-epoch-5 folder](https://uofi.box.com/s/0ekhjz7mrwz6u2lpxqaz3ti49wtaegjq) and put exactly at the same root, else it will not work.

### Translation
If your tweets also includes non-English texts, please first run <translator.py> file on your dataset. It will runs over all the rows and translate them to english language and create a new file by "_en" suffix.

