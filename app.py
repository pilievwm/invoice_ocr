from flask import Flask, request, jsonify
from checkMail import main as check_mail_main
import socket
import os
import base64
import json
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv('.env')

@app.route('/checkmail', methods=['POST'])
def notifications():
    # Process the request payload
    data = request.get_json()

    # Decode the base64 encoded 'data' field from the 'message' object
    message_data = base64.b64decode(data['message']['data']).decode('utf-8')
    message_json = json.loads(message_data)
    
    # Here you could add any conditions you want to check before triggering the email processing.
    # For example, you might want to check the 'emailAddress' field in the decoded message.
    check_mail_main()

    return jsonify({'status': 'success'}), 200

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Use the DNS address from the environment variables
    s.connect((os.environ['DNS_ADDRESS'], int(os.environ['DNS_PORT'])))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    data_dir=os.environ['CERT_DIR']
    host = get_ip_address()
    app.run(debug=True, host=host, port=port, ssl_context=(os.path.join(data_dir, os.environ['FULLCHAIN_FILE']), os.path.join(data_dir, os.environ['PRIVKEY_FILE'])))
