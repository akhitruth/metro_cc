import pandas as pd
import requests
import json
import difflib
import tensorflow as tf
from torch.utils.data import TensorDataset
from scipy.spatial.distance import cosine
from transformers import DistilBertTokenizer, TFDistilBertModel

# Load the DistilBERT tokenizer and model
tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
model = TFDistilBertModel.from_pretrained("distilbert-base-uncased", output_hidden_states=True)

# Load the FAQ questions and answers from the Excel file
df = pd.read_excel("newchatbot.xlsx")
faq_dict = dict(zip(df["Question"], df["Answer"]))

# Load the station names and codes from the Excel file
station_df = pd.read_excel("newstation.xlsx")
station_dict = dict(zip(station_df["NAME"].str.title(), station_df["CODE"]))

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
    closest_match = difflib.get_close_matches(input_str.title(), options, n=1, cutoff=0.8)
    return closest_match[0] if closest_match else None

def route_info():
    from_stn = input("From: ").title()
    to_stn = input("To: ").title()
    print("Please wait...")

    from_stn_code = station_dict.get(from_stn)
    to_stn_code = station_dict.get(to_stn)

    if not from_stn_code:
        print(f"Could not find a matching station for '{from_stn}'")
        return

    if not to_stn_code:
        print(f"Could not find a matching station for '{to_stn}'")
        return

    url = "http://139.59.31.166:8000/api/v2/en/station_route/{from_stn_code}/{to_stn_code}/least-distance/2023-07-12%2010:36:00.000000"
    url = url.format(from_stn_code=from_stn_code, to_stn_code=to_stn_code)

    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        stations = data['stations']
        total_time = data['total_time']
        fare = data['fare']
        line = data['route'][0]['line']
        line_number = data['route'][0]['line_no']
        towards_station = data['route'][0]['towards_station']

        print(f"No. of stations: {stations}, Total time: {total_time}, Total Fare: {fare} .")

        input_boarding_info_askuser = input('Do you want boarding station information: (yes/no) ? ')
        if input_boarding_info_askuser.lower() == 'yes':
            output_boarding_info = f"Board at station: {data['route'][0]['start']}, Towards Station: {data['route'][0]['towards_station']}, in Platform : {data['route'][0]['platform_name']} "
            print(output_boarding_info)
        elif input_boarding_info_askuser.lower() == 'no':
            pass
        else:
            print('Did not match your response')

        if len(data['route']) > 1:
            input_interchange_info_askuser = input('Do you want interchange station information: (yes/no) ? ')
            if input_interchange_info_askuser.lower() == 'yes':
                outputStations = [data['route'][i]['start'] for i in range(1, len(data['route']))]
                print(f"No of Interchange stations are: {len(data['route'])-1}, Namely: {outputStations}")
            elif input_interchange_info_askuser.lower() == 'no':
                pass
            else:
                print('Did not match your response')
    else:
        print(f"Error: {response.status_code}")

def main():
    similarity_threshold = 0.85

    while True:
        question = input("Hi! I'm DMRC bot. How may I help you? \nIf your query is related to metro route or fare of journey, type 'route'. \nTo exit the chatbot, type 'exit'. \nOtherwise, enter your question: ")

        if question.lower() == 'route':
            
            route_info()
            continue
        elif question.lower() == "exit":
            print("Goodbye!")
            break

        print("Please wait...")
        most_similar_question, similarity_score = find_most_similar_question(question, faq_dict)

        if most_similar_question is not None:
            if similarity_score >= similarity_threshold:
                answer = faq_dict[most_similar_question]
                print(answer)
            else:
                print("Sorry, I couldn't find a similar question in the dataset.")
        else:
            print("Sorry, I couldn't find a similar question in the dataset.")

if __name__ == "__main__":
    main()
