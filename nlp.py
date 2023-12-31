# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 15:05:07 2023

@author: Eric
"""

"""
The new_comment data is retrieved from 'Youtube05-Shakira.csv' file,
which is for group project use. 
I have no intention of discriminating against others 
or even hating others.

Please pip install sklearn, nltk in the terminal at first

"""

import pandas as pd
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import matplotlib.pyplot as plt
import seaborn as sns

nltk.download('punkt')
nltk.download('stopwords')

# Load the data into a pandas DataFrame
def load_data(file_path):
    try:
        # Try different encodings to handle diverse datasets
        encodings = ['utf-8', 'ISO-8859-1']
        for encoding in encodings:
            with open(file_path, 'r', encoding=encoding, errors='replace') as file:
                data = pd.read_csv(file)
                if 'CLASS' in data.columns and 'CONTENT' in data.columns:
                    return data
    except Exception as e:
        print(f"Error loading data: {e}")
    return None

def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()
    words = word_tokenize(text)
    words = [stemmer.stem(word) for word in words if word.isalpha() and word.lower() not in stop_words]
    return ' '.join(words)

def extract_features(comment):
    # Example features, add more as needed
    num_urls = len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', comment))
    comment_length = len(comment)
    capital_letter_count = sum(1 for char in comment if char.isupper())
    
    # Sentiment analysis
    sid = SentimentIntensityAnalyzer()
    sentiment_score = sid.polarity_scores(comment)['compound']
    
    return [num_urls, comment_length, capital_letter_count, sentiment_score]

def is_spam_comment(comment):
    # Custom function to check for specific patterns or keywords indicative of spam
    spam_keywords = ['secret video', 'celeb site', 'free iPhone', 'special offer']
    return any(keyword in comment.lower() for keyword in spam_keywords)

def plot_confusion_matrix(conf_matrix, title):
    plt.figure(figsize=(6, 4))
    sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues", cbar=False)
    plt.title(title)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.show()

def explore_data(data):
    # Explore the distribution of spam and non-spam comments
    sns.countplot(x='CLASS', data=data)
    plt.title('Distribution of Spam and Non-Spam Comments')
    plt.show()

def main():
    path = "C:/Users/Eric/OneDrive/Desktop/nlp/"
    filename = 'Youtube05-Shakira.csv'
    fullpath = os.path.join(path, filename)

    # Load data with dynamic encoding
    data = load_data(fullpath)

    if data is not None:
        # Data exploration
        explore_data(data)
        print(data.head())
        print(data.info())

        comments = data['CONTENT']
        labels = data['CLASS']

        # Text preprocessing
        comments = comments.apply(preprocess_text)

        # Vectorize the text data using TF-IDF Vectorizer
        tfidf_vectorizer = TfidfVectorizer()
        X_tfidf = tfidf_vectorizer.fit_transform(comments)

        # Present highlights of the output (initial features)
        print("Initial Features - Shape:", X_tfidf.shape)
        print("Initial Features - First Few Rows:")
        print(X_tfidf[:5, :])

        # Shuffle the dataset
        data_shuffled = data.sample(frac=1, random_state=42)

        # Split the dataset into 75% training and 25% testing
        train_data, test_data = train_test_split(data_shuffled, test_size=0.25, random_state=42)
        train_comments, test_comments = train_data['CONTENT'], test_data['CONTENT']
        train_labels, test_labels = train_data['CLASS'], test_data['CLASS']

        # Fit the training data into a Naive Bayes classifier
        classifier_nb = MultinomialNB()
        classifier_nb.fit(X_tfidf, labels)

        # Cross-validate the Naive Bayes model on the training data using 5-fold
        cross_val_scores_nb = cross_val_score(classifier_nb, X_tfidf, labels, cv=5, scoring='accuracy')
        print("Naive Bayes Cross-Validation Mean Accuracy:", cross_val_scores_nb.mean())

        # Fit the training data into a RandomForest classifier
        classifier_rf = RandomForestClassifier(n_estimators=100, random_state=42)
        classifier_rf.fit(X_tfidf, labels)

        # Cross-validate the RandomForest model on the training data using 5-fold
        cross_val_scores_rf = cross_val_score(classifier_rf, X_tfidf, labels, cv=5, scoring='accuracy')
        print("RandomForest Cross-Validation Mean Accuracy:", cross_val_scores_rf.mean())

        # Test the Naive Bayes model on the test data
        test_comments_preprocessed = test_comments.apply(preprocess_text)
        X_test_tfidf = tfidf_vectorizer.transform(test_comments_preprocessed)

        predictions_nb = classifier_nb.predict(X_test_tfidf)

        # Confusion matrix and evaluation metrics for the Naive Bayes model
        conf_matrix_nb = confusion_matrix(test_labels, predictions_nb)
        accuracy_nb = accuracy_score(test_labels, predictions_nb)
        precision_nb = precision_score(test_labels, predictions_nb)
        recall_nb = recall_score(test_labels, predictions_nb)
        f1_nb = f1_score(test_labels, predictions_nb)

        print("Naive Bayes Confusion Matrix:")
        print(conf_matrix_nb)
        print("Naive Bayes Accuracy:", accuracy_nb)
        print("Naive Bayes Precision:", precision_nb)
        print("Naive Bayes Recall:", recall_nb)
        print("Naive Bayes F1 Score:", f1_nb)

        # Plot confusion matrix for Naive Bayes
        plot_confusion_matrix(conf_matrix_nb, "Naive Bayes Confusion Matrix")

        # Test the RandomForest model on the test data
        predictions_rf = classifier_rf.predict(X_test_tfidf)

        # Confusion matrix and evaluation metrics for the RandomForest model
        conf_matrix_rf = confusion_matrix(test_labels, predictions_rf)
        accuracy_rf = accuracy_score(test_labels, predictions_rf)
        precision_rf = precision_score(test_labels, predictions_rf)
        recall_rf = recall_score(test_labels, predictions_rf)
        f1_rf = f1_score(test_labels, predictions_rf)

        print("RandomForest Confusion Matrix:")
        print(conf_matrix_rf)
        print("RandomForest Accuracy:", accuracy_rf)
        print("RandomForest Precision:", precision_rf)
        print("RandomForest Recall:", recall_rf)
        print("RandomForest F1 Score:", f1_rf)

        # Plot confusion matrix for RandomForest
        plot_confusion_matrix(conf_matrix_rf, "RandomForest Confusion Matrix")

        # Generate new comments for classification
        new_comments = [
        "I believe that soccer promotes terrorism.",
        "win money at hopme",
        "New way to make money easily",
        "You acquire the bonus as income",
        "download some other free apps and you get money",
        "You can make money online and start working from home today",
        "Work from the Comfort of your Home",
        "I Found a Way to Make Money Online",
        "Your a fucking bitch. ",
        "this song is racist",
        "Perhaps you have seen the newest Miley Cyrus SECRET video ?   She&#39;s sucking an old man&#39;s cock ,  If you wish to see her , check out the celebrity website beneath",
        "Haha , Miley Cyrus has done it once again  Today someone leeched a porno video with her on a celeb site   I believe the website link is : miley-celeb-news.co.uk in case you want to view it.... ",
        "I really can&#39;t comprehend Miley Cyrus , she actually is a high profile and she tapes herself banging Today a video was leeched with her sucking and fucking The video has been posted at the celebrity website under :  miley-celeb-news.co.uk ",
        "WAYS TO MAKE MONEY 50k Per Month Search google Now &gt;&gt; 9nl.me/make-money-without-investment-1",
        "WOW muslims are really egoistic..... 23% of the World population and not in this video or donating 1 dollar to the poor ones in Africa :( shame on those terrorist muslims",
        "wanna earn money online without investment.....just visit this link",
        "Earn money for being online with 0 efforts!",
        "O peoples of the earth, I have seen how you perform every form of evil at your leisure! You cease not from reveling in that which I hate! Behold, you murder the innocent day and night and plot evil against your neighbor! You stand up for the rights of those who commit abomination and clap your hands as wickedness is celebrated openly in the streets!... O MOST PERVERSE AND ABOMINABLE GENERATION, SHALL I NOT REPAY?!  Hear the Word of The Lord - TrumpetCallOfGodOnline.  co m",
        "Recommend:  Apple iPad 4th Gen 32GB Unlocked Wi-Fi+4G 9.7in White Price:$390  Apple iPhone 5 (Latest Model) - 32GB - Black Price:$385  Samsung Galaxy S4 S IV 4 with 16GB New White Price:$360  Sony 60-inch 3D LED HDTV Price:$510  All-in-One PCs: Apple MacBook Pro: Apple MacBook Air Price:$320  Camera :Nikon D90 SLR Camera /18-55mm /55-200mm 32GB  Price:$390   Ultrabooks: SONY VAIO Pro 13 Intel Core i5 4GB 128GB Price:$515  +++++++++++++++    Purchase online Website is:  Taaee.com",
        "Message :   GTA V  $20  FIFA 14 $15  PS4  $200  Galaxy S4 mini $250  Ipad 4   $200  visit the site hh.nl",
        "Meet The Richest Online Marketer  NOW CLICK : bit.ly/make-money-without-adroid",
        "Hey, I am doing the Forty Hour famine so I&#39;ll be giving up on food and social working for 40 hours. I&#39;m doing this to raise money for African people who can&#39;t experience the luxuries that we can. So can you donate to give them a chance?  Any amount would do :)  Click on the link and donate h t t p : / / 4 0 h f . c o m . a u / A n t h o n y L a m Thanks :)"
        ]

        # Preprocess the new comments
        new_comments_preprocessed = [preprocess_text(comment) for comment in new_comments]

        # Vectorize and transform the new comments using the existing TF-IDF Vectorizer
        X_new_tfidf = tfidf_vectorizer.transform(new_comments_preprocessed)

        # Predict the class of the new comments using Naive Bayes
        new_predictions_nb = classifier_nb.predict(X_new_tfidf)

        # Predict the class of the new comments using RandomForest
        new_predictions_rf = classifier_rf.predict(X_new_tfidf)

        # Display the results for the new comments using Naive Bayes
        print("Results for Naive Bayes:")
        for comment, preprocessed_comment, prediction in zip(new_comments, new_comments_preprocessed, new_predictions_nb):
            print(f"Raw Comment: {comment}")
            print(f"Preprocessed Comment: {preprocessed_comment}")
            print(f"Prediction: {'Spam' if prediction == 1 else 'Non-Spam'}\n")

        # Display the results for the new comments using RandomForest
        print("Results for RandomForest:")
        for comment, preprocessed_comment, prediction in zip(new_comments, new_comments_preprocessed, new_predictions_rf):
            print(f"Raw Comment: {comment}")
            print(f"Preprocessed Comment: {preprocessed_comment}")
            print(f"Prediction: {'Spam' if prediction == 1 else 'Non-Spam'}\n")

if __name__ == "__main__":
    main()
    
