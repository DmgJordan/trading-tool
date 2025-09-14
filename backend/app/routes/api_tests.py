from fastapi import APIRouter, HTTPException
from ..schemas.user import ApiKeyTest
import httpx
import asyncio

router = APIRouter(prefix="/test", tags=["api-tests"])

@router.post("/hyperliquid")
async def test_hyperliquid_api(api_test: ApiKeyTest):
    """Test the Hyperliquid API connection"""
    try:
        # Test basique de l'API Hyperliquid
        # Ici, nous testons juste la connectivité avec un endpoint simple
        async with httpx.AsyncClient() as client:
            # Exemple d'endpoint de test Hyperliquid
            response = await client.get(
                "https://api.hyperliquid.xyz/info",
                params={"type": "clearinghouseState", "user": "0x0000000000000000000000000000000000000000"},
                timeout=10.0
            )

            if response.status_code == 200:
                return {"status": "success", "message": "Connexion Hyperliquid réussie !"}
            else:
                raise HTTPException(status_code=400, detail="Échec de la connexion Hyperliquid")

    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Timeout lors de la connexion à Hyperliquid")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur de connexion Hyperliquid: {str(e)}")

@router.post("/anthropic")
async def test_anthropic_api(api_test: ApiKeyTest):
    """Test the Anthropic API connection"""
    try:
        # Test basique de l'API Anthropic
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": api_test.api_key,
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": "Test"}]
                },
                timeout=10.0
            )

            if response.status_code == 200:
                return {"status": "success", "message": "Connexion Anthropic réussie !"}
            elif response.status_code == 401:
                raise HTTPException(status_code=401, detail="Clé API Anthropic invalide")
            else:
                raise HTTPException(status_code=400, detail="Échec de la connexion Anthropic")

    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Timeout lors de la connexion à Anthropic")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur de connexion Anthropic: {str(e)}")