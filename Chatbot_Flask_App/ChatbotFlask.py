try:
    from flask import Flask, jsonify, request
    import logging
    from ChatbotAPI_code import menu, Get_Answer,Get_Answer_routeInfo
    
    import re
    app = Flask(__name__)
    
    @app.route('/home')
    def getMenu():
        logging.info('Get Request To Home method')
        data = menu(False)
        logging.info('Get Response From Home Method')
        
        return jsonify(data)
        
    @app.route('/home/', methods=["POST"])
    def GetAnswer():
        x:int = request.json['menu_item'] 
        ques = request.json['question']
        logging.info('Post Request To Home method')
        if(re.match(r'^[1-7]$',str(x))):
            if x==1:
                ans = Get_Answer_routeInfo(x, ques)
                return jsonify({'ans': ans})
            elif(x==7):
                return jsonify({'pagename': "Goodbye!"})
            else:
                ans = Get_Answer(x,ques)
                return jsonify({'ans': ans})         
        else: 
            return jsonify({'title_text': 'Invalid Menu Item'})
    if __name__=="__main__":
        logging.info('*********** Start of program ***************') 
        app.run(host='0.0.0.0', port=8080)
        app.run(debug=True)
             
except Exception as e:
    logging.exception(" Something else went wrong: {e} in function:")