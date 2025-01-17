try:
    from flask import Flask, request,jsonify
    import logging
    #from ChatbotAPI_code import menu, Get_Answer,Get_Answer_routeInfo
    #from ChatbotAPI_code import menu, Get_Answer,Get_Answer_routeInfo
    from apps.ChatbotAPI_code import menu
    #from functools import lru_cache
    from time import perf_counter
    from flask_cors import cross_origin
    import re
    app = Flask(__name__)
    
    #@lru_cache(maxsize = None)
    @app.route('/home')
    @cross_origin()
    def getMenu():
        t1_start = perf_counter() 
        logging.info('Get Request To Home method')
        data = menu()
        logging.info('Get Response From Home Method')
        t2_end = perf_counter() 
    
        #data = data + 'cache info is: "/' +cacheinfo + '"/' 
        #return jsonify({'menu':data + f'\n Execution time:  {t2_end - t1_start:.3}s ','default-text': 'Enter your question'})
        return jsonify({'menu':data , 'Execution-time': f'{t2_end - t1_start:.3}s ','default-text': 'Enter your question'})
    @app.route('/home/', methods=["POST"])
    @cross_origin()
    def GetAnswer():    
        from apps.ChatbotAPI_code import Get_Answer, Get_Answer_routeInfo
        x:int = request.json['menu_item'] 
        ques = request.json['question']
        logging.info('Post Request To Home method')
        t1_start = perf_counter() 
        if(re.match(r'^[1-7]$',str(x))):
            if x==1:
                ans = Get_Answer_routeInfo(ques)
                t2_end = perf_counter()
                #return jsonify({'ans': ans})
                #return jsonify({'answer': ans +'\n'+f' Execution time:  {t2_end - t1_start:.3}s '})
                return jsonify({'answer': ans , 'Execution-time':f'{t2_end - t1_start:.3}s '})
                
            #elif(x==7):
            elif(x==4):
                #return jsonify({'pagename': "Goodbye!"})
                t2_end = perf_counter()
                #return "Goodbye!" + f'\n Execution time:  {t2_end - t1_start:.3}s '
                #return jsonify({'answer': "Goodbye!" +"\n" + f' Execution time:  {t2_end - t1_start:.3}s '})
                return jsonify({'answer': "Goodbye!", 'Execution-time': f'{t2_end - t1_start:.3}s '})
                
            else:
                ans = Get_Answer(x,ques)
                t2_end = perf_counter()
                #return ans + f'\nExecution time:  {t2_end - t1_start:.3}s '    
                #return jsonify({'answer':ans +'\n' + f' Execution time:  {t2_end - t1_start:.3}s '})
                return jsonify({'answer':ans , 'Execution-time': f'{t2_end - t1_start:.3}s '})   
        else: 
            #return jsonify({'title_text': 'Invalid Menu Item'})
            t2_end = perf_counter()
            #return 'Invalid Menu Item' + f'\n Execution time:  {t2_end - t1_start:.3}s '
            return jsonify({'answer':'Invalid Menu Item' , 'Execution-time': f'{t2_end - t1_start:.3}s '})    

             
    if __name__=="__main__":
        logging.info('*********** Start of program ***************') 
        #getMenu.cache_clear()
        
        app.run(host='0.0.0.0', port=8080)
        app.run(debug=True)
    
             
except Exception as e:
    logging.exception(" Something else went wrong: {e} in function:")