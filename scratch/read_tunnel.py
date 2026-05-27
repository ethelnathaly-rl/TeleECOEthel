import os

def read_info():
    url_file = "scratch/tunnel_url.txt"
    if os.path.exists(url_file):
        with open(url_file, "r", encoding="utf-8") as f:
            print(f"=== TUNNEL URL FILE ===\n{f.read()}")
    else:
        print("El archivo scratch/tunnel_url.txt no existe aún.")
        
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for l in lines:
                if l.startswith("TABLET_URL="):
                    print(f"=== .ENV TABLET_URL ===\n{l.strip()}")
    else:
        print("El archivo .env no existe.")

if __name__ == '__main__':
    read_info()
