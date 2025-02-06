from flask import Flask, jsonify, request
import os
import json
import re
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

#meetod failist sõne otsimiseks
@app.route('/raamatu_otsing/<raamatu_id>/', methods=['POST'])
def raamatust_sone_otsimine(raamatu_id):
    input_data = request.json
    sone = input_data.get('sone')
    if not raamatu_id or not raamatu_id.isnumeric() or not sone:
        return jsonify({}), 400
    try:
        faili_nimi = f'{raamatu_id}.txt'
        sisu = blob_alla_laadimine(faili_nimi)
        leitud = len(re.findall(r'\b' + re.escape(sone) + r'\b', sisu, re.IGNORECASE))
        return jsonify({"raamatu_id": raamatu_id, "sone": sone, "leitud": leitud}), 200
    except Exception:
        return jsonify({}), 404

@app.route('/raamatu_otsing/', methods=['POST'])
def koikidest_raamatutest_sone_otsimine():
    input_data = request.json
    sone = input_data.get('sone')
    if not sone:
        return jsonify({}), 400
    tulemused = []
    try:
        raamatud_nimekiri = blob_raamatute_nimekiri()
        for faili_nimi in raamatud_nimekiri:
            raamatu_id = os.path.splitext(faili_nimi)[0]
            sisu = blob_alla_laadimine(faili_nimi)
            leitud = len(re.findall(r'\b' + re.escape(sone) + r'\b', sisu, re.IGNORECASE))
            if leitud > 0:
                tulemused.append({"raamatu_id": raamatu_id, "leitud": leitud})
        return jsonify({"sone": sone, "tulemused": tulemused}), 200
    except Exception:
        return jsonify({}), 400

if __name__ == '__main__':
    blob_konteineri_loomine(blob_container_name)
    app.run(debug=True, host='0.0.0.0')
