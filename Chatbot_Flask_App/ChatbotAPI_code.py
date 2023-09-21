try:
    #import pandas as pd
    #import numpy as np
    from tqdm.auto import tqdm
    from scipy.spatial.distance import cosine
    import tensorflow as tf
    #from torch.utils.data import TensorDataset
    #import torch
    import requests
    import json
    import difflib
    import mysql.connector as c
    import re
    import json
    import logging

    # from google.colab import files
    # upload= files.upload()
    #logging.basicConfig(filename='ChatBotLogs.log',level = logging.INFO,format='%(asctime)s,%(levelname)s,%(name)s,%(message)s')
    # # Load the DistilBERT tokenizer and model
    from transformers import DistilBertTokenizer, TFDistilBertModel
    tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
    model = TFDistilBertModel.from_pretrained("distilbert-base-uncased", output_hidden_states=True)
    similarity_threshold = 0.85
    #flag = True
    logging.basicConfig(filename='ChatBotLogs.log',level = logging.INFO,format='%(asctime)s,%(levelname)s,Functioname: (%(funcName)s), %(message)s')
    
    # from transformers import DistilBertTokenizer, TFDistilBertModel

    # Load the FAQ questions and answers from the Excel file
    #df = pd.read_excel("newchatbot1.xlsx")
    con =c.connect(host="localhost", user="root", passwd="",database="chatbot_dmrc")
    cursor=con.cursor()
    #cursor.execute("SELECT 	Query as Question,Response as Answer FROM excel_import_chatbotqueries")
    #df= cursor.fetchall()
    #faq_dict = dict(df)
    #fetching complaint tables
    cursor.execute("SELECT 	Query as Question,Response as Answer FROM master_complaint")
    dict_complaint = dict(cursor.fetchall())
    #fetching QR table
    cursor.execute("SELECT 	Query as Question,Response as Answer FROM master_qr")
    dict_qr = dict(cursor.fetchall())
    #fetching Parking nd divyanjan
    cursor.execute("SELECT 	Query as Question,Response as Answer FROM master_parking_divyangjan")
    dict_parking_divyan = dict(cursor.fetchall())
    #fetching smart card from backend
    cursor.execute("SELECT 	Query as Question,Response as Answer FROM master_smartcard_ncmc")
    dict_smartcard = dict(cursor.fetchall())
    #fetching Misc from backend
    cursor.execute("SELECT 	Query as Question,Response as Answer FROM master_misc")
    dict_misc = dict(cursor.fetchall())
    
    #Fetching Route-Query-Intants from database 
    cursor.execute("SELECT 	Query as Question,Response as Answer FROM master_route_fetch")
    dict_route_intants = dict(cursor.fetchall())
    
    #Fetching Station-Names from Databse
    cursor.execute("SELECT Station_Name,Station_Code FROM master_station")
    d= cursor.fetchall()
    d= dict(d)  

    #for index, row in df.iterrows():
    #    question = row["Question"]
    #    answer = row["Answer"]
    #    faq_dict[question] = answer

    def get_contextual_embeddings(text):
        input_ids = tokenizer.encode(text, add_special_tokens=True)
        inputs = tf.constant([input_ids])
        outputs = model(inputs)
        hidden_states = outputs.last_hidden_state
        contextual_embeddings = tf.reduce_mean(hidden_states, axis=1).numpy()
        return contextual_embeddings

    def find_most_similar_question(input_question, faq_dict):
        input_embeddings = get_contextual_embeddings(input_question)

        max_similarity = -1
        most_similar_question = None

        for question in faq_dict:
            question_embeddings = get_contextual_embeddings(question)

            similarity = 1 - cosine(input_embeddings.flatten(), question_embeddings.flatten())

            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_question = question

        return most_similar_question, max_similarity

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
    def Get_Answer_routeInfo(x, ques):
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
         
    '''       
    def routeInfo():

        url = "http://139.59.31.166:8000/api/v2/en/station_route/*source*/*destination*/least-distance/2023-07-12%2010:36:00.000000"
        fromStn = input("From: ")
        toStn = input("To: ")

        #d = {'Rajiv Chowk': 'RCK', 'Kashmere Gate': 'KG', 'Saket': 'SAKT', 'ANAND VIHAR ISBT': 'AVIT', 'ADARSH NAGAR': 'AHNR', 'LAL QUILA': 'LLQA', 'JAMA MASJID': 'JAMD', 'DELHI GATE': 'DLIG', 'CHANDNI CHOWK': 'CHK', 'CHAWRI BAZAR': 'CWBR', 'MANDI HOUSE': 'MDHS', 'BARAKHAMBA ROAD': 'BRKR', 'NEW DELHI': 'NDI', 'UDYOG BHAWAN': 'UDB', 'JOR BAGH': 'JB', 'QUTAB MINAR': 'QM', 'SAMAYPUR BADLI': 'SPBI', 'HAIDERPUR BADLI MOR': 'BIMR', 'GURU TEG BAHADUR NAGAR': 'GTBR', 'VIDHAN SABHA': 'VS', 'SHAHEED STHAL': 'NBAA', 'NEW BUS ADDA': 'NBAA', 'NOIDA CITY CENTRE': 'NCC', 'CHHATARPUR': 'CHTP', 'GURU DRONACHARYA': 'GE', 'IFFCO CHOWK': 'IFOC', 'MILLENNIUM CITY CENTRE GURUGRAM': 'HCC', 'HUDA CITY CENTRE GURUGRAM': 'HCC', 'ROHINI SECTOR': 'RISE', 'CIVIL LINES': 'CL', 'DILLI HAAT - INA': 'INA', 'GREEN PARK': 'GNPK', 'SIKANDERPUR': 'SKRP', 'OLD FARIDABAD': 'OFDB', 'JAFRABAD': 'JFRB', 'GOLF COURSE': 'GEC', 'NAJAFGARH': 'NFGH', 'LOK KALYAN MARG': 'LKM', 'JAFRABAD': 'JFRB', 'GOLF COURSE': 'GEC', 'NAJAFGARH': 'NFGH', 'LOK KALYAN MARG': 'LKM', 'JAFRABAD': 'JFRB', 'GOLF COURSE': 'GEC', 'NAJAFGARH': 'NFGH', 'LOK KALYAN MARG': 'LKM', 'JAFRABAD': 'JFRB', 'GOLF COURSE': 'GEC', 'NAJAFGARH': 'NFGH', 'LOK KALYAN MARG': 'LKM', 'JAFRABAD': 'JFRB',
        #    'GOLF COURSE': 'GEC', 'NAJAFGARH': 'NFGH', 'LOK KALYAN MARG': 'LKM', 'JAFRABAD': 'JFRB', 'GOLF COURSE': 'GEC', 'NAJAFGARH': 'NFGH', 'LOK KALYAN MARG': 'LKM', 'MALVIYA NAGAR': 'MVNR', 'GHITORNI': 'GTNI', 'ARJAN GARH': 'AJG', 'VAISHALI': 'VASI', 'MALVIYA NAGAR': 'MVNR', 'GHITORNI': 'GTNI', 'ARJAN GARH': 'AJG', 'VAISHALI': 'VASI', 'MALVIYA NAGAR': 'MVNR', 'GHITORNI': 'GTNI', 'ARJAN GARH': 'AJG', 'VAISHALI': 'VASI', 'ITO': 'ITO', 'JAHANGIRPURI': 'JGPI', 'MAJOR MOHIT SHARMA RAJENDRA NAGAR': 'RJNM', 'MAJOR MOHIT SHARMA': 'RJNM', 'RAJENDRA NAGAR': 'RJNM', 'RAJ BAGH': 'RJBH', 'JHILMIL': 'JLML', 'NETAJI SUBHASH PLACE': 'NSHP',  'PUNJABI BAGH': 'PBGA', 'SULTANPUR': 'SLTP', 'AIIMS': 'AIIMS', 'MG ROAD': 'MGRO', 'AZADPUR': 'AZU', 'PATEL CHOWK': 'PTCK', 'VISWAVIDYALAYA': 'VW', 'HINDON RIVER': 'HDNR', 'MANSAROVAR PARK': 'MPK', 'LAXMI NAGAR': 'LN', 'MAYUR VIHAR EXTENSION': 'MVE', 'MAYUR VIHAR': 'MVE', 'SHYAM PARK': 'SMPK', 'HAUZ KHAS': 'HKS', 'TIS HAZARI': 'TZI', 'SADAR BAZAR CANTONMENT': 'SABR', 'SHYAM PARK': 'SMPK', 'HAUZ KHAS': 'HKS', 'TIS HAZARI': 'TZI', 'SADAR BAZAR CANTONMENT': 'SABR', 'SADAR BAZAR': 'SABR', 'SARAI KALE KHAN - NIZAMUDDIN': 'NIZM', 'NIZAMUDDIN': 'NIZM', 'EAST AZAD NAGAR': 'EANR'}
        
        #Fetching Station-Names from Databse
        con =c.connect(host="localhost", user="root", passwd="",database="chatbot_dmrc")
        cursor=con.cursor()
        cursor.execute("SELECT Station_Name,Station_Code FROM master_station")
        d= cursor.fetchall()
        d= dict(d)
        cursor.close() 
        fromStnIndex = find_closest_match(fromStn, list(
            map(lambda x: x.title(), list(d.keys()))))
        # print("From Index: ", fromStnIndex)
        toStnIndex = find_closest_match(toStn, list(
            map(lambda x: x.title(), list(d.keys()))))
        # print("To Index: ", toStnIndex,type(fromStnIndex), type(toStnIndex))


        if fromStnIndex is not None:
            fromStn = list(d.values())[fromStnIndex]
        else:
            print(f"Could not find a matching station for '{fromStn}'")

        if toStnIndex is not None:
            toStn = list(d.values())[toStnIndex]
        else:
            print(f"Could not find a matching station for '{toStn}'")

        #added by akhilesh
        if fromStnIndex is not None and toStnIndex is not None:
            url = url.replace("*destination*", toStn)
            url = url.replace("*source*", fromStn)
            print("Processing your request...")
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
                print(
                        f"No. of stations: {stations}, Total time: {total_time} Line: {line}, Line Number:{line_number}.")
                print("Fare is:", fare)
                # print("Towards Station:", towards_station)
                # akhilesh_code'
                # data['route'][0]['start']
                #re.sub('\W+', ' ',question)
                #input_boarding_info_askuser = input(
                #   'Do you want boarding station information: (yes/no) ?')
                input_boarding_info_askuser = re.sub('\W+', ' ',input('Do you want boarding station information: (yes/no) ?')[:1500])
                
                if 'y' in input_boarding_info_askuser.lower():
                    output_boarding_info = f"Board at station: {data['route'][0]['start']}, Towards Station: {data['route'][0]['towards_station']}, in Platform : {data['route'][0]['platform_name']} "
                    print(output_boarding_info)  # output boarding information
                elif 'n' in input_boarding_info_askuser.lower():
                    pass
                else:
                    print('Did not match your response')

                if int(len(data['route'])) > 1:
                    input_interchange_info_askuser = re.sub('\W+', ' ',input(
                        'Do you want interchange station information: (yes/no) ?')[:1500])
                    if 'y' in input_interchange_info_askuser.lower():
                        output_interchange_info = "No of Interchange station: " + \
                            str(len(data['route'])-1)
                        interchange_list_stationsname = ''
                        for i in range(1, len(data['route'])):
                            interchange_list_stationsname = interchange_list_stationsname + ', ' +\
                                data['route'][i]['start']
                        output_interchange_info = output_interchange_info + \
                            "\n Namely: " + interchange_list_stationsname
                        #print(interchange_list_stationsname)
                        #added by akhilesh
                        if ': ,' in output_interchange_info: 
                            output_interchange_info = output_interchange_info.replace(': ,',':',1)
                        print(output_interchange_info)
                        outputStations=[]
                        #interchange_list_stationsname = "" 
                        for i in range(1, len(data['route'])):
                            #interchange_list_stationsname = data['route'][i]['start'] 
                            outputStations.append(data['route'][i]['start'])

                        output_interchange_info = "No of Interchange stations are: " + \
                            str(len(data['route'])-1)+'\n'+'Namely:'
                        print(output_interchange_info, outputStations)
                    elif 'n' in input_interchange_info_askuser.lower():
                        pass
                    else:
                        print('Did not match your response')

                    # print(f"Board at station: {data['route'][0]['start']}, Towards Station:{data['route'][0]['end']}, in platform :{data['route'][0]['platform_name']} ")


            else:
                print(f"Error: {response.status_code}")
        else:
            pass 
        '''      
    #ques=input("Route?")
    #if ques=="route":
    #added by akhilesh
    #ques=input("Hi! I'm DMRC bot. How May I help you? \n If query related to metro route or fare of journey, type \"route\" \n To exit chatbot, type \"exit\" \n else: \n Enter your question: ?")
    #if "route" in ques.lower():
    def menu():
        logging.info('Displaying Menu')
        dict_menu = "If query related to metro route or fare of journey, type: \"1\"\nIf query related to QR Tickets, type: \"2\" \nIf query related to metro parking or Divyangjan, type: \"3\" \nIf query related to metro SmartCards,Tokens, type: \"4\" \nIf query related to miscellaneous , type: \"5\" \nIf query related to complaints , type: \"6\"  \nTo exit chatbot, type: \"7\"\n"
        return dict_menu
    
    '''
    #   routeInfo()
    def menu(flag):
        logging.info('Displaying Menu')
        display_text ={} 
        title_text = "Hi! I'm DMRC bot. How May I help you?"
        dict_menu = {1: "metro route or fare of journey",
                     2: "QR Tickets",
                     3: "Parking or Divyangjan",
                     4: "SmartCards,Tokens",
                     5: "miscellaneous",
                     6: "Complaints",
                     7: "exit"}
        if (flag):
            display_text={
                'menu_items':dict_menu, 
            }
               
        else:
            display_text ={'title_text': title_text,'menu_items':dict_menu} 
        # returnJson = {
        #     "displayText": "hjwfdiw"
        # }
        # return json.dumps(returnJson)
        return (display_text) 
    '''
               
    '''   
    def main():
        
        flag = True
        print("Hi! I'm DMRC bot. How May I help you? \n")

        while flag:
            #empty the previous question
            question=''
            
            # Ask the user a questi'on
            question = input("Hi! I'm DMRC bot. How May I help you? \n If query related to metro route or fare of journey, type \"route\" \n To exit chatbot, type \"exit\" \n else: \n Enter your question: ")
            #question = re.sub('\W+', ' ',input("\n If query related to metro route or fare of journey, type \"route\" \n If query related to QR Tickets, type \"QR\" \n If query related to metro parking or Divyangjan, type \"Parking\" Or \"Divyangjan\" \n If query related to metro SmartCards,Tokens, type \"SmartCards\" \n If query related to miscellaneous , type \"Misc\" \n If query related to complaints , type \"Complaint\"  \n To exit chatbot, type \"exit\"\n")[:1500].lower().strip())
            quest_menu = re.sub('\W+', ' ',input("If query related to metro route or fare of journey, type: \"1\"\nIf query related to QR Tickets, type: \"2\" \nIf query related to metro parking or Divyangjan, type: \"3\" \nIf query related to metro SmartCards,Tokens, type: \"4\" \nIf query related to miscellaneous , type: \"5\" \nIf query related to complaints , type: \"6\"  \nTo exit chatbot, type: \"7\"\n"))
            if(re.match(r'^[1-7]$',quest_menu.strip())):
                if(int(quest_menu)==1):
                    routeInfo()
                elif(int(quest_menu)==7):
                    print("Goodbye!")
                    flag=False
                    break
                else:
                    print("Please wait...")
                    question = input("\nEnter your question: ")
                    if(int(quest_menu)==2):
                        GetAnswer(question, dict_qr)
                    elif(int(quest_menu)==3):
                        GetAnswer(question, dict_parking_divyan)
                    elif(int(quest_menu)==4):
                        GetAnswer(question, dict_smartcard)
                    elif(int(quest_menu)==5):    
                        GetAnswer(question, dict_misc)
                    elif(int(quest_menu)==6):
                        GetAnswer(question, dict_complaint)
                if(AskUserToProceed(flag)):
                    pass
                else:
                    flag=False           
            else:
                print('Enter a valid response')
    '''    
                        
            
    def AskUserToProceed(flag):  #Recursive method 
        while(flag):
            Questanyother = re.sub('\W+', ' ',input('Do you have any other question? (y/n): ')[:1500].lower().strip())
            if 'y' in Questanyother:
                flag=True  
                break       
            elif 'n' in Questanyother:
                flag=False
                print("Goodbye!")
                break
            else:
                print('Enter your Response again')
        return flag       
                    
        
        return None
    def GetAnswer(question, faq_dict):
        # Find the most similar question in the dataset
        most_similar_question, similarity_score = find_most_similar_question(question, faq_dict)

        if most_similar_question is not None:
            if similarity_score < similarity_threshold:
                print("Sorry, I couldn't find a similar question in the dataset.")
            else:
                # Get the answer for the most similar question
                answer = faq_dict[most_similar_question]
                print(answer)
        else:
            print("Sorry, I couldn't find a similar question in the dataset.") 
        
        #Call from API    
    def Get_Answer(x, question):
        logging.info("Fetching Answer from Dataset")
        if(x==2):
            faq_dict =dict_qr
        elif(x==3):   
            faq_dict = dict_parking_divyan
        elif(x==4):
            faq_dict = dict_smartcard
        elif(x==5):
            faq_dict = dict_misc
        elif(x==6):
            faq_dict = dict_complaint       
                            
        # Find the most similar question in the dataset
        most_similar_question, similarity_score = find_most_similar_question(question, faq_dict)
        answer = ""
        if most_similar_question is not None:
            if similarity_score < similarity_threshold:
                answer = "Sorry, I couldn't find a similar question in the dataset."
            else:
                # Get the answer for the most similar question
                answer = faq_dict[most_similar_question]
                
        else:
            answer = "Sorry, I couldn't find a similar question in the dataset." 
        logging.info("Answers fetched successfully from Dataset")    
        return answer           
    '''
    if __name__ == "__main__":
        main() 
    '''
    
    
except Exception as e:
    logging.error("Something else went wrong: {e}")
finally:
    #con.close()
    pass

     