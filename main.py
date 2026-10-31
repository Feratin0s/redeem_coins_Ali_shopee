#uvicorn main:app --host 0.0.0.0 --port 8000
from contextlib import asynccontextmanager
import logging
import time

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
import uiautomator2 as u2

from app.buyshopee import buy
from app.coinsshopee import redeem_shopee
from app.coinsAli import redeem
from app.debug import debug

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

d = None


def get_device():
    global d

    if d is not None:
        return d

    try:
        d = u2.connect()
        d.screen_on()
        d.unlock()
        logger.info("Dispositivo conectado com sucesso")
        return d
    except Exception as exc:
        logger.exception("Erro ao conectar com o dispositivo")
        raise HTTPException(
            status_code=503,
            detail=f"Não foi possível conectar ao dispositivo Xiaomi: {exc}",
        ) from exc


@asynccontextmanager
async def lifespan(app: FastAPI):
    global d

    try:
        d = u2.connect()
        d.screen_on()
        d.unlock()
        logger.info("App iniciado com dispositivo conectado")
    except Exception as exc:
        d = None
        logger.warning("App iniciado sem dispositivo conectado: %s", exc)

    yield

    d = None


app = FastAPI(lifespan=lifespan)

#d(text="Entrar").click()               # acha pelo texto e clica

#d.press("home")

#d.screenshot("tela.png")
def wake():
    device = get_device()
    try:
        device.screen_on()
        device.unlock()
        #logger.info("waked")
    except Exception:
        logger.exception("Erro ao despertar o dispositivo")
        debug(device, nome="wake_error")
        raise


def close_apks():
    device = get_device()
    try:
        device.press("home")
        device.press("recent")
        time.sleep(1)
        if device(resourceId="com.miui.home:id/clearAnimView").exists:
            device(resourceId="com.miui.home:id/clearAnimView").click()
        time.sleep(2)
    except Exception:
        logger.exception("Erro ao fechar aplicativos")
        debug(device, nome="close_apks_error")
        raise


def execute_redeem():
    device = get_device()
    try:
        logger.info("Iniciando resgate de moedas...")

        wake()
        close_apks()

        redeem(device)

        logger.info("Resgate finalizado!")

    except Exception:
        logger.exception("Erro durante o resgate")
        debug(device, nome="execute_redeem_error")
        raise


def execute_coin_shopee():
    device = get_device()
    try:
        logger.info("Iniciando resgate de moedas...")

        wake()
        close_apks()

        redeem_shopee(device)

        logger.info("Resgate finalizado!")

    except Exception:
        logger.exception("Erro durante o resgate")
        debug(device, nome="execute_coin_shopee_error")
        raise


def execute_buy_shopee():
    device = get_device()
    try:
        logger.info("Iniciando compras na shopee")

        wake()
        close_apks()

        buy(device)
    except Exception:
        logger.exception("Erro ao comprar na Shopee")
        debug(device, nome="execute_buy_shopee_error")
        raise


@app.post("/aliexpress/coin")
async def coin_redeem_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        get_device()
        background_tasks.add_task(execute_redeem)
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Erro ao agendar resgate do AliExpress")
        debug(d, nome="coin_redeem_webhook_error")
        raise


@app.post("/shopee/buy")
async def shopee_buy_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        get_device()
        background_tasks.add_task(execute_buy_shopee)
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Erro ao agendar compra na Shopee")
        debug(d, nome="shopee_buy_webhook_error")
        raise


@app.post("/shopee/coin")
async def shopee_redeem_coin_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        get_device()
        background_tasks.add_task(execute_coin_shopee)
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Erro ao agendar resgate de moedas da Shopee")
        debug(d, nome="shopee_redeem_coin_webhook_error")
        raise


@app.post("/get/xml")
async def phone_get_xml(request: Request, background_tasks: BackgroundTasks):
    try:
        get_device()
        background_tasks.add_task(get_xml)
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Erro ao agendar captura do XML")
        debug(d, nome="phone_get_xml_error")
        raise


def get_xml():
    device = get_device()
    try:
        xml = device.dump_hierarchy()
        print(xml)
        device.screenshot("tela.png")
    except Exception:
        logger.exception("Erro ao capturar XML do dispositivo")
        debug(device, nome="get_xml_error")
        raise


@app.get("/health")
async def health():
    try:
        device = get_device()
        return {
            "status": "online",
            "device": device.device_info,
        }
    except HTTPException as exc:
        return {
            "status": "error",
            "message": exc.detail,
        }
    except Exception:
        logger.exception("Erro ao consultar estado do dispositivo")
        return {
            "status": "error",
            "message": "Erro ao consultar o estado do dispositivo.",
        }

#d.app_start("com.alibaba.aliexpresshd") #Aliexpress
#d.app_start("com.shopee.br") #Shopee
#xml = d.dump_hierarchy()
#print(d.app_current())
#print(xml)

#d(text="Moedas").click()

#url = "https://www.aliexpress.com/"

#d.shell([
#    "am", "start",
#    "-a", "android.intent.action.VIEW",
#    "-d", url
#])

# Espera até 20 segundos pelo elemento
#if d(text="Resgatar").wait(timeout=20):
#    print("Página carregada!")
#else:
#    print("Tempo esgotado!")