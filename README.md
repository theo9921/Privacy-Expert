# Privacy Expert

## Inspiration
Recent events such as the Cambridge Analytica scandal have prompted a heightened focus on personal data and its use by tech companies. However, most users are still faced with daunting service agreements designed to discourage in-depth reviews of the rights they are forfeiting. Legislation such as GDPR is a step in the right direction, but our team felt that technology should also be leveraged to empower users and take back control of our digital lives.

## What it does
When faced with an extensive terms and agreements page, users can simply paste the URL into our custom website. Using Microsoft Cognitive Services, the document is analysed and made available for users to query via the Privacy Expert Alexa skill. Example questions include:

* Find the terms and conditions
* Tell me about subscriptions
* Give me details about content availability

## How we built it
The custom website was built using Flask and accepts a URL input which then is sent to a Python backend script. The script makes an API call to QnA Maker on Microsoft Cognitive Services for extracting and generating Q&A pairs from the target URL. This result is then downloaded and processed using a DeepAI text summarisation API, before being uploaded back to a Cognitive Services knowledge base.

The Alexa skill uses an AWS Lambda function which processes the QuestionIntent and identifies the Q&A pair most relevant to the query.

## Instructions to run
To run the project first clone the github repository and then run the `application.py` file. First navigate to the directory you want to create the project and run

`git clone https://github.com/theo9921/privacy-expert.git && python ./privacy-expert/application.py` 

This will spawn the website on http://localhost:5000/

