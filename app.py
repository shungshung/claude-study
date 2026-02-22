from flask import Flask, request, Response, render_template, stream_with_context
from config import Config
from services.okr_service import generate_okr_stream

app = Flask(__name__)
app.config.from_object(Config)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate-okr", methods=["POST"])
def generate_okr():
    payload = request.get_json(force=True)
    business_description = (payload.get("business_description") or "").strip()
    rough_goals = (payload.get("rough_goals") or "").strip()
    time_period = (payload.get("time_period") or "").strip()

    if not business_description or not rough_goals:
        return {"error": "사업 설명과 목표를 모두 입력해주세요."}, 400

    def event_stream():
        yield from generate_okr_stream(
            business_description=business_description,
            rough_goals=rough_goals,
            time_period=time_period,
        )

    return Response(
        stream_with_context(event_stream()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    app.run(debug=Config.DEBUG, threaded=True)
