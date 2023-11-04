#!pip install -r '/content/requirements_ex_venv.txt'
try:
    
    from tqdm.auto import tqdm
    from scipy.spatial.distance import cosine
    import tensorflow as tf
    #from torch.utils.data import TensorDataset
    #import torch
    import requests
    import difflib
    import mysql.connector as c
    import re
    import pandas as pd
    import json
    import logging

    from transformers import DistilBertTokenizer, TFDistilBertModel
    tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
    model = TFDistilBertModel.from_pretrained("distilbert-base-uncased", output_hidden_states=True)
    similarity_threshold = 0.85
    logging.basicConfig(filename='ChatBotLogs.log',level = logging.INFO,format='%(asctime)s,%(levelname)s,Functioname: (%(funcName)s), %(message)s')
    def get_contextual_embeddings(text):
        input_ids = tokenizer.encode(text, add_special_tokens=True)
        inputs = tf.constant([input_ids])
        outputs = model(inputs)
        hidden_states = outputs.last_hidden_state
        contextual_embeddings = tf.reduce_mean(hidden_states, axis=1).numpy()
        return contextual_embeddings

    con =c.connect(host="localhost", user="root", passwd="",database="chatbot_dmrc")
    cursor=con.cursor()
    #cursor.execute("SELECT 	Query as Question,Response as Answer FROM excel_import_chatbotqueries")
    #df= cursor.fetchall()
    #faq_dict = dict(df)
    #fetching complaint tables
    cursor.execute("SELECT 	Query as Question,Response as Answer FROM master_qr_cards")
    df = pd.DataFrame(cursor.fetchall(),  columns = ['Question', 'Answer'])
    df['question_embeddings']=df['Question'].apply(get_contextual_embeddings)
    #Fetching Station-Names from Databse
    cursor.execute("SELECT Station_Name,Station_Code FROM master_station")
    d= dict(cursor.fetchall())

    #to fetch generalized queries
    cursor.execute("SELECT 	Query as Question,Response as Answer FROM master_generalized_queries")
    df_gen = pd.DataFrame(cursor.fetchall(),  columns = ['Question', 'Answer'])  
    df_gen['question_embeddings']=df_gen['Question'].apply(get_contextual_embeddings)

    def find_most_similar_question(x,input_question):
        input_embeddings = get_contextual_embeddings(input_question)

        max_similarity = -1
        most_similar_question = None
        response = None
        newdf = df if x == 2 else df_gen
        for key,value in newdf.iterrows():
            #print(value['Question'])
            #question_embeddings = get_contextual_embeddings(question)
            similarity = 1 - cosine(input_embeddings.flatten(), value['question_embeddings'].flatten())
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_question = value['Question']
                response = value['Answer']
        return (most_similar_question, response  ,max_similarity)

    def find_closest_match(input_str, options):
        # print(options)
        closest_match = difflib.get_close_matches(
            input_str.title(), options, n=1, cutoff=0.8)
        #Check for nulls in closest match
        if closest_match.__len__()>0:
        # print(closest_match)
            indexOfDataFound = options.index(closest_match[0])
            # print("Index: ", indexOfDataFound)
            if indexOfDataFound is not None:
                return indexOfDataFound
            else:
                return None
    def Get_Answer_routeInfo(ques):
        logging.debug('Fetching Route')
        logging.info('Fetching Route')
        answer = ''
        url = "http://139.59.31.166:8000/api/v2/en/station_route/*source*/*destination*/least-distance/2023-07-12%2010:36:00.000000"
        
        BetweenStnsRegex = re.compile(r'between(.+)(?:and|to)(.+)')
        if(BetweenStnsRegex.search(ques.lower(),re.IGNORECASE)):
            match = BetweenStnsRegex.search(ques.lower(),re.IGNORECASE)
            fromStn = re.sub('\W*[?!@#$%^&*()_+":{}?><]+', ' ',match.group(1)).strip()
            toStn = re.sub('\W*[?!@#$%^&*()_+":{}?><]+', ' ',match.group(2)).strip() 
        else:
            fromStn = re.sub('\W*[?!@#$%^&*()_+":{}?><]+', ' ',ques.lower().split("from", 1)[1].split('to',1)[0]).strip()
            toStn = re.sub('\W*[?!@#$%^&*()_+":{}?><]+', ' ',ques.lower()[ques.lower().rfind('to')+2:].split('from')[0]).strip()

        if(fromStn == None):
            answer = "Please mention Source Station"
            return answer
        
        if(toStn== None):
            answer = "Please mention Destination Station"
            return answer
            
        fromStnIndex = find_closest_match(fromStn, list(
            map(lambda x: x.title(), list(d.keys()))))
        # print("From Index: ", fromStnIndex)
        toStnIndex = find_closest_match(toStn, list(
            map(lambda x: x.title(), list(d.keys()))))
        # print("To Index: ", toStnIndex,type(fromStnIndex), type(toStnIndex))
        
        if fromStnIndex is not None:
            fromStn = list(d.values())[fromStnIndex]
        else:
            answer += f"Could not find a matching station for '{fromStn}'"

        if toStnIndex is not None:
            toStn = list(d.values())[toStnIndex]
        else:
            answer +=f"Could not find a matching station for '{toStn}'"

        #added by akhilesh
        if fromStnIndex is not None and toStnIndex is not None:
            url = url.replace("*destination*", toStn)
            url = url.replace("*source*", fromStn)
            
            response = requests.get(url)
        
            if response.status_code == 200:
                data = json.loads(response.text)
                # pprint.pprint(data)

                stations = data['stations']
                # line = data['line']
                total_time = data['total_time']
                fare = data['fare']
                line = (data['route'][0]['line'])
                line_number = (data['route'][0]['line_no'])
                towards_station = (data['route'][0]['towards_station'])
            # print(f'To station is: ',toStn)
                answer+=f"No. of stations: {stations}, Total time: {total_time} Line: {line}, Line Number:{line_number}, Fare is:, {fare}"
                answer+=f"\nBoard at station: {data['route'][0]['start']}, Towards Station: {data['route'][0]['towards_station']}, in Platform : {data['route'][0]['platform_name']} "
                
                if int(len(data['route'])) > 1:
                    
                    outputStations=[]
                    #interchange_list_stationsname = "" 
                    for i in range(1, len(data['route'])):
                        #interchange_list_stationsname = data['route'][i]['start'] 
                        outputStations.append(data['route'][i]['start'])
                    output_interchange_info = "\nNo of Interchange stations are: " + \
                        str(len(data['route'])-1)+'\n'+'Namely:'
                    answer+=(output_interchange_info + ','.join([str(ele) for ele in outputStations]))
        logging.info('Route Fetch successfully')            
        return answer

    def menu():
        logging.info('Displaying Menu')
        dict_menu = "If query related to metro route or fare of journey, type: \"1\"\nIf query related to QR Tickets,SmartCards,Tokens etc type: \"2\" \nFor any other Generalized queries like parking, divyangjang etc or any complaints , type: \"3\" \nTo exit chatbot, type: \"4\"\n"
        return dict_menu  
                
    def Get_Answer(x,question):
            #logging.info("Fetching Answer from Dataset")
        '''if(x==2):
            faq_dict =df'''
        '''elif(x==3):   
            faq_dict = dict_parking_divyan
        elif(x==4):
            faq_dict = dict_smartcard
        elif(x==5):
            faq_dict = dict_misc
        elif(x==6):
            faq_dict = dict_compl   aint ''' 
        most_similar_question, response ,similarity_score = find_most_similar_question(x,question)
        answer = ""
        if most_similar_question is not None:
            if similarity_score < similarity_threshold:
                answer = "Sorry, I couldn't figure out what exactly you want."
            else:
                # Get the answer for the most similar question
                answer = response   
                
        else:
            answer = "Sorry, I couldn't find a similar question in the dataset." 
        #logging.info("Answers fetched successfully from Dataset")    
        return answer                    
    #answer = find_most_similar_question('Do QR tickets come with a seperate receipt?')
    #answer = Get_Answer(2,'Are there any additional papers or receipts provided along with a QR ticket?')
    #answer
    '''
    if __name__ == "__main__":
        ans =Get_Answer(2,'Are there any additional papers or receipts provided along with a QR ticket?')
        print(ans)
    '''
except Exception as e:
    logging.error(f"Something else went wrong: {e}")
finally:
    #con.close()
    pass
        