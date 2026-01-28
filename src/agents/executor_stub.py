from typing import Dict


def run(conn, settings) -> Dict:
    return {
        "status": "desabilitado",
        "mensagem": "Camada de escrita desabilitada. Requer aprovacao explicita via WhatsApp.",
    }
