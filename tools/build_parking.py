"""전국주차장정보표준데이터(공공데이터포털) → 앱용 위치별 작은 JSON 파일

사용법:  python3 tools/build_parking.py <다운로드한 .xls 또는 .csv> parking
결과:    parking/index.json  (기준일, 개수, 타일 목록)
         parking/<위도칸>_<경도칸>.json  (0.2도 칸마다 주차장 목록)

한 줄 형식 (앱 index.html 의 PK_ 상수와 순서가 같아야 함)
 0 이름, 1 구분(공영/민영), 2 유형(노상/노외/부설), 3 주소, 4 주차면수, 5 운영요일,
 6 평일시간, 7 토요일시간, 8 공휴일시간, 9 요금정보(무료/유료/혼합),
 10 기본시간(분), 11 기본요금, 12 추가단위시간(분), 13 추가단위요금, 14 1일주차권요금, 15 월정기권요금,
 16 결제방법, 17 특기사항, 18 관리기관, 19 전화, 20 위도, 21 경도, 22 데이터기준일
"""
import json, math, os, sys
import pandas as pd

TILE = 0.2  # 도 단위 칸 크기 (약 22km)


def read(path):
    if path.lower().endswith('.csv'):
        raw = pd.read_csv(path, dtype=str, header=None)
    else:
        raw = pd.read_excel(path, dtype=str, header=None)
    # 제목 줄 찾기 ('주차장명'이 들어 있는 줄)
    hdr = next(i for i in range(10) if '주차장명' in [str(x).strip() for x in raw.iloc[i].tolist()])
    df = raw.iloc[hdr + 1:].copy()
    df.columns = [str(c).strip() for c in raw.iloc[hdr].tolist()]
    return df


def num(v):
    try:
        f = float(str(v).replace(',', '').strip())
        return int(f) if f == int(f) else f
    except Exception:
        return None


def s(v):
    v = '' if v is None else str(v).strip()
    return '' if v.lower() == 'nan' else v


def hours(a, b):
    a, b = s(a), s(b)
    return f'{a}-{b}' if a or b else ''


def main(src, out):
    df = read(src)
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.endswith('.json'):
            os.remove(os.path.join(out, f))
    tiles, n, dates = {}, 0, set()
    for _, r in df.iterrows():
        lat, lng = num(r.get('위도')), num(r.get('경도'))
        if not lat or not lng or not (33 < lat < 39.5 and 124 < lng < 132):
            continue
        row = [
            s(r.get('주차장명')), s(r.get('주차장구분')), s(r.get('주차장유형')),
            s(r.get('소재지도로명주소')) or s(r.get('소재지지번주소')), num(r.get('주차구획수')), s(r.get('운영요일')),
            hours(r.get('평일운영시작시각'), r.get('평일운영종료시각')),
            hours(r.get('토요일운영시작시각'), r.get('토요일운영종료시각')),
            hours(r.get('공휴일운영시작시각'), r.get('공휴일운영종료시각')),
            s(r.get('요금정보')),
            num(r.get('주차기본시간')), num(r.get('주차기본요금')), num(r.get('추가단위시간')), num(r.get('추가단위요금')),
            num(r.get('1일주차권요금')), num(r.get('월정기권요금')),
            s(r.get('결제방법')), s(r.get('특기사항')), s(r.get('관리기관명')), s(r.get('전화번호')),
            round(lat, 6), round(lng, 6), s(r.get('데이터기준일자')),
        ]
        key = f'{math.floor(lat / TILE)}_{math.floor(lng / TILE)}'
        tiles.setdefault(key, []).append(row)
        dates.add(row[22])
        n += 1
    for k, rows in tiles.items():
        with open(os.path.join(out, k + '.json'), 'w', encoding='utf-8') as f:
            json.dump(rows, f, ensure_ascii=False, separators=(',', ':'))
    latest = max((d for d in dates if d), default='')
    with open(os.path.join(out, 'index.json'), 'w', encoding='utf-8') as f:
        json.dump({'source': '공공데이터포털 전국주차장정보표준데이터', 'latest': latest, 'count': n,
                   'tile': TILE, 'tiles': sorted(tiles)}, f, ensure_ascii=False)
    print('주차장', n, '곳, 파일', len(tiles), '개, 최신 기준일', latest)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'parking')
