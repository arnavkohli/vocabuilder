<h1 align="center"> Vocabuilder </h1>

<p align="center">
  <img src="https://github.com/arnavkohli/vocabuilder/actions/workflows/vocabuilder-ci.yml/badge.svg" />
  <img src="https://visitor-badge.laobi.icu/badge?page_id=vocabuilder" />
</p>

<p align="center">
    Script to send random words via email from the Magoosh GRE preperation list!
 </p>
 
## Setup 

### Clone this Repository
```
git clone https://github.com/arnavkohli/vocabuilder
```

### Setup ETL
This step is required to extract the words from the raw list and ingest them into MongoDB.

#### Inside _etl_run.py_ update variables as per your setup
```
MONGO_CONN_URL = ""                               # MongoDB Connection URL
DATABASE = "vocabuilder"                          # Database name
COLLECTION = "magoosh_words"                      # Collection name
FP_TO_RAW_DATA = "./static/magoosh_raw_list.txt"  # File path to raw list
```

### Run the ETL
```
python etl_run.py
```

### Get random words using email!

#### Inside _send_random_word_via_email.py_ update variables as per your setup
```
MONGO_CONN_URL = ""                           # MongoDB Connection URL
DATABASE = "vocabuilder"                      # Database name
NEW_WORDS_COLLECTION = "magoosh_words"        # New words collection name
OLD_WORDS_COLLECTION = "old_magoosh_words"    # Old words collection name
SENDER_ADDR = "example@gmail.com"             # Email address of sender
SENDER_PWD = "abcd1234"                       # Password of sender
EMAILS = ["test@gmail.com"]                   # List of emails to send the word to
FP_TO_EMAIL_TEMPLATE = "./static/email.html"  # Path to email template
```

### Run the script
```
python send_random_word_via_email.py
```

![sample](https://github.com/arnavkohli/vocabuilder/blob/develop/screenshot.png)