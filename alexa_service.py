import http.client, urllib.parse, json, time
import ast

def download_kb(kb_information):

    # Replace this with a valid subscription key.
    subscriptionKey = kb_information['subscriptionKey'] 

    # Replace this with a valid knowledge base ID.
    kb = kb_information['kbId']

    # Replace this with "test" or "prod".
    env = 'test'

    host = "westus.api.cognitive.microsoft.com"
    service = '/qnamaker/v4.0'
    method = '/knowledgebases/{0}/{1}/qna/'.format(kb, env)

    def get_qna(path):
        print ('Calling ' + host + path + '.')
        headers = {
            'Ocp-Apim-Subscription-Key': subscriptionKey,
        }
        conn = http.client.HTTPSConnection(host)
        conn.request("GET", path, '', headers)
        response = conn.getresponse ()
        return response.read ()

    path = service + method
    result = get_qna(path)
    return result

def send_req(req, kb_information):
    # Sends the processed qna objects to the new knowledge base
        
    subscriptionKey = kb_information['subscriptionKey'] 
    kb = kb_information['kbId']

    host = "westus.api.cognitive.microsoft.com"
    service = '/qnamaker/v4.0'
    method = '/knowledgebases/'


    def update_kb (path, content):
        print ('Calling ' + host + path + '.')
        headers = {
            'Ocp-Apim-Subscription-Key': subscriptionKey,
            'Content-Type': 'application/json',
            'Content-Length': len (content)
        }
        conn = http.client.HTTPSConnection(host)
        conn.request ("PATCH", path, content, headers)
        response = conn.getresponse()
        return response.getheader('Location'), response.read ()

    def check_status (path):
        print ('Calling ' + host + path + '.')
        headers = {'Ocp-Apim-Subscription-Key': subscriptionKey}
        conn = http.client.HTTPSConnection(host)
        conn.request ("GET", path, None, headers)
        response = conn.getresponse ()
        # If the operation is not finished, /operations returns an HTTP header named Retry-After
        # that contains the number of seconds to wait before we query the operation again.
        return response.getheader('Retry-After'), response.read ()


    path = service + method + kb
    # Convert the request to a string.
    content = json.dumps(req)
    operation, result = update_kb(path, content)
    print (pretty_print(result))

    done = False
    while False == done:
        path = service + operation
        wait, status = check_status (path)
        print (pretty_print(status))

    # Convert the JSON response into an object and get the value of the operationState field.
        state = json.loads(status)['operationState']
    # If the operation isn't finished, wait and query again.
        if state == 'Running' or state == 'NotStarted':
            print ('Waiting ' + wait + ' seconds...')
            time.sleep (int(wait))
        else:
            done = True

def pretty_print(content):
    # Note: We convert content to and from an object so we can pretty-print it.
    return json.dumps(json.loads(content), indent=4)

import requests
import re

def text_summarise(text):
    r = requests.post("https://api.deepai.org/api/summarization", 
        data={'text': text,},
        headers={'api-key': '57bc518b-5bfa-4424-9716-37fd3dec890c'})
    return r

def clean_basic(text):
    replaced = text.replace('\n', ' ').replace('*', ' ')
    return re.sub(' +', ' ', replaced)

def clean_text(text):
    text = clean_basic(text)
    # Further cleaning if necessary
    return text

def process_dict(kb_dict):
    cleaned_ids = []
    for qna_object in kb_dict['qnaDocuments']:
        question, answer = qna_object['questions'][0], qna_object['answer']
        
        # Clean question and answer
        cleaned_question = clean_basic(question)
        cleaned_answer = clean_text(answer)

        qna_object['questions'][0] = cleaned_question
        
        # Text summarization
        if len(cleaned_answer) < 300:
            summarized_answer = text_summarise(cleaned_answer).json()
        
        try:
            if summarized_answer['output'] == '\n':
                qna_object['answer'] = cleaned_answer
            else:
                qna_object['answer'] = summarized_answer['output']
        except:
            qna_object['answer'] = cleaned_answer

        cleaned_ids.append(qna_object['id'])
        
    return cleaned_ids

