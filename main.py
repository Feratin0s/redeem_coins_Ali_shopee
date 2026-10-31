#uvicorn main:app --host 0.0.0.0 --port 8000

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, Query, Header
import uiautomator2 as u2
from coinsAli import redeem
from buyshopee import buy
import logging
import time

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
    #d.screen_on()
    #d.unlock()
    logger.info("waked")

def close_apks():
    d.press("home")
    d.press("recent")
    time.sleep(1)
    #d.screenshot("tela.png")
    #xml = d.dump_hierarchy()
    #print(xml)
    if d(resourceId="com.miui.home:id/clearAnimView").exists:
        d(resourceId="com.miui.home:id/clearAnimView").click()
    time.sleep(2)


def execute_redeem():
    try:
        logger.info("Iniciando resgate de moedas...")

        wake()
        close_apks()

        redeem(d)

        logger.info("Resgate finalizado!")

    except Exception:
        logger.exception("Erro durante o resgate")

def execute_coin_shopee():
    try:
        logger.info("Iniciando resgate de moedas...")

        wake()
        close_apks()

        logger.info("Resgate finalizado!")

    except Exception:
        logger.exception("Erro durante o resgate")

def execute_buy_shopee():
    try:
        logger.info("Iniciando compras na shopee")

        wake()
        close_apks()

        buy(d)
    except Exception as e:
        logger.exception("Erro ao comprar - {e}")


@app.post("/aliexpress/coin")
async def coin_redeem_webhook(request: Request, background_tasks: BackgroundTasks):
    background_tasks.add_task(execute_redeem)
    return { 'status': 'success'}

@app.post("/shopee/buy")
async def shopee_buy_webhook(request: Request, background_tasks: BackgroundTasks):
    background_tasks.add_task(execute_buy_shopee)
    return { 'status': 'success'}

@app.post("/shopee/coin")
async def shopee_redeem_coin_webhook(request: Request, background_tasks: BackgroundTasks):
    background_tasks.add_task(execute_coin_shopee)
    return { 'status': 'success'}

@app.get("/health")
async def health():
    return {
        "status": "online",
        "device": d.device_info
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