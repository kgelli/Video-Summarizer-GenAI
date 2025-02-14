#!/usr/bin/env python3

import cgi
import cgitb
import os
import time
import google.generativeai as genai

cgitb.enable()


# Ensure API key is correctly configured
api_key = "Your Api Key Here"  # Replace with your actual API key
genai.configure(api_key=api_key)

form = cgi.FieldStorage()
fileitem = form['file']

if fileitem.filename:
    fn = os.path.basename(fileitem.filename)
    open('/tmp/' + fn, 'wb').write(fileitem.file.read())

    def upload_to_gemini(path, mime_type=None):
        try:
            file = genai.upload_file(path, mime_type=mime_type)
            return file
        except Exception as e:
            print(f"<p>Error uploading file to Gemini: {e}</p>")
            return None

    def wait_for_files_active(files):
        for name in (file.name for file in files):
            file = genai.get_file(name)
            while file.state.name == "PROCESSING":
                time.sleep(10)
                file = genai.get_file(name)
            if file.state.name != "ACTIVE":
                raise Exception(f"File {file.name} failed to process")

    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
    )

    files = [
        upload_to_gemini("/tmp/" + fn, mime_type="video/mp4"),
    ]

    if all(files):  # Check if all uploads were successful
        wait_for_files_active(files)

        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        files[0],
                    ],
                },
            ]
        )

        response = chat_session.send_message("explain me entire video and create a summary of it")

        print(f"<h2>Summary of the video:</h2><p>{response.text}</p>")
    else:
        print("<h2>File upload failed</h2>")
else:
    print("<h2>No file uploaded</h2>")
