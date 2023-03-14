pip install -r requirements.txt

///////////////////////////////
https://code.luasoftware.com/tutorials/linux/auto-start-python-script-on-boot-systemd/
"/etc/systemd/system/dvr2mjpeg.service"

[Unit]
After=network.service
Description=dvr2mjpeg

[Service]
Type=simple
WorkingDirectory=/home/cray/dvr2mjpeg
ExecStart=python3 main.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target

sudo systemctl enable dvr2mjpeg.service
sudo systemctl start dvr2mjpeg.service
///////////////////////////////