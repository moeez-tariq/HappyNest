import os
from dotenv import load_dotenv
from sentiment_analysis import is_political, analyze_sentiment

load_dotenv()

def test_sentiment_analysis():
    # Test cases
    test_cases = [
        "I love this beautiful day!",
        "The election results are disappointing.",
        "The new policy will affect many citizens.",
        "I'm feeling sad and lonely today.",
        "The stock market crashed today.",
        "My cat is so cute and fluffy!"
    ]

    print("Testing sentiment analysis:")
    for text in test_cases:
        sentiment = analyze_sentiment(text)
        political = is_political(text)
        print(f"Text: '{text}'")
        print(f"Sentiment: {sentiment}")
        print(f"Is political: {political}")
        print("---")

if __name__ == "__main__":
    test_sentiment_analysis()