ception as e:
        raise HTTPException(502,f"No se pudo actualizar el precio: {str(e)[:160]}")
