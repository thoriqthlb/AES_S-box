from flask import Flask, request, render_template, send_file, url_for
from sbox_core import generate_sbox
from crypto_tests import *
from encryption import *
from export import export_to_excel
import io  

app = Flask(__name__)

# ================= HELPER LOGIC =================  
def run_aes_logic(matrix_name, plaintext_input):
    # 1. Generate S-box
    sbox = generate_sbox(matrix_name)

    # 2. Generate Inverse S-box
    inv_sbox = [0] * 256
    for i in range(256):
        inv_sbox[sbox[i]] = i

    # 3. Key & Encryption
    key = generate_key()
    pt = plaintext_input.encode().ljust(16, b'\x00')

    # Encrypt & Decrypt
    ciphertext, enc_trace = aes_encrypt_trace(pt, key, sbox)
    decrypted, dec_trace = aes_decrypt_trace(ciphertext, key, sbox)

    # 4. Tables for UI
    sbox_table = [[f"{sbox[r * 16 + c]:02X}" for c in range(16)] for r in range(16)]
    inv_sbox_table = [[f"{inv_sbox[r * 16 + c]:02X}" for c in range(16)] for r in range(16)]

    # 5. Crypto Tests
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

    result = {
        "Key": key.hex(),
        "Plaintext": plaintext_input,
        "Ciphertext": ciphertext.hex(),
        "Decrypted": decrypted.rstrip(b"\x00").decode(errors="ignore"),
        **crypto_result
    }

    return {
        "result": result,
        "sbox": sbox,
        "inv_sbox": inv_sbox,
        "enc_trace": enc_trace,
        "dec_trace": dec_trace,
        "crypto_result": crypto_result,
        "sbox_table": sbox_table,
        "inv_sbox_table": inv_sbox_table
    }

# ================= ROUTES =================
@app.route("/", methods=["GET", "POST"])
def index():
    context = {
        "result": None,
        "sbox_table": None,
        "inv_sbox_table": None,
        "enc_trace": None,
        "dec_trace": None
    }

    if request.method == "POST":
        matrix = request.form.get("matrix")
        plaintext = request.form.get("plaintext")
        
        if matrix and plaintext:
            data = run_aes_logic(matrix, plaintext)
            context.update({
                "result": data["result"],
                "sbox_table": data["sbox_table"],
                "inv_sbox_table": data["inv_sbox_table"],
                "enc_trace": data["enc_trace"],
                "dec_trace": data["dec_trace"]
            })

    return render_template(
        "index.html",
        matrices=["K4", "K44", "K81", "K111", "K128"],
        **context
    )

@app.route("/download")
def download_excel():
    
    matrix = request.args.get("matrix")
    plaintext = request.args.get("plaintext")

    if not matrix or not plaintext:
        return "Missing parameters. Please encrypt first.", 400

 
    data = run_aes_logic(matrix, plaintext)

    
    output = io.BytesIO()

    # Tulis Excel ke Memory
    export_to_excel(
        output_stream=output,
        affine_matrix=matrix,
        key_hex=data["result"]["Key"],
        plaintext=plaintext,
        ciphertext_hex=data["result"]["Ciphertext"],
        decrypted=data["result"]["Decrypted"],
        sbox=data["sbox"],
        inv_sbox=data["inv_sbox"],
        enc_trace=data["enc_trace"],
        dec_trace=data["dec_trace"],
        crypto_result=data["crypto_result"]
    )

    # Reset pointer ke awal file di memory
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name="AES_Encryption_Result.xlsx"
    )

if __name__ == "__main__":
    app.run(debug=True)