import subprocess
import time
import os
import re

def update_env(url):
    env_path = '.env'
    if not os.path.exists(env_path):
        print(f"Error: {env_path} no existe.")
        return
        
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    tablet_url_line = f"TABLET_URL={url.rstrip('/')}/tablet/\n"
    
    # Check if TABLET_URL already exists in the file
    if re.search(r'^TABLET_URL=.*$', content, re.MULTILINE):
        # Replace the existing line
        content = re.sub(r'^TABLET_URL=.*$', f"TABLET_URL={url.rstrip('/')}/tablet/", content, flags=re.MULTILINE)
        print(f"Modificada línea TABLET_URL existente en .env")
    else:
        # Append to the end
        if not content.endswith('\n'):
            content += '\n'
        content += tablet_url_line
        print(f"Agregada línea TABLET_URL al final de .env")
        
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Archivo .env actualizado con TABLET_URL={url.rstrip('/')}/tablet/")

def start_tunnel():
    print("Iniciando túnel Pinggy SSH en puerto 443 -> local 5000...")
    cmd = [
        "ssh", 
        "-o", "StrictHostKeyChecking=no", 
        "-o", "ServerAliveInterval=15", 
        "-o", "ServerAliveCountMax=3", 
        "-p", "443", 
        "-R", "80:127.0.0.1:5000", 
        "a.pinggy.io"
    ]
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1 # Line buffered
    )
    
    # Read output to find URL
    url = None
    start_time = time.time()
    
    print("Esperando salida de Pinggy...")
    # Read first 30 lines of output to extract URL
    for _ in range(60):
        if time.time() - start_time > 20:
            break
        line = process.stdout.readline()
        if not line:
            # Check stderr if stdout is empty
            err_line = process.stderr.readline()
            if err_line:
                print(f"SSH Stderr: {err_line.strip()}")
            time.sleep(0.5)
            continue
            
        print(f"SSH Stdout: {line.strip()}")
        
        # Check if line contains the HTTPS pinggy free dynamic link
        if "https://" in line and "pinggy-free.link" in line:
            match = re.search(r'(https://[^\s]+)', line)
            if match:
                url = match.group(1)
                break
                
        time.sleep(0.1)
        
    if url:
        print(f"\n[ÉXITO] ¡Túnel Pinggy establecido con éxito!")
        print(f"URL Pública: {url}")
        
        # Update .env file
        update_env(url)
        
        # Save url to scratch/tunnel_url.txt
        os.makedirs("scratch", exist_ok=True)
        with open("scratch/tunnel_url.txt", "w", encoding='utf-8') as f:
            f.write(url + "/tablet/")
            
        print("Túnel activo. Manteniendo proceso abierto para sostener la conexión...")
        # Keep process running
        try:
            while True:
                # Check if process is still running
                if process.poll() is not None:
                    print("El proceso SSH ha finalizado inesperadamente.")
                    break
                time.sleep(5)
        except KeyboardInterrupt:
            print("Cerrando túnel...")
            process.terminate()
    else:
        print("\n[ERROR] No se pudo extraer la URL de la salida de Pinggy.")
        # Print remaining output to help debug
        print("Salida restante:")
        for _ in range(5):
            line = process.stdout.readline()
            if line:
                print(line.strip())
        process.terminate()

if __name__ == '__main__':
    start_tunnel()
