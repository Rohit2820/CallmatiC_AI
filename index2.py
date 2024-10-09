from flask import Flask, request, jsonify
from twilio.twiml.voice_response import Gather, VoiceResponse
from twilio.rest import Client
from google.cloud import speech_v1p1beta1 as speech
from flask_cors import CORS  # Import CORS module


app = Flask(__name__)
CORS(app)  

account_sid = "AC983e0b4c1afbefcd9e72a4343bfa3f85"   #"AC808494874d5f826ac0af22eb863f4f25"
auth_token = "9dfa426e50c4254ac84b661b249de823"      #"e6c7fd3628398ea5a9a61f7959beae71"
twilio_phone_number = "+17122275889" 

client = Client(account_sid, auth_token)
   
counter=0
def extract_question_time(filename):
    with open(filename,'r') as f:
        question_read = f.read()
    questionsFetched = [question.strip() for question in question_read.split(',')]

    questionAndTime=[]# questions = ["what is your name ?","How old are you?","What is your favourate Color","what else you want apart from what you have ?","Thank You Survey Completed"]

    for i in questionsFetched:
        questionAndTime.append(i.split(':'))

    time = []
    questions = []
    for i in questionAndTime:
        for j in i:
            if j.strip().isnumeric():
                time.append(j.strip())
            else:
                questions.append(j.strip())
    return time,questions

    
    

positive_responses_lowercase = [
    "yes, i'm free!",
    "ab5olutely, i'm available!",
    "sure thing, i'm not busy at the moment.",
    "of cour5e, i'm all yours!",
    "indeed, i've got 50me free time!",
    "ye5, i'm available to chat!",
    "definitely, no plans right now!",
    "yup, i'm not occupied at the moment.",
    "affirmative, i'm free!",
    "certainly, i'm at your 5ervice!",
    "yeah, i'm free!",
    "sure, i'm available!",
    "yep, not busy right now.",
    "of course, what's up?",
    "definitely, i've got time!",
    "sure thing, ready to chat!",
    "totally, no plans!",
    "yep, just chilling.",
    "sure thing, i'm all yours!",
    "yep, i'm here for you!",
    "yup!",
    "sure!",
    "yep!",
    'yes',
    'yeah',
    'yas',
    'yash',
    "of course!",
    "definitely!",
    "absolutely!",
    "affirmative!",
    "yeah!",
    "sure!",
    "totally!",
    "हाँ!",
    "हाँजी, मैं फ्री हूँ!",
    "जी, बोलिए!",
    'haan',
    'haan ji',
    'haanji',
    'bilkul free hu btaiye',
    'free hu boliye',
    'bilkul free hai ji btaiye aap',
    'ji madam boliye',
    'han ji',
    'han ji madam free hai',
    'han ji free hai bilkul',
    'han ji btaiye',
    'han',
    'hmm',
    'Yes.',
    'yes.'
]
answers =[]

# questions = ["what is your name ?","How old are you?","What is your favourate Color","what else you want apart from what you have ?","Thank You Survey Completed"]

def gather_response(question,time):
    response = VoiceResponse()
    with response.gather(input="speech",language='en-IN', action='https://0915-2401-4900-8845-15c8-3e91-b1eb-1a11-4497.ngrok-free.app/handle-speech',enhanced='true',speechModel="phone_call", speechTimeout=time) as gather: 
        gather.say(question)
    response.redirect("https://0915-2401-4900-8845-15c8-3e91-b1eb-1a11-4497.ngrok-free.app/handle-speech")
    return str(response)

def gather_response_no(question,time):
       response = VoiceResponse()
       with response.gather(input="speech",language='en-IN', action='https://0915-2401-4900-8845-15c8-3e91-b1eb-1a11-4497.ngrok-free.app/handle-speech-no',speechModel="experimental_conversations", speechTimeout=time) as gather: 
        gather.say(question)
       return str(response)

@app.route('/question1', methods=['POST'])                                                                                                                                                
def question1(): 
    time,questions = extract_question_time('questions.txt')
    userAnswer = request.form["SpeechResult"]
    with open('answers.txt','w') as f:
        f.write('This Call is from Callmatic Are you free now : ')
        f.write(f'\nAnswer is : {userAnswer}\n')
    print(userAnswer)
    if (userAnswer.lower() in positive_responses_lowercase):
         answers.append(userAnswer)
         return gather_response(questions[0],'auto')
    elif ('yes' in userAnswer.lower()):
         answers.append(userAnswer)
         return gather_response(questions[0],'auto')
    else:
        answers.append(userAnswer)
        return gather_response_no('when we can call you ?','auto')
    


@app.route('/handle-speech', methods=['POST'])
def handle_speech(): 
    global counter
    time,questions = extract_question_time('questions.txt')
    audio_data = request.form.get("SpeechResult")
    if (audio_data is None or audio_data.strip() == "") and counter<=len(questions):
        print('user did not answered this question ! \n')
        answers.append('user did not answered this question ! ')
        counter = counter+1
        if(counter<len(questions)):
            with open('answers.txt','a') as f:
              f.write(f'{questions[counter-1]}\n')
              f.write(' user did not answered this question ! \n')
            return gather_response(questions[counter],'auto') 
        else:
            counter = 0
            print(f'Survey completed here is the user Answers : {answers}')
            response = VoiceResponse()  
            return str(response)  
    else:
        response = VoiceResponse()
        print('user said ',audio_data)
        answers.append(audio_data)
        with open('answers.txt','a') as f:
            f.write(f'{questions[counter]}\n')
            f.write(f'Answer is : {audio_data}\n')
        counter=counter+1
        if(counter<len(questions)):    
          return gather_response(questions[counter],'auto')
        else:
            counter = 0
            print(f'Survey completed here is the user Answers : {answers}')
            response = VoiceResponse()
            return str(response)

    

@app.route('/handle-speech-no', methods=['POST'])
def handle_speech_no():
    global counter
    audio_data = request.form["SpeechResult"]
    answers.append(audio_data)
    print('user Said: ',audio_data)
    with open('answers.txt','a') as f:
        f.write('when we can call you ?\n')
        f.write(f'Answer is : {audio_data}')
        counter = 0
    response = VoiceResponse()
    return str(response)




@app.route('/make-call', methods=['POST'])
def make_outgoing_call():
    try:    
        data = request.get_json()
        twiml_response = VoiceResponse()
        with twiml_response.gather(input="speech",language='en-IN',action='https://0915-2401-4900-8845-15c8-3e91-b1eb-1a11-4497.ngrok-free.app/question1',enhanced = 'true',speechModel="phone_call", speechTimeout='auto') as gather:
            gather.say("we are calling you from Frisson are you free now ?")
        call = client.calls.create(
            to=data['mobile'],
            from_= twilio_phone_number,
            twiml=str(twiml_response)
        )
        return jsonify({"Outgoing Call SID": call.sid})

    except Exception as e:
        return jsonify({"An error Occured": str(e)})
    

# @app.route('/', methods=['GET'])
# def healthcheck():
#     print("Hii")
#     return jsonify("Hello World")

# def detect_language(text):
#     if any(ord(char) > 127 for char in text):
#         return 'hi'D
#     else:                            
#         return 'en'
    

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)

