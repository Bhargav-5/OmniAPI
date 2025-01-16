from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import google.generativeai as genai

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

context = {}




@app.route('/api/main', methods=['POST'])
def select_api():
    data = request.get_json()
    query = data.get("query")
    
    genai.configure(api_key=os.getenv('API_KEY'))
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    try:
        prompt = f''' 
                    You are an intelligent system designed to classify user prompts and route them to the appropriate API or function based on the user's intent and stored context. The available APIs are:

                        1. **Image_Generation_API**: Use this API when the user explicitly asks for an image or describes something to visualize.
                        - Example queries: "Generate an image of a futuristic city," "Show me a painting of a lion in a jungle."

                        2. **Information_Retrieval_API**: Use this API when the user asks for factual information, general knowledge, or research-based content.
                        - Example queries: "What is the capital of France?", "Tell me about the benefits of meditation."

                        3. **Telugu_Response_API**: Use this API when the user wants a response in Telugu or if the intent is conversational and does not match the criteria for the other two APIs.
                        - Example queries: "మీరు ఎలా ఉన్నారు?" (How are you?), "నాకు తెలుగు లో జోక్ చెప్పండి" (Tell me a joke in Telugu).

                        ### Instructions:
                        1. Analyze the **current user query**.
                        2. Consider the **context of previous interactions** (if available) to understand the user's intent.
                        3. Decide which API is most suitable for handling the query.

                        ### Context:
                        {context}

                        ### Current User Query:
                        {query}

                        Respond with the **exact name of the API** to use (i.e., "Image_Generation_API", "Information_Retrieval_API", or "Telugu_Response_API") do not give any further explanation for the given query.
                  '''
        response = model.generate_content([prompt])
        generated_text = response.text.strip()
        # print("GEN TEXT : ", generated_text) 
        # api_dict = {
        #     "Image_Generation_API": "Vinuthna",
        #     "Information_Retrieval_API": "Chandrima",
        #     "Telugu_Response_API": "Bhargav"
        # }
        msg = []
        if(generated_text == "Image_Generation_API"):
            msg.append({"replyImage":"api_call_to_vinuthna","reply":None})
        elif(generated_text == "Information_Retrieval_API"):
            msg.append({"replyImage":None,"reply":"api_call_to_chandrima"})
        else:
            try:
                telugu_api_url = "https://defeated-cathi-bhargavramkongara-d69e1f60.koyeb.app/get_telugu_response"
                payload = {"message":query}
                headers = {"Content-Type": "application/json"}
                # print("PAYLOAD : ",payload)
                telugu_response = requests.post(telugu_api_url,json=payload,headers=headers)
                # print("TELUGU RESPONSE : ",telugu_response)
                # telugu_response.raise_for_status()
                # print("BELOW RAISE FOR STATUS")
                api_msg_bhargav = telugu_response.json()
                # print("API_MSG_BHARGAV : ",api_msg_bhargav)
                
                msg.append({"replyImage":None, "reply":api_msg_bhargav.get("response","No response found")})
            except requests.exceptions.RequestException as e:
                # print("EXCEPTION IS : ",e)
                msg.append({"replyImage":None, "reply":"Error retrieving telugu response"})
        # print("-"*54)
        # print("MSG[0] : ",msg[0])   
        # print("-"*54) 
        return jsonify(msg[0])       
    except Exception as e:
        return {"replyImage":None,"reply":None}, 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
