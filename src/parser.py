import re  # [필수] 누락된 라이브러리 추가
import pandas as pd
from pathlib import Path

def parse_raw_logs(data_dir="./data"):
    """
    지정된 폴더의 로그 파일을 읽어 원본 데이터프레임을 반환합니다.
    """
    log_dir = Path(data_dir)
    # 파일이 없으면 빈 리스트 반환 등의 예외처리도 가능하지만, 일단 원본 로직 유지
    [cite_start]files = sorted(log_dir.glob("log_*.txt")) # [cite: 11]

    # [cite_start]정규표현식 컴파일 [cite: 30-31]
    pattern = re.compile(
        r'^(?P<ts>\S+)\s+\[.*?\]\s+IP=(?P<ip>\S+)\s+METHOD=(?P<method>\S+)\s+URI=(?P<uri>\S+)\s+STATUS=(?P<status>\d+)\s+TIME=(?P<time>\d+)ms\s+UA=(?P<ua>.*)$'
    )

    rows = []

    [cite_start]for fp in files: # [cite: 34]
        with open(fp, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                [cite_start]m = pattern.match(line) # [cite: 37]
                if m:
                    [cite_start]rows.append(m.groupdict()) # [cite: 39]

    [cite_start]df = pd.DataFrame(rows) # [cite: 40]
    return df

# 직접 실행했을 때만 테스트하도록 설정
if __name__ == "__main__":
    df = parse_raw_logs()
    print(df.head())
