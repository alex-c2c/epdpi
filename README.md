# Setup Guide

1. Run `sudo raspi-config` and turn on SPI interface
2. Run `sudo install python3-redis python3-dotenv python3-pil`
3. Create a new file `<epdpi_root>/.env` with the following environment variables
``` bash
REDIS_PASSWORD=<your_redis_password>
REDIS_HOST=<your_redis_url>
REDIS_PORT=<your_redis_port>
IS_RASPBERRYPI=1
```
4. Create a new file `/lib/systemd/system/epdpi.service` with the following content
```
[Unit]
Description=EPD Pi
After=multi-user.target

[Service]
Type=simple
Restart=on-abort
ExecStart=/usr/bin/python <path_to_epdpi_dir>/src/main.py

[Install]
WantedBy=multi-user.target
```
5. Run `sudo systemctl enable epdpi.service`
6. Run `sudo systemctl start epdpi.service`
