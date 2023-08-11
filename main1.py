import requests
import json
import difflib
import mysql.connector as c

url = "http://139.59.31.166:8000/api/v2/en/station_route/*source*/*destination*/least-distance/2023-07-12%2010:36:00.000000"


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





fromStn = input("From: ")
toStn = input("To: ")

d = {'Rajiv Chowk': 'RCK', 'Kashmere Gate': 'KG', 'Saket': 'SAKT', 'ANAND VIHAR ISBT': 'AVIT', 'ADARSH NAGAR': 'AHNR', 'LAL QUILA': 'LLQA', 'JAMA MASJID': 'JAMD', 'DELHI GATE': 'DLIG', 'CHANDNI CHOWK': 'CHK', 'CHAWRI BAZAR': 'CWBR', 'MANDI HOUSE': 'MDHS', 'BARAKHAMBA ROAD': 'BRKR', 'NEW DELHI': 'NDI', 'UDYOG BHAWAN': 'UDB', 'JOR BAGH': 'JB', 'QUTAB MINAR': 'QM', 'SAMAYPUR BADLI': 'SPBI', 'HAIDERPUR BADLI MOR': 'BIMR', 'GURU TEG BAHADUR NAGAR': 'GTBR', 'VIDHAN SABHA': 'VS', 'SHAHEED STHAL': 'NBAA', 'NEW BUS ADDA': 'NBAA', 'NOIDA CITY CENTRE': 'NCC', 'CHHATARPUR': 'CHTP', 'GURU DRONACHARYA': 'GE', 'IFFCO CHOWK': 'IFOC', 'MILLENNIUM CITY CENTRE GURUGRAM': 'HCC', 'HUDA CITY CENTRE GURUGRAM': 'HCC', 'ROHINI SECTOR': 'RISE', 'CIVIL LINES': 'CL', 'DILLI HAAT - INA': 'INA', 'GREEN PARK': 'GNPK', 'SIKANDERPUR': 'SKRP', 'OLD FARIDABAD': 'OFDB', 'JAFRABAD': 'JFRB', 'GOLF COURSE': 'GEC', 'NAJAFGARH': 'NFGH', 'LOK KALYAN MARG': 'LKM', 'JAFRABAD': 'JFRB', 'GOLF COURSE': 'GEC', 'NAJAFGARH': 'NFGH', 'LOK KALYAN MARG': 'LKM', 'JAFRABAD': 'JFRB', 'GOLF COURSE': 'GEC', 'NAJAFGARH': 'NFGH', 'LOK KALYAN MARG': 'LKM', 'JAFRABAD': 'JFRB', 'GOLF COURSE': 'GEC', 'NAJAFGARH': 'NFGH', 'LOK KALYAN MARG': 'LKM', 'JAFRABAD': 'JFRB',
     'GOLF COURSE': 'GEC', 'NAJAFGARH': 'NFGH', 'LOK KALYAN MARG': 'LKM', 'JAFRABAD': 'JFRB', 'GOLF COURSE': 'GEC', 'NAJAFGARH': 'NFGH', 'LOK KALYAN MARG': 'LKM', 'MALVIYA NAGAR': 'MVNR', 'GHITORNI': 'GTNI', 'ARJAN GARH': 'AJG', 'VAISHALI': 'VASI', 'MALVIYA NAGAR': 'MVNR', 'GHITORNI': 'GTNI', 'ARJAN GARH': 'AJG', 'VAISHALI': 'VASI', 'MALVIYA NAGAR': 'MVNR', 'GHITORNI': 'GTNI', 'ARJAN GARH': 'AJG', 'VAISHALI': 'VASI', 'ITO': 'ITO', 'JAHANGIRPURI': 'JGPI', 'MAJOR MOHIT SHARMA RAJENDRA NAGAR': 'RJNM', 'MAJOR MOHIT SHARMA': 'RJNM', 'RAJENDRA NAGAR': 'RJNM', 'RAJ BAGH': 'RJBH', 'JHILMIL': 'JLML', 'NETAJI SUBHASH PLACE': 'NSHP',  'PUNJABI BAGH': 'PBGA', 'SULTANPUR': 'SLTP', 'AIIMS': 'AIIMS', 'MG ROAD': 'MGRO', 'AZADPUR': 'AZU', 'PATEL CHOWK': 'PTCK', 'VISWAVIDYALAYA': 'VW', 'HINDON RIVER': 'HDNR', 'MANSAROVAR PARK': 'MPK', 'LAXMI NAGAR': 'LN', 'MAYUR VIHAR EXTENSION': 'MVE', 'MAYUR VIHAR': 'MVE', 'SHYAM PARK': 'SMPK', 'HAUZ KHAS': 'HKS', 'TIS HAZARI': 'TZI', 'SADAR BAZAR CANTONMENT': 'SABR', 'SHYAM PARK': 'SMPK', 'HAUZ KHAS': 'HKS', 'TIS HAZARI': 'TZI', 'SADAR BAZAR CANTONMENT': 'SABR', 'SADAR BAZAR': 'SABR', 'SARAI KALE KHAN - NIZAMUDDIN': 'NIZM', 'NIZAMUDDIN': 'NIZM', 'EAST AZAD NAGAR': 'EANR'}