def kb_dict_to_req(kb_dict):
    req = {'add' : {'qnaList' : []}}
    for qna_object in kb_dict['qnaDocuments']:
        del qna_object['alternateQuestionClusters']
        del qna_object['changeStatus']
        del qna_object['kbId']
        
        req['add']['qnaList'].append(qna_object)
    return req

def ids_to_delete_req(ids):
    return {'delete': {'ids': ids}}

def add_url_to_kb(url_string, kb_information):
    req = {'add' : {'urls' : [url_string]}}
    send_req(req, kb_information)
    
def add_url_to_kb_v2(url_string, kb_information):
    req = {'urls' : [url_string]}
    replacing_request_kb(req, kb_information)
    
def replacing_request_kb(req, kb_information):
    subscriptionKey = kb_information['subscriptionKey'] 
    kb = kb_information['kbId']

    host = 'westus.api.cognitive.microsoft.com'
    service = '/qnamaker/v4.0'
    method = '/knowledgebases/'
    
    def replace_kb(path, content):
        print ('Calling ' + host + path + '.')
        headers = {
            'Ocp-Apim-Subscription-Key': subscriptionKey,
            'Content-Type': 'application/json',
            'Content-Length': len (content)
        }
        conn = http.client.HTTPSConnection(host)
        conn.request ("PUT", path, content, headers)
        response = conn.getresponse ()

        if response.status == 204:
            return json.dumps({'result' : 'Success.'})
        else:
            return response.read ()
    
    path = service + method + kb
    content = json.dumps(req)
    result = replace_kb (path, content)
    print (pretty_print(result))
    
def reset_kb(kb_information):
    empty_req = {
      'qnaList': [
        {
          'id': 13392,
          'answer': 'Empty Answer',
          'source': 'Empty Source',
          'questions': [
            'This is an empty question'
          ],
          'metadata': [{'name': 'category', 'value': 'api'}]
        }
      ]
    }
    replacing_request_kb(empty_req, kb_information)

def publish_kb(kb_information):
    subscriptionKey = kb_information['subscriptionKey'] 
    kb = kb_information['kbId']

    host = 'westus.api.cognitive.microsoft.com'
    service = '/qnamaker/v4.0'
    method = '/knowledgebases/'

    def publish_kb (path, content):
        print ('Calling ' + host + path + '.')
        headers = {
            'Ocp-Apim-Subscription-Key': subscriptionKey,
            'Content-Type': 'application/json',
            'Content-Length': len (content)
        }
        conn = http.client.HTTPSConnection(host)
        conn.request ("POST", path, content, headers)
        response = conn.getresponse ()

        if response.status == 204:
            return json.dumps({'result' : 'Success.'})
        else:
            return response.read ()

    path = service + method + kb
    result = publish_kb (path, '')
    print (pretty_print(result))

original_kb = {'subscriptionKey' : 'c4761c345d4649de8fe5cc1c1c494331',
               'kbId': '5f3b0508-8439-4a7c-ab0f-a8b0e59d9fd5'}
cleaned_kb = {'subscriptionKey' : 'c4761c345d4649de8fe5cc1c1c494331',
              'kbId': '6e80dd6f-807a-45ce-ab70-dd4a2cf0ea92'}


def alexa_service(url_string):
    # Erases the cleaned kb
    reset_kb(cleaned_kb)
    print('-' * 90)
    print("Resetting finished")

    # Sends url
    add_url_to_kb(url_string, original_kb)
    print('-' * 90)
    print("URL added")

    # Makes a download request
    result = download_kb(original_kb)
    print('-' * 90)
    print('Download Finished')

    # Convert 
    kb_dict = ast.literal_eval(result.decode('utf-8'))

    # Takes a kb_dict, cleans and summarizes answers, returns ids of cleaned qna_objects
    cleaned_ids = process_dict(kb_dict)
    print('-' * 90)
    print('Processing finished')

    # Create request
    req = kb_dict_to_req(kb_dict)

    # Send request to cleaned kb
    send_req(req, cleaned_kb)
    print('-' * 90)
    print("Cleaned kb updated")

    # Delete old questions
    req = ids_to_delete_req(cleaned_ids)

    # Send request to original kb
    send_req(req, original_kb)
    print('-' * 90)
    print("Original kb updated")
    
    # Publish the public (cleaned) kb
    publish_kb(cleaned_kb)
    print('-' * 90)
    print("PUBLISHED")