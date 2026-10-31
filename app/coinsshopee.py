import logging
import time
from app.debug import debug

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def redeem_shopee(d):
    try:
        d.app_start("com.shopee.br")
        d(text="Moedas").wait(timeout=10)
        d(text="Moedas").click()
        d(textContains="Faça o check-in").wait(timeout=10)
        d(textContains="Faça o check-in").click()
        d(resourceId="buttonClosePopup").wait(timeout=10)
        d(resourceId="buttonClosePopup").click
        d.press("home")
        time.sleep(2)
        #xml = d.dump_hierarchy()
        #logger.info(xml)
    except Exception:
        logging.getLogger(__name__).exception("Erro ao resgatar moedas na Shopee")
        debug(d, nome="redeem_shopee_error")
        raise