#Fetching Station-Names from Databse
#con =c.connect(host="localhost", user="root", passwd="",database="chatbot_dmrc")
#cursor=con.cursor()
#cursor.execute("SELECT Station_Name,Station_Code FROM master_station")
#d= cursor.fetchall()
#d= dict(d)

fromStnIndex = find_closest_match(fromStn, list(
    map(lambda x: x.title(), list(d.keys()))))

toStnIndex = find_closest_match(toStn, list(
    map(lambda x: x.title(), list(d.keys()))))



if fromStnIndex is not None:
    fromStn = list(d.values())[fromStnIndex]
else:
    print(f"Could not find a matching station for '{fromStn}'")

if toStnIndex is not None:
    toStn = list(d.values())[toStnIndex]
else:
    print(f"Could not find a matching station for '{toStn}'")
    
    #added by akhilesh
if fromStnIndex is not None or toStnIndex is not None:
    url = url.replace("*destination*", toStn)

    url = url.replace("*source*", fromStn)

    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        # pprint.pprint(data)

        stations = data['stations']
        total_time = data['total_time']
        fare = data['fare']
        line = (data['route'][0]['line'])
        line_number = (data['route'][0]['line_no'])
        towards_station = (data['route'][0]['towards_station'])
        
        print(
            f"No. of stations: {stations}, Total time: {total_time}, Total Fare: {fare} .")

        
        # data['route'][0]['start']
        # Region Displaying boarding station info
        input_boarding_info_askuser = input(
            'Do you want boarding station information: (yes/no) ? ')
        if input_boarding_info_askuser.lower() == 'yes':
            output_boarding_info = f"Board at station: {data['route'][0]['start']}, Towards Station: {data['route'][0]['towards_station']}, in Platform : {data['route'][0]['platform_name']} "
            print(output_boarding_info)  # output boarding information
        elif input_boarding_info_askuser.lower() == 'no':
            pass
        else:
            print('Did not match your response')
        # end region


        if int(len(data['route'])) > 1:
            input_interchange_info_askuser = input(
                'Do you want interchange station information: (yes/no) ? ')  # Displaying interchange station information
            if input_interchange_info_askuser.lower() == 'yes':
                
                outputStations=[]
                #interchange_list_stationsname = "" 
                for i in range(1, len(data['route'])):
                    #interchange_list_stationsname = data['route'][i]['start'] 
                    outputStations.append(data['route'][i]['start'])

                output_interchange_info = "No of Interchange stations are: " + \
                    str(len(data['route'])-1)+'\n'+'Namely:'
                print(output_interchange_info, outputStations)
                
                # print(outputStations)
            elif input_interchange_info_askuser.lower() == 'no':
                pass
            else:
                print('Did not match your response')

            # print(f"Board at station: {data['route'][0]['start']}, Towards Station:{data['route'][0]['end']}, in platform :{data['route'][0]['platform_name']} ")


    else:
        print(f"Error: {response.status_code}")
else: 
    pass 
#cursor.close()       
