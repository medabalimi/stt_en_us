#!venv/bin/python

from stt_api import app
import os
import requests
import tqdm

if __name__ == "__main__":
    for asr_model_type in app.config['ASR_MODELS']:
        print("Checking if models exist.")
        asr_model = app.config['ASR_MODELS'][asr_model_type]
        model_path = f"{app.config['ASR_MODEL_FOLDER']}/{asr_model}.nemo"
        if not os.path.exists(model_path):

            URL = f"https://api.ngc.nvidia.com/v2/models/nvidia/nemo/{asr_model}/versions/1.6.0/files/{asr_model}.nemo"
            print(f"Downloading missing model {asr_model} from {URL}")
            response = requests.get(URL, stream=True)
            block_size = 1024 * 1024
            total_size_in_bytes = int(response.headers.get('content-length', 0))
            total_chunks = 0
            progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)

            with open(model_path, 'wb') as of:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        progress_bar.update(len(chunk))
                        of.write(chunk)

    app.run(host="0.0.0.0", debug=True)

