from flask import (
    Flask,
    request,
    render_template,
    send_file,
    after_this_request
)
from sbox_core import generate_sbox
from crypto_tests import *
from encryption import *
from export import export_to_excel

import os
import atexit

app = Flask(__name__)

# ================= CONFIG =================
EXPORT_FILE = "aes_export.xlsx"

# ================= CLEANUP FUNCTION =================
def cleanup_export_file():
    if os.path.exists(EXPORT_FILE):
        try:
            os.remove(EXPORT_FILE)
        except Exception as e:
            print("Cleanup error:", e)

# Cleanup at app start
cleanup_export_file()

# Cleanup at normal app exit
atexit.register(cleanup_export_file)

# ================= ROUTES =================
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    sbox_table = None
    inv_sbox_table = None
    enc_trace = None
    dec_trace = None

    if request.method == "POST":
        matrix = request.form["matrix"]
        plaintext = request.form["plaintext"]

        # ---- 1. Generate S-box ----
        sbox = generate_sbox(matrix)

        # ---- 2. Generate Inverse S-box ----
        inv_sbox = [0] * 256
        for i in range(256):
            inv_sbox[sbox[i]] = i

        # ---- 3. Key & Encryption ----
        key = generate_key()
        pt = plaintext.encode().ljust(16, b'\x00')

        # Encrypt & Decrypt with Trace
        ciphertext, enc_trace = aes_encrypt_trace(pt, key, sbox)
        decrypted, dec_trace = aes_decrypt_trace(ciphertext, key, sbox)

        # ---- 4. Build Tables (16x16) for Frontend ----
        sbox_table = [
            [f"{sbox[r * 16 + c]:02X}" for c in range(16)]
            for r in range(16)
        ]
        
        inv_sbox_table = [
            [f"{inv_sbox[r * 16 + c]:02X}" for c in range(16)]
            for r in range(16)
        ]

        # ---- 5. Cryptographic Tests ----
        crypto_result = {
            "NL": nonlinearity(sbox),
            "SAC": sac(sbox),
            "BIC_NL": bic_nl(sbox),
            "BIC_SAC": bic_sac(sbox),
            "LAP": lap(sbox),
            "DAP": dap(sbox),
            "DU": differential_uniformity(sbox),
            "AD": algebraic_degree(sbox),
            "TO": transparency_order(sbox),
            "CI": correlation_immunity(sbox),
        }

        # ---- 6. Result Object ----
        result = {
            "Key": key.hex(),
            "Plaintext": plaintext,
            "Ciphertext": ciphertext.hex(),
            "Decrypted": decrypted.rstrip(b"\x00").decode(errors="ignore"),
            **crypto_result
        }

        # ---- 7. Export Excel ----
        export_to_excel(
            filename=EXPORT_FILE,
            affine_matrix=matrix,
            key_hex=key.hex(),
            plaintext=plaintext,
            ciphertext_hex=ciphertext.hex(),
            decrypted=result["Decrypted"],
            sbox=sbox,
            inv_sbox=inv_sbox,
            enc_trace=enc_trace,
            dec_trace=dec_trace,
            crypto_result=crypto_result
        )

    return render_template(
        "index.html",
        matrices=["K4", "K44", "K81", "K111", "K128"],
        result=result,
        sbox_table=sbox_table,
        inv_sbox_table=inv_sbox_table,
        enc_trace=enc_trace,
        dec_trace=dec_trace
    )

@app.route("/download")
def download_excel():
    if not os.path.exists(EXPORT_FILE):
        return "File not found", 404

    @after_this_request
    def remove_file(response):
        try:
            os.remove(EXPORT_FILE)
        except Exception as e:
            print("Cleanup error:", e)
        return response

    return send_file(
        EXPORT_FILE,
        as_attachment=True,
        download_name="AES_Affine_Sbox_Result.xlsx"
    )

# ================= MAIN =================
if __name__ == "__main__":
    app.run(debug=True)