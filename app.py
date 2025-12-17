from flask import Flask, request, render_template
from sbox_core import generate_sbox
from crypto_tests import *
from encryption import *

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        matrix = request.form["matrix"]
        plaintext = request.form["plaintext"]

        sbox = generate_sbox(matrix)
        key = generate_key()

        ciphertext = encrypt(plaintext, sbox, key)
        decrypted = decrypt(ciphertext, sbox, key)

        result = {
            "NL": nonlinearity(sbox),
            "SAC": sac(sbox),
            "LAP": lap(sbox),
            "DAP": dap(sbox),
            "DU": differential_uniformity(sbox),
            "AD": algebraic_degree(sbox),
            "TO": transparency_order(sbox),
            "CI": correlation_immunity(sbox),
            "Ciphertext": ciphertext.hex(),
            "Decrypted": decrypted
        }

    return render_template(
        "index.html",
        matrices=["K4", "K44", "K81", "K111", "K128"],
        result=result
    )

if __name__ == "__main__":
    app.run(debug=True)
