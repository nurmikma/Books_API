from flask import Flask, jsonify, request
import os
import json
import requests
from azure.storage.blob import BlobServiceClient
from flask_cors import CORS


app = Flask(__name__)
cors = CORS(app, resources={r"/raamatud/*": {"origins": "*"}, r"/raamatu_otsing/*": {"origins": "*"}})

# Azure blob konfiguratsioon
blob_connection_string = os.getenv('AZURE_BLOB_CONNECTION_STRING') 
blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
blob_container_name = "hslabnurmik8"

#meetodi uue Azure blob konteineri loomiseks
def blob_konteineri_loomine(konteineri_nimi):
    container_client = blob_service_client.get_container_client(container=konteineri_nimi)
    if not container_client.exists():
        blob_service_client.create_container(konteineri_nimi)
        print(f"Konteiner '{konteineri_nimi}' loodud.")
    else:
        print(f"Konteiner '{konteineri_nimi}' juba eksisteerib.")

#meetodi Azure blob konteineri siseste objektide nimekirja tagastamiseks.
def blob_raamatute_nimekiri():
    container_client = blob_service_client.get_container_client(container=blob_container_name)
    blobs_list = container_client.list_blobs()
    raamatud_nimekiri = [blob.name for blob in blobs_list]
    return raamatud_nimekiri

#meetodi Azure blob objekti/faili SISU alla laadimiseks konteinerist.
def blob_alla_laadimine(faili_nimi):
    blob_client = blob_service_client.get_blob_client(container=blob_container_name, blob=faili_nimi)
    blob_sisu = blob_client.download_blob().content_as_text()
    return blob_sisu

#meetodi uue Azure blob objekti/faili loomiseks, ehk üles laadimiseks konteinerisse.
def blob_ules_laadimine_sisu(faili_nimi, sisu):
    blob_client = blob_service_client.get_blob_client(container=blob_container_name, blob=faili_nimi)
    blob_client.upload_blob(sisu)
    print(f"Fail '{faili_nimi}' üles laaditud konteinerisse '{blob_container_name}'.")

#meetodi uue Azure blob objekti/faili kustutamiseks konteinerist.
def blob_kustutamine(faili_nimi):
    blob_client = blob_service_client.get_blob_client(container=blob_container_name, blob=faili_nimi)
    blob_client.delete_blob()
    print(f"Fail '{faili_nimi}' kustutatud konteinerist '{blob_container_name}'.")

#meetod raamatute nimekirja vaatamiseks
@app.route('/raamatud/', methods=['GET'])
def raamatu_nimekiri():
    try:
        raamatud = blob_raamatute_nimekiri()
        raamatud = [book.replace('.txt', '') for book in raamatud if book.endswith('.txt')]
        return jsonify({"raamatud": raamatud}), 200
    except Exception:
        return jsonify({}), 400

#meetod raamatu allatõmbamiseks
@app.route('/raamatud/<book_id>', methods=['GET'])
def raamatu_allatombamine(book_id):
    if not book_id.isnumeric():
        return jsonify({}), 400
    try:
        faili_nimi = f'{book_id}.txt'
        raamatu_sisu = blob_alla_laadimine(faili_nimi)
        return raamatu_sisu, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception:
        return jsonify({}), 404

#meetod raamatu kustutamiseks
@app.route('/raamatud/<book_id>', methods=['DELETE'])
def raamatu_kustutamine(book_id):
    if not book_id.isnumeric():
        return jsonify({}), 400
    try:
        faili_nimi = f'{book_id}.txt'
        blob_kustutamine(faili_nimi)
        return jsonify({}), 204
    except Exception:
        return jsonify({}), 404

#meetod failide alla tõmbamiseks Gutenbergist
@app.route('/raamatud/', methods=['POST'])
def raamatu_lisamine():
    input_data = request.json
    raamatu_id = input_data.get('raamatu_id')
    if not raamatu_id or not raamatu_id.isnumeric():
        return jsonify({}), 400
    url = f'http://gutenberg.org/cache/epub/{raamatu_id}/pg{raamatu_id}.txt'
    response = requests.get(url)
    if response.status_code == 404:
        return jsonify({}), 404
    try:
        blob_ules_laadimine_sisu(f'{raamatu_id}.txt', response.text)
        return jsonify({"tulemus": "Raamatu loomine õnnestus", "raamatu_id": raamatu_id}), 201
    except Exception:
        return jsonify({}), 400

if __name__ == '__main__':
    blob_konteineri_loomine(blob_container_name)
    app.run(debug=True, host='0.0.0.0')
