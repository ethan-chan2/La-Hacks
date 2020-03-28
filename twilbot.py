from flask import Flask, request, session, send_file
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

app = Flask(__name__)

def create_client():
    account_sid = "ACab302ee65e2d6d41c34b1d1f14773625"
    auth_token  = "513ce6d58e34278250b357f1744542d0"
    client = Client(account_sid, auth_token)
    return client

@app.route("/sms", methods=['GET', 'POST'])
def sms_send_reply():
    """Respond to incoming messages with a friendly SMS."""
    resp = MessagingResponse()

    resp.message("yo, whats up")

    return str(resp)

def send_question(client):
    user_input = input('enter a message\n')
    message = client.messages.create(
                    to="+16266506683", 
                    from_="+16015640369",
                    body=user_input)
    print(message.sid)

##def main(client):
##    running = True
##    while running:
##        have_question = False
##        while not have_question:
##            send_question(client)
##            have_question = True
##        have_response = False
##        while not have_response:
##            app.run(debug=True)
##            have_response = True
##            
##        have_question = False
##        have_response = False

if __name__ == "__main__":
    client = create_client()
##    main(client)
    send_question(client)
    app.run(debug=True)


