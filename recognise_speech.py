import io, os
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.cloud import translate
from google.cloud import texttospeech
from flask import jsonify, Flask, request, render_template, redirect
from flask import Flask, flash, request, redirect, render_template, send_from_directory
from werkzeug.utils import secure_filename

client = speech.SpeechClient()

filename = 'hin.wav'

app = Flask(__name__)

def get_transcript(filename, lang):
	with io.open(filename, 'rb') as fi:
		content = fi.read()
		audio = types.RecognitionAudio(content=content)

	config = types.RecognitionConfig(
		encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16,
	    sample_rate_hertz=8000,
	    language_code=lang)

	response = client.recognize(config, audio)
	# print(response)
	for result in response.results:
		return result.alternatives[0].transcript

# @app.route('/')
# def upload_form():
# 	return render_template('hello.html')

@app.route('/translate', methods=['POST','GET'])
def trans():
	# if request.method == 'POST':
	# 	print('here')

	# 	if 'file' not in request.files:
	# 		flash('No file part')
	# 		return redirect(request.url)

	# 	file = request.files['file']
	# 	filename = secure_filename(file.filename)
	# 	print(filename)
	# 	file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	# 	flash('File successfully uploaded')
	# 	return redirect('/')
		file = request.files['file']
		print('-----')
		print(file)
		print(type(file))
		filename = secure_filename(file.filename)
		print(filename)
		file.save(os.path.join('uploads', filename))
		print('saved')

		# filename = request.args.get('filename')
		lang = request.args.get('lang')
		target = request.args.get('target')
		print(lang, target)

		text = get_transcript(os.path.join('uploads', filename), lang)
		print(f'Text: {text}')
		data = {'text': text}

		translate_client = translate.Client()
		translation = translate_client.translate(
	    text,
	    target_language=target)

		translated_text = translation['translatedText']
		data['translation'] = translated_text
		with open('txt.txt','w', encoding='utf-8') as file:
			file.write(str(data))
		# translated_audio = tts(translated_text, target)
		# data['audio'] = translated_audio
		print(data)
		return jsonify(data)
		# return redirect(request.url)

def tts(text, lang, filename):
	client = texttospeech.TextToSpeechClient()
	synthesis_input = texttospeech.types.SynthesisInput(text=text)
	voice = texttospeech.types.VoiceSelectionParams(
    language_code=lang,
    ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)

	audio_config = texttospeech.types.AudioConfig(audio_encoding=texttospeech.enums.AudioEncoding.MP3)

	response = client.synthesize_speech(synthesis_input, voice, audio_config)

	save_file = os.path.join('audio',f'{filename}.mp3')
	with open(save_file, 'wb') as out:
	# Write the response to the output file.
	    out.write(response.audio_content)
	    print('Audio content written to file "output.mp3"')
	    return save_file

@app.route('/tts', methods=['POST','GET'])
#user id, text, lang -> saves audio, returns path
def audio():
	user = request.args.get('user')
	lang = request.args.get('lang')
	text = request.args.get('text')

	filename = tts(text, lang, user)
	return {'file':filename}

@app.route('/audio/<path:path>')
def send_js(path):
    return send_from_directory('audio', path)

if __name__=='__main__':
	app.run('localhost', debug=True)

