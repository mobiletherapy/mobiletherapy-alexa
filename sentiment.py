# -*- coding: utf-8 -*-

import requests
import json

accessKey = '2f95a0b225b141c290a3a1d4f2f7e87a'
uri = 'northeurope.api.cognitive.microsoft.com'
path = '/text/analytics/v2.0/sentiment'

def GetSentiment (text):
    "Gets the sentiments for a set of documents and returns the information."

    filled_in_documents = { 'documents': [{ 'id': '0', 'language': 'en', 'text': text }]}

    body = json.dumps (filled_in_documents)
    headers = {'Ocp-Apim-Subscription-Key': accessKey}
    return print("%.2f" % json.loads(requests.post("https://" + uri + path, data=body, headers=headers).content)['documents'][0]['score'] / 100)

print('Please wait a moment for the results to appear.\n')
sentiment = GetSentiment("terrible")
print(json.dumps(sentiment, indent=4))
