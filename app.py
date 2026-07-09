from flask import Flask, request, jsonify
from flask_cors import CORS
from jsonschema import validate, ValidationError
import json

app = Flask(__name__)

CORS(app)


Dummy = '''
{
  "status": "success",
  "user_position": [
    {
      "user_num": 0,
      "x": 3.21,
      "y": 1.42,
      "z": 0.0,
      "confidence": 0.87
    }
  ],
  "timestamp": "2026-06-23T10:30:01+09:00"
}
'''

def load_schema(filepath):
    try:
        # utf-8 인코딩으로 파일을 읽어 파이썬 딕셔너리로 변환
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"스키마 파일을 찾을 수 없습니다: {filepath}")
        raise
    except json.JSONDecodeError as e:
        print(f"스키마 파일의 JSON 형식이 잘못되었습니다: {e}")
        raise

# 서버 시작 시 스키마를 한 번만 메모리에 로드 (매 요청마다 읽으면 성능 저하)
EXPECTED_SCHEMA = load_schema('client_to_Ai_schema.json')


def validate_sensor_data(data):
    if data is None:
        print("요청에 JSON 데이터가 없거나 형식이 잘못되었습니다.")
        return False, "Invalid or missing JSON"
    try:
        # 로드된 EXPECTED_SCHEMA를 사용하여 검증
        validate(instance=data, schema=EXPECTED_SCHEMA)
        return True, None
        
    except ValidationError as e:
        error_msg = f"JSON 스키마 검증 실패: {e.message} (경로: {list(e.path)})"
        print(error_msg)
        return False, e.message
        
    except Exception as e:
        print(f"예기치 못한 검증 에러 발생: {str(e)}")
        return False, "Internal validation error"

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Welcome to the PulseWave AI Server!"}), 200

@app.route('/ai/predict', methods=['POST'])
def predict():
    data = request.get_json(silent=True)

    is_valid, error_detail = validate_sensor_data(data)
    
    if not is_valid:
        return jsonify({
            "status": "error", 
            "message": "Data format validation failed", 
            "details": error_detail
        }), 400

    return jsonify(json.loads(Dummy)), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)