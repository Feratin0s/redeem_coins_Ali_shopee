#../logs --> Pasta pra salvar os erros e imagens
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# ../logs relativo ao arquivo do script (e não ao diretório de onde você roda)
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"

def debug(d, nome="bug"):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = LOG_DIR / f"{nome}_{ts}"

    try:
        d.screenshot(str(base.with_suffix(".png")))
        base.with_suffix(".xml").write_text(d.dump_hierarchy(), encoding="utf-8")
        logger.info(f"Debug salvo em {base}.png / .xml")
    except Exception:
        logger.exception("Falha ao salvar debug")