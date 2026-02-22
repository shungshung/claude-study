import json
import re
import anthropic
from config import Config

client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """당신은 세계적인 수준의 OKR(Objectives and Key Results) 전문 컨설턴트입니다.
한국 중소기업 및 스타트업의 경영자와 관리자를 위해 실용적이고 측정 가능한 OKR을 작성합니다.

<role>
당신의 역할:
- 사업 설명과 목표를 분석하여 전략적으로 정렬된 OKR을 생성합니다.
- 한국 비즈니스 환경과 문화적 맥락을 이해하고 반영합니다.
- 야심차되 현실적인 목표를 설정합니다 (목표 달성 가능성 60-70% 수준).
</role>

<okr_principles>
좋은 OKR의 원칙:
1. Objective(목표): 질적이고 영감을 주는 방향. 숫자 없음. 짧고 명확함 (15자 이내 권장).
2. Key Result(핵심 결과): 반드시 측정 가능한 숫자 포함. 동사로 시작. 결과 중심 (활동이 아님).
3. KR은 목표당 2-5개. 각 KR은 독립적으로 진행 상황을 추적 가능해야 함.
4. KR은 서로 상호보완적이어야 하며 하나의 Objective를 다각도로 측정해야 함.
</okr_principles>

<output_format>
반드시 다음 JSON 스키마를 정확히 따르세요. JSON 외의 텍스트는 절대 출력하지 마세요.

{
  "period": "기간 (예: 2025년 1분기)",
  "summary": "이 OKR 세트의 핵심 전략 방향을 1-2문장으로 설명",
  "objectives": [
    {
      "id": "O1",
      "title": "목표 제목 (질적, 영감을 주는 문장)",
      "rationale": "이 목표를 선택한 이유 (1-2문장)",
      "key_results": [
        {
          "id": "O1-KR1",
          "title": "핵심 결과 (측정 가능한 숫자 포함, 동사로 시작)",
          "metric_type": "number|percentage|currency|boolean",
          "baseline": "현재 값 또는 추정 시작값 (모를 경우 알 수 없음)",
          "target": "목표 값",
          "unit": "단위 (예: 명, %, 만원, 건)",
          "measurement_method": "어떻게 측정할 것인지 (1문장)"
        }
      ]
    }
  ],
  "implementation_tips": [
    "실행 팁 1",
    "실행 팁 2"
  ]
}
</output_format>

<constraints>
- Objective 수: 최소 1개, 최대 3개
- Key Result 수: Objective당 최소 2개, 최대 5개
- 모든 Key Result에는 반드시 숫자(target)가 포함되어야 합니다
- 응답 언어: 한국어 (period, id, metric_type 필드 제외)
- JSON 외의 텍스트(인사말, 설명, 마크다운 코드 펜스 등) 출력 금지
</constraints>

<example>
입력:
- 사업: 서울 강남구의 30대 여성 타겟 프리미엄 네일샵
- 목표: 단골 고객 늘리고 SNS 마케팅 강화
- 기간: 2025년 2분기

출력:
{
  "period": "2025년 2분기 (4월-6월)",
  "summary": "재방문율 중심의 충성 고객 기반을 구축하고, SNS 채널을 활성화하여 신규 고객 유입 경로를 다각화합니다.",
  "objectives": [
    {
      "id": "O1",
      "title": "충성 고객이 자연스럽게 돌아오는 네일샵을 만든다",
      "rationale": "신규 고객 유치 비용은 재방문 고객 유지 비용의 5배입니다. 재방문율 향상이 수익성 개선의 핵심입니다.",
      "key_results": [
        {
          "id": "O1-KR1",
          "title": "재방문 고객 비율을 현재 35%에서 55%로 높인다",
          "metric_type": "percentage",
          "baseline": "35",
          "target": "55",
          "unit": "%",
          "measurement_method": "예약 시스템에서 월별 신규/재방문 고객 수를 집계"
        },
        {
          "id": "O1-KR2",
          "title": "멤버십 프로그램 가입자를 0명에서 100명으로 늘린다",
          "metric_type": "number",
          "baseline": "0",
          "target": "100",
          "unit": "명",
          "measurement_method": "멤버십 카드 발급 수 또는 CRM 등록 수 집계"
        }
      ]
    },
    {
      "id": "O2",
      "title": "SNS를 통해 강남 네일샵의 대명사로 자리잡는다",
      "rationale": "30대 여성 타겟 고객의 주요 정보 탐색 채널은 인스타그램입니다. SNS 가시성이 신규 고객 유입의 핵심 레버입니다.",
      "key_results": [
        {
          "id": "O2-KR1",
          "title": "인스타그램 팔로워를 현재 800명에서 2,000명으로 늘린다",
          "metric_type": "number",
          "baseline": "800",
          "target": "2000",
          "unit": "명",
          "measurement_method": "인스타그램 인사이트에서 월말 팔로워 수 기록"
        },
        {
          "id": "O2-KR2",
          "title": "SNS를 통한 신규 예약 건수를 월 5건에서 30건으로 늘린다",
          "metric_type": "number",
          "baseline": "5",
          "target": "30",
          "unit": "건/월",
          "measurement_method": "예약 시 유입 경로 질문 또는 인스타그램 DM 예약 수 집계"
        }
      ]
    }
  ],
  "implementation_tips": [
    "매주 월요일 30분: 다음 주 SNS 콘텐츠 3개 미리 촬영 및 예약 포스팅",
    "서비스 완료 후 고객에게 멤버십 카드 안내 및 인스타그램 태그 요청"
  ]
}
</example>"""


