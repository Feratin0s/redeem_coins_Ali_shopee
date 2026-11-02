import logging
import time
from app.debug import debug

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PKG = "com.alibaba.aliexpresshd"

def redeem(d):
    try:
        d.app_start("com.alibaba.aliexpresshd") #Aliexpress
        time.sleep(4)
        fechar_popup_webview(d)
        d(text="Moedas").wait(timeout=10)
        d(text="Moedas").click()
        time.sleep(20)
        d.click(850, 1040)
        time.sleep(10)
        d.press("home")
        #xml = d.dump_hierarchy()
        #print(xml)
    except Exception as e:
        logger.exception(e)
        debug(d, nome="redeem_aliexpress_error")
        raise

def fechar_overlays(d, timeout=8):
    try:
        # 1) Splash: botão "Pular em N"
        pular = d(resourceId=f"{PKG}:id/skip_message_v3")
        if pular.wait(timeout=3):
            logger.info("Fechando splash")
            pular.click()
            # espera o splash sumir
            d(resourceId=f"{PKG}:id/rl_screen_v3").wait_gone(timeout=timeout)

        # 2) Popup de promoção (se aparecer)
        fechar = d(resourceId=f"{PKG}:id/iv_close_poplayer_image")
        if fechar.wait(timeout=3):
            logger.info("Fechando popup de promoção")
            fechar.click()
            fechar.wait_gone(timeout=5)
    except Exception as e:
        logger.exception(e)
        debug(d, nome="fechar_overlays_error")
        raise

def fechar_popup_webview(d):
    try:
        wv = d(className="com.uc.webview.export.WebView")
        if wv.exists:
            d.click(0.5, 0.676)
            time.sleep(0.5)
    except Exception as e:
        logger.exception(e)
        debug(d, nome="fechar_popup_webview_error")
        raise