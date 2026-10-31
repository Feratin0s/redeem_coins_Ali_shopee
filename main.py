#uvicorn main:app --host 0.0.0.0 --port 8000
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, Query, Header
import uiautomator2 as u2
from app.coinsAli import redeem
from app.buyshopee import buy
import logging
import time
from app.coinsshopee import redeem_shopee
from app.debug import debug

d = u2.connect()

d.screen_on()
d.unlock()    

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Conecta ao Xiaomi
d = u2.connect()

#d(text="Entrar").click()               # acha pelo texto e clica

#d.press("home")

#d.screenshot("tela.png")
def wake():
    try:
        #d.screen_on()
        #d.unlock()
        logger.info("waked")
    except Exception:
        logger.exception("Erro ao despertar o dispositivo")
        debug(d, nome="wake_error")
        raise

def close_apks():
    try:
        d.press("home")
        d.press("recent")
        time.sleep(1)
        #d.screenshot("tela.png")
        #xml = d.dump_hierarchy()
        #print(xml)
        if d(resourceId="com.miui.home:id/clearAnimView").exists:
            d(resourceId="com.miui.home:id/clearAnimView").click()
        time.sleep(2)
    except Exception:
        logger.exception("Erro ao fechar aplicativos")
        debug(d, nome="close_apks_error")
        raise


def execute_redeem():
    try:
        logger.info("Iniciando resgate de moedas...")

        wake()
        close_apks()

        redeem(d)

        logger.info("Resgate finalizado!")

    except Exception:
        logger.exception("Erro durante o resgate")
        debug(d, nome="execute_redeem_error")
        raise

def execute_coin_shopee():
    try:
        logger.info("Iniciando resgate de moedas...")

        wake()
        close_apks()

        redeem_shopee(d)

        logger.info("Resgate finalizado!")

    except Exception:
        logger.exception("Erro durante o resgate")
        debug(d, nome="execute_coin_shopee_error")
        raise

def execute_buy_shopee():
    try:
        logger.info("Iniciando compras na shopee")

        wake()
        close_apks()

        buy(d)
    except Exception:
        logger.exception("Erro ao comprar na Shopee")
        debug(d, nome="execute_buy_shopee_error")
        raise


@app.post("/aliexpress/coin")
async def coin_redeem_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(execute_redeem)
        return { 'status': 'success'}
    except Exception:
        logger.exception("Erro ao agendar resgate do AliExpress")
        debug(d, nome="coin_redeem_webhook_error")
        raise

@app.post("/shopee/buy")
async def shopee_buy_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(execute_buy_shopee)
        return { 'status': 'success'}
    except Exception:
        logger.exception("Erro ao agendar compra na Shopee")
        debug(d, nome="shopee_buy_webhook_error")
        raise

@app.post("/shopee/coin")
async def shopee_redeem_coin_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(execute_coin_shopee)
        return { 'status': 'success'}
    except Exception:
        logger.exception("Erro ao agendar resgate de moedas da Shopee")
        debug(d, nome="shopee_redeem_coin_webhook_error")
        raise

@app.post("/get/xml")
async def phone_get_xml(request: Request, background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(get_xml)
        return { 'status': 'success'}
    except Exception:
        logger.exception("Erro ao agendar captura do XML")
        debug(d, nome="phone_get_xml_error")
        raise

def get_xml():
    try:
        xml = d.dump_hierarchy()
        print(xml)
        d.screenshot("tela.png")
    except Exception:
        logger.exception("Erro ao capturar XML do dispositivo")
        debug(d, nome="get_xml_error")
        raise


@app.get("/health")
async def health():
    try:
        return {
            "status": "online",
            "device": d.device_info
        }
    except Exception:
        logger.exception("Erro ao consultar estado do dispositivo")
        debug(d, nome="health_error")
        raise

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