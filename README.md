# gmail-spam-detector
clean up Gmail inbox using machine learning model safely. 

# Gmail Spam Detector App

This is a Python-based application that connects to your Gmail account using the Gmail API and reads your latest emails. You can choose days, such as older than1 month/older than 1 year etc. It is intended to serve as a foundation for building a spam detection system using machine learning or rule-based filtering.

##What it will do?

- Connects securely to your Gmail via OAuth 2.0
- Fetches and displays recent email senders and subjects
- Easily extendable for spam detection or email classification

##Requirements

- Python 3.7+
- Google Cloud project with Gmail API enabled
- OAuth 2.0 credentials (`credentials.json`)


##Usage:
-Download your credentials.json file from Google Cloud Console.

-Place it in the project directory.

-Run the script: 
python gmail_script.py

-A browser window will open to authenticate your Gmail account.

-The script will then display the latest emails (sender and subject).

-Make sure to add the following to your .gitignore:
1.credentials.json
2.token.json


-This app uses read-write access to Gmail/.
#To build a full spam detection system, you can add NLP or machine learning models. In this app I have used, SMS Spam Collection using Naïve Bayes, a well-known and fast baseline for text-based spam detection.

-About the used model:
#This model is very strong at catching spam:
#High accuracy means most messages are classified correctly.
#High spam precision (≥ 75%) ensures when it flags something as spam, it usually is.
#High non-spam precision (> 95%) means it rarely mislabels legitimate messages.

-Limitations
#Trained on SMS data, not email, so certain email-specific spam patterns may slip through.

#Inputs with HTML, links, or modern obfuscation might reduce confidence.

#Extremely cautious deletion (only at 100% spam confidence) helps avoid false positives.
#Emails and Text sms spam are different so lot spam email can slip out-at the same time its safe.


-License
#MIT License — feel free to use, modify, and distribute with attribution.