def build_user_message(business_description: str, rough_goals: str, time_period: str) -> str:
    period_line = f"- 기간: {time_period}" if time_period else "- 기간: 명시되지 않음 (분기 단위로 가정)"
    return f"""다음 정보를 바탕으로 OKR을 생성해주세요:

- 사업 설명: {business_description}
- 대략의 목표: {rough_goals}
{period_line}

반드시 JSON 형식으로만 응답하세요."""


def extract_json_from_text(text: str) -> dict:
    """3단계 폴백으로 Claude 응답에서 JSON을 추출한다."""
    # 1. 직접 파싱
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # 2. 마크다운 코드 펜스 (```json ... ```)
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence_match:
        try:
            return json.loads(fence_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # 3. 가장 바깥쪽 { } 블록
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    return {"error": "JSON 파싱에 실패했습니다.", "raw": text}


def generate_okr_stream(business_description: str, rough_goals: str, time_period: str):
    """SSE 형식의 문자열을 yield하는 제너레이터."""
    accumulated_text = ""
    user_message = build_user_message(business_description, rough_goals, time_period)

    try:
        with client.messages.stream(
            model=Config.CLAUDE_MODEL,
            max_tokens=Config.MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        ) as stream:
            for text_chunk in stream.text_stream:
                accumulated_text += text_chunk
                payload = json.dumps({"type": "chunk", "text": text_chunk}, ensure_ascii=False)
                yield f"data: {payload}\n\n"

        okr_data = extract_json_from_text(accumulated_text)
        done_payload = json.dumps({"type": "done", "okr": okr_data}, ensure_ascii=False)
        yield f"data: {done_payload}\n\n"

    except anthropic.APIConnectionError:
        error_payload = json.dumps(
            {"type": "error", "message": "API 서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요."},
            ensure_ascii=False,
        )
        yield f"data: {error_payload}\n\n"
    except anthropic.AuthenticationError:
        error_payload = json.dumps(
            {"type": "error", "message": "API 키가 유효하지 않습니다. 설정을 확인해주세요."},
            ensure_ascii=False,
        )
        yield f"data: {error_payload}\n\n"
    except anthropic.RateLimitError:
        error_payload = json.dumps(
            {"type": "error", "message": "요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요."},
            ensure_ascii=False,
        )
        yield f"data: {error_payload}\n\n"
    except Exception as e:
        error_payload = json.dumps(
            {"type": "error", "message": f"오류가 발생했습니다: {str(e)}"},
            ensure_ascii=False,
        )
        yield f"data: {error_payload}\n\n"
