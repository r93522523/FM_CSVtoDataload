from flask import Flask, request, jsonify
import paramiko
import os
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)

hostname = '35.242.211.28'
port = 2022
username = 'familymart-tw-test'
render_folder = r'/mnt/data'
key_path = os.path.join(render_folder, 'familymart-tw-test.key')

@app.route('/upload_toFTP', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Missing file'}), 400
   
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            render_path = os.path.join(render_folder, file.filename)
            file.save(render_path)
            
            done_folder = os.path.join(render_folder, 'done')
            os.makedirs(done_folder, exist_ok=True)
            done_path = os.path.join(done_folder, file.filename)
            shutil.copy(render_path, done_path)

            FTP_path = f'/APItest/{file.filename}'

            private_key = paramiko.RSAKey.from_private_key_file(key_path)
            transport = paramiko.Transport((hostname, port))
            transport.connect(username=username, pkey=private_key)
            sftp = paramiko.SFTPClient.from_transport(transport)

            sftp.put(render_path, FTP_path)
            sftp.close()
            transport.close()

            os.remove(render_path)

            return jsonify({'message': 'File uploaded successfully'}), 200
        else:
            return jsonify({'error': 'No CSV file found'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
#    app.run(debug=True)
