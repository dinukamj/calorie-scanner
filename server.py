import os
import anthropic
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder="public")
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

@app.route("/")
def index():
    return send_from_directory("public", "index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    image_data = data.get("image")  # base64 string, e.g. "data:image/jpeg;base64,..."

    if not image_data:
        return jsonify({"error": "No image provided"}), 400

    # Strip the data URL prefix
    if "," in image_data:
        media_type_part, b64 = image_data.split(",", 1)
        media_type = media_type_part.split(":")[1].split(";")[0]
    else:
        b64 = image_data
        media_type = "image/jpeg"

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            "Identify the food(s) in this image and estimate the calories. "
                            "Be concise. Format your response as:\n\n"
                            "**Food:** <name>\n"
                            "**Calories:** <number> kcal (estimated)\n"
                            "**Serving size:** <description>\n\n"
                            "If multiple foods are visible, list each one, then give a total. "
                            "If you can't identify food, say so briefly."
                        ),
                    },
                ],
            }
        ],
    )

    return jsonify({"result": message.content[0].text})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=False)
