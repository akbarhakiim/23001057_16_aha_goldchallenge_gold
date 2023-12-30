from flask import Flask, request, jsonify
from flasgger import Swagger, LazyString, LazyJSONEncoder, swag_from
import re
import pandas as pd
import sqlite3

class UploadFilecsv(Flask):
    json_provider_class = LazyJSONEncoder

app = UploadFilecsv(__name__)


    
swagger_template = dict(
info = {
    'title': LazyString(lambda: 'Cleansing data text dan file text csv'),
    'version': LazyString(lambda: '1.0.0'),
    'description': LazyString(lambda: 'Membersihkan data text dan file text csv'),
    },
    host= LazyString(lambda: request.host)
)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    'static_url_path': "/flasgger_static",
    'swagger_ui': True,
    'specs_route': "/docs/"
}
swagger = Swagger(app, template=swagger_template,
                  config=swagger_config)

@swag_from("docs/hello_world.yml", methods=['GET'])
@app.route('/', methods=['GET'])
def hello_world():
    json_response = {
        'status_code': 200,
        'description': "Menyapa Hello World",
        'data': "Hello World",
    }

    response_data = jsonify(json_response)
    return response_data

@swag_from("docs/text_processing.yml", methods=['POST'])
@app.route('/text_processing', methods=['POST'])
def text_processing():

    # proses input text dari form
    text = request.form.get('text')
    output = re.sub(r'[^a-z0-9A-Z]', ' ', text)

    conn = sqlite3.connect('data/binar_data_science.db')
    print('Openned database successfully')

    conn.execute("INSERT INTO text (raw_text, clean_text) VALUES (?, ?)", (text, output))
    
    conn.commit()
    print('Record data successfully')
    conn.close()

    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': output,
    }

    response_data = jsonify(json_response)
    return response_data

@swag_from("docs/upload.yml", methods=['POST'])
@app.route('/upload_csv', methods=['POST'])
def upload_file():

    # proses upload file csv
    file = request.files.get('file')
    
    # proses read data csv
    csv_data = pd.read_csv(file, encoding='ISO-8859-1')
    tweet = csv_data['Tweet']

    # function untuk cleansing data csv
    def cleansing(sent):
        string = sent.lower()
        string = re.sub(r'[^a-z0-9A-Z]', ' ', string)
        string = re.sub('user', '', string)
        string = re.sub('\t', '', string)
        return string
    
    # proses output data csv yang sudah dicleansing
    tweet_clean = tweet.apply(cleansing)
    tweet_clean = tweet_clean.tolist()

    json_response = {
        'status_code': 200,
        'description': "Upload berhasil",
        'data': tweet_clean,
    }

    response_data = jsonify(json_response)
    return response_data

if __name__ == '__main__':
    app.run()