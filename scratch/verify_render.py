import urllib.request

def verify():
    print("Verificando Modo Evaluado...")
    try:
        url_evaluado = "http://127.0.0.1:5000/evaluado/etapa2/e1"
        req = urllib.request.Request(url_evaluado)
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            
            # Check for Aurelio Méndez (our new caso clínico)
            if "Aurelio" in html:
                print("[OK] Caso clínico de Aurelio Méndez detectado en /evaluado/etapa2/e1")
            else:
                print("[ERROR] Caso clínico de Aurelio Méndez NO detectado")
                
            # Check for the chest X-ray image render
            if "/static/ejemplos/rx_torax.png" in html:
                print("[OK] Imagen radiografía de tórax (rx_torax.png) detectada y renderizada en HTML")
            else:
                print("[ERROR] Imagen rx_torax.png NO detectada")
                
            # Check for the safe filter (make sure it's not escaped)
            if "&lt;p&gt;&lt;strong&gt;" in html:
                print("[ERROR] HTML clínico parece estar ESCAPADO (filtro |safe falló o falta)")
            else:
                print("[OK] HTML clínico renderizado directamente (filtro |safe funcionando)")
    except Exception as e:
        print("[ERROR] Failed to contact /evaluado/etapa2/e1:", e)
        
    print("\nVerificando Dashboard Master...")
    try:
        url_master = "http://127.0.0.1:5000/"
        req = urllib.request.Request(url_master)
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            
            # Check for Camila Ortega Reyes (our new Grupo 3 student)
            if "Camila Ortega Reyes" in html:
                print("[OK] Alumna Camila Ortega Reyes de Grupo 3 detectada en el Dashboard")
            else:
                print("[ERROR] Alumna Camila Ortega Reyes NO detectada")
                
            # Check for the Popover comments (Mateo San Martín comment)
            if "impecable de auscultaci" in html or "auscultación pulmonar" in html:
                print("[OK] Comentario de evaluación cualitativo detectado en el HTML del Dashboard")
            else:
                print("[ERROR] Comentario de auscultación pulmonar NO detectado")
    except Exception as e:
        print("[ERROR] Failed to contact /:", e)

if __name__ == '__main__':
    verify()
