import httpx
import json

class LLMClient:

   timeout = httpx.Timeout(
        connect=10.0,
        read=300.0,   
        write=10.0,
        pool=10.0
    )
   
   async def generate(self, prompt: str) -> dict:
       
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                "model": "gemma3:4b",
                "prompt": prompt,
                "stream": False,
                "format": "json"
                },  
                timeout=self.timeout
            )

            response.raise_for_status()
            data = response.json()
            print("RESPUESTA CRUDA:", data)
            print("TEXTO DEL MODELO:", data["response"])

            # 👇 El modelo devuelve texto, así que lo parseamos
            raw_text = data["response"]
            
            try:
                response = await client.post("http://localhost:11434/api/generate")
            except httpx.ReadTimeout:
                raise TimeoutError("El modelo tardó demasiado en responder")
            
            try:
                return data["response"]
            except json.JSONDecodeError:
                raise ValueError("La IA no devolvió un JSON válido")
            


# 👇 instancia exportada
llm_client = LLMClient()