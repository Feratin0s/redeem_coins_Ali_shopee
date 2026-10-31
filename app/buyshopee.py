import logging
import time
import re
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def buy(d):
    try:
        d.app_start("com.shopee.br") 
        d(resourceId="com.shopee.br:id/cart_btn").wait(timeout=10)
        d(resourceId="com.shopee.br:id/cart_btn").click()
        d(resourceId="buttonCheckBoxNotChecked").wait(timeout=10)
        d(resourceId="buttonCheckBoxNotChecked").click()
        time.sleep(0.5)
        botao = d(textMatches=r"Continuar \(\d+\)")
        if botao.exists:
            botao.click()
        d(text="Selecione ou insira o código", instance=1).wait(timeout=10)
        d(text="Selecione ou insira o código", instance=1).click()
        
        #--> Insere aqui o código do cupom ----------------------

        d(resourceId="btnOkVoucherSelectionSubmitSection").wait(timeout=10)
        d(resourceId="btnOkVoucherSelectionSubmitSection").click()
        d(resourceId="labelRedeemCoins").wait(timeout=10)
        d(resourceId="labelRedeemCoins").click()
        d(scrollable=True).scroll.vert.forward()
        time.sleep(1)
        d(resourceId="paymentMethodRow", instance=1).wait(timeout=10)
        d(resourceId="paymentMethodRow", instance=1).click()

        card = os.getenv('CARD_ABREVIATION')
        
        d(text=card).wait(timeout=10)
        d(text=card).click()
        time.sleep(1)
        options = d(className="android.widget.TextView")
        installments(d)
        d(text="CONFIRMAR").wait(timeout=10)
        d(text="CONFIRMAR").click()
        d(resourceId="buttonPlaceOrder").wait(timeout=10)
        #d(resourceId="buttonPlaceOrder").click()
        time.sleep(5)
        d.press("home") #---> Termina
        #xml = d.dump_hierarchy()
        #print(xml)
    except Exception as e:
        logger.exception("Erro ao efetuar compra na Shopee - {e}")

def brl_to_float(txt: str) -> float:
    # "R$1.234,56" -> 1234.56
    return float(txt.replace("R$", "").replace(".", "").replace(",", ".").strip())

def parse_bounds(b: str):
    # "[121,1209][806,1253]" -> centro (x, y)
    x1, y1, x2, y2 = map(int, re.findall(r"\d+", b))
    return (x1 + x2) // 2, (y1 + y2) // 2

def installments(d, tolerancia=0.05, max_parcelas=None):
    padrao = re.compile(r"^(\d+)x\s*R\$\s*([\d.,]+)$")

    root = ET.fromstring(d.dump_hierarchy())   # 1 única chamada ao celular

    opcoes = []  # (parcelas, valor_parcela, (x, y))
    for node in root.iter("node"):
        texto = (node.get("text") or "").strip()
        m = padrao.match(texto)
        if m:
            opcoes.append((
                int(m.group(1)),
                brl_to_float(m.group(2)),
                parse_bounds(node.get("bounds")),
            ))

    a_vista = next(((v, pos) for p, v, pos in opcoes if p == 1), None)
    if a_vista is None:
        logger.warning("Opção 1x não encontrada")
        return None
    valor_a_vista, pos_a_vista = a_vista

    sem_juros = [
        (p, pos) for p, v, pos in opcoes
        if p > 1
        and abs(p * v - valor_a_vista) <= tolerancia
        and (max_parcelas is None or p <= max_parcelas)
    ]

    if sem_juros:
        p, pos = max(sem_juros, key=lambda x: x[0])
        logger.info(f"Clicando em {p}x sem juros")
        d.click(*pos)
        return p

    logger.info("Nenhuma opção sem juros; selecionando à vista (1x)")
    d.click(*pos_a_vista)
    return 1