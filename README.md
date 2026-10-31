# Reddem coins smartphone automatic

Python backend for automating interactions on a Xiaomi 11T smartphone using `uiautomator2` and a FastAPI API.
If you want to use in another device, please check "d.click(850, 1040)" with bounces based on screen resolution

This project can:

- redeem coins on stores such as Shopee and AliExpress
- automate a Shopee purchase for an item already added to the cart
- open apps, capture screenshots, and inspect the device UI for debugging
- expose endpoints to trigger these actions remotely

## Features

- FastAPI server for webhook-style automation
- `uiautomator2` integration for Android device control
- action endpoints for coin redemption and shopping flows
- device health check and XML/screenshot debugging helpers

## Requirements

- Smartphone connected to the computer via ADB
- USB debugging enabled on the device
- Python environment with the dependencies from `requirements.txt`
- `adb` available in the system PATH

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Connect the device and confirm it is available:

   ```bash
   adb devices
   ```

4. Create a `.env` file with the card information used by the purchase flow:

   ```env
   CVC=123
   CARD_ABREVIATION=*1234
   ```

   These values are examples only; replace them with your own valid details when required by the automation flow.

5. Start the API:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### Docker

You can also run the project with Docker Compose.


```bash
docker compose up --build
```

This starts the FastAPI app on port `8000` and exposes the USB device to the container so ADB can communicate with the phone.
If using docker start on port `3671`

### ADB Server (systemd)

The container connects to an ADB server running on the host. To install it as a service (starts on boot and restarts automatically):

```bash
chmod +x install-adb-service.sh
sudo ./install-adb-service.sh
```

The script is safe to run more than once.

## Available endpoints

- `POST /aliexpress/coin` — start the AliExpress coin redemption flow
- `POST /shopee/coin` — start the Shopee coin redemption flow
- `POST /shopee/buy` — start the Shopee purchase flow
- `GET /health` — check whether the device is responding
- `POST /get/xml` — capture XML and screenshot for debugging

## Notes

This project is intended for personal automation on your own device. Please use it responsibly and ensure you comply with the terms of service of the apps you automate.
