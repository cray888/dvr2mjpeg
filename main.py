#http://192.168.0.2:5555/mjpeg?address=89.185.93.107&port=34567&login=380&password=380&chanel=4&stream=0
#http://192.168.0.2:5555/snapshot?address=89.185.93.107&port=34567&login=380&password=380&chanel=4&stream=0
#http://localhost:5555/snapshot?address=89.185.93.132&port=26715&login=o9yh0b&password=sh158&chanel=5&stream=0

from cmath import isnan, nan
from datetime import datetime, timedelta
from email.mime import image
from xmlrpc.client import boolean
from dvrip.io import DVRIPClient
from dvrip.monitor import Monitor, MonitorAction, MonitorClaim, DoMonitor, MonitorParams, Stream
from socket import AF_INET, SOCK_STREAM, socket as Socket
from av.packet import Packet
from av.codec.context import CodecContext
import io

from flask import Flask, Response, request, send_file
app = Flask(__name__)

@app.route('/')
def hello():
    return "DVR to mjpeg streamer!"

@app.route('/mjpeg')
def mjpeg():
	address = request.args.get('address')
	port = int(request.args.get('port'))
	login = request.args.get('login')
	password = request.args.get('password')
	chanel = int(request.args.get('chanel')) - 1
	stream = int(request.args.get('stream'))
	return Response(gather_img_stream(address, port, login, password, chanel, stream, 25), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/snapshot')
def snapshot():
	address = request.args.get('address')
	port = int(request.args.get('port'))
	login = request.args.get('login')
	password = request.args.get('password')
	chanel = int(request.args.get('chanel')) - 1
	stream = int(request.args.get('stream'))
	return send_file(gather_img_static(address, port, login, password, chanel, stream), mimetype='image/jpeg')

def gather_img_stream(address, port, login, password, chanel, stream, fps):
	(client, reader) = get_reader(address, port, login, password, chanel, stream)
	codec = CodecContext.create('h264', 'r')
	now = datetime.now()
	while True:
		data = b''
		while True:
			if reader.readable():
				if chunk := reader.read(1024):
					data += chunk
				if len(chunk) < 1024:
					break
		if len(data) > 0:
			frame = nan
			nodata = False
			try:
				packet = Packet(data)
				frame = codec.decode(packet)
			except:
				nodata = True
			if nodata == False and len(frame) > 0:
				imgByteArr = io.BytesIO()
				frame[0].to_image().save(imgByteArr, format='jpeg', quality=20, optimize=True)
				imgByteArr = imgByteArr.getvalue()
				yield (b'--frame\r\nContent-Type: image/jpeg\r\nContent-Length: ' + f"{len(imgByteArr)}".encode() + b'\r\n\r\n' + imgByteArr + b'\r\n')
			if (datetime.now() - now).seconds > 10:
				print(client.time())
				now = datetime.now()

def gather_img_static(address, port, login, password, chanel, stream):
	(client, reader) = get_reader(address, port, login, password, chanel, stream)
	codec = CodecContext.create('h264', 'r')
	now = datetime.now()
	data = b''
	print(client.time())
	while True:
		while True:
			if reader.readable():
				if chunk := reader.read(1024):
					data += chunk
				if len(chunk) < 1024:
					break
		if len(data) > 0:
			frame = nan
			nodata = False
			try:
				packet = Packet(data)
				frame = codec.decode(packet)
			except:
				nodata = True
			if nodata == False and len(frame) > 0:
				imgByteArr = io.BytesIO()
				frame[0].to_image().save(imgByteArr, format='jpeg', quality=50, optimize=True)
				imgByteArr.seek(0)
				return imgByteArr
			if (datetime.now() - now).seconds > 10:
				print(client.time())
				now = datetime.now()

def get_reader(address, port, login, password, chanel, stream):
	remote = (address, port)
	client = DVRIPClient(Socket(AF_INET, SOCK_STREAM))
	client.connect(remote, login, password)
	sock = Socket(AF_INET, SOCK_STREAM)
	sock.connect(remote)
	if stream == 0:
		stream = Stream.SD
	else:
		stream = Stream.HD	
	reader = client.monitor(sock, chanel, stream)
	return (client, reader)

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)