# PhyAugPipe-style Panda-70M Winner Selection Pipeline

이 레포는 **metadata-first** 방식으로 Panda-70M에서 후보를 고르고,
프레임/추론/스코어링을 거쳐 최종 winner를 내보내는 파이프라인입니다.

---

## 0) 진짜로 필요한 순서 (헷갈리지 않게 3단계)

### Step 1. Prompt 필터링 (CSV 만들기)
```bash
python scripts/build_prompt_subset.py \
  --input-csv data/panda70m_meta/train_2m.csv \
  --output-csv data/panda70m_meta/train_2m_sports_30k.csv \
  --max-samples 30000 \
  --seed 42
```

### Step 2. 영상 다운로드 (+ prompt/metadata 매칭 파일)
> 둘 중 하나 선택

#### 2-A) official video2dataset
```bash
python scripts/download_with_video2dataset.py \
  --csv data/panda70m_meta/train_2m_sports_30k.csv \
  --output-folder data/panda70m_subset_v2d \
  --config video2dataset/video2dataset/configs/panda70m.yaml
```
- CSV에 있는 row만 다운로드합니다.

#### 2-B) yt-dlp fallback (clip + prompt sidecar + manifest)
```bash
python scripts/download_videos_subset.py \
  --input-csv data/panda70m_meta/train_2m_sports_30k.csv \
  --raw-video-dir data/videos_raw \
  --clip-dir data/videos \
  --save-prompts-dir data/prompts_txt \
  --save-metadata-dir data/prompts_meta \
  --manifest-jsonl data/videos/download_manifest.jsonl
```
- `data/videos/<sample_id>.mp4`
- `data/prompts_txt/<sample_id>.txt`
- `data/prompts_meta/<sample_id>.json`
- `data/videos/download_manifest.jsonl` (status/경로 매핑)

### Step 3. run_phase로 파이프라인 실행
```bash
# A. 준비 단계 (stage1-2)
python scripts/run_phase.py --phase prepare

# B. data filtering 5단계 (stage3-7)
python scripts/run_phase.py --phase data_filtering_5steps

# C. export (stage8)
python scripts/run_phase.py --phase export
```

### (선택) 네가 원하는 방식: `prepare` 한 번에 "CSV 필터링 -> 다운로드 -> 프레임 추출"
`configs/default.yaml`에서 아래만 켜면 됨:
- `prepare.csv_filter.enabled: true`
- `prepare.video_download.enabled: true` (provider는 현재 `video2dataset`만 지원)

이 모드에서는 `prepare.csv_filter.disable_stage1_filters: true` 기본값으로 인해
stage1에서 중복 필터링을 하지 않습니다.
그리고 다운로드는 stage1 결과(`metadata_records/shortlist.csv`) 기준으로 실행됩니다.
(`yt-dlp` 다운로드는 의도적으로 분리되어 있으므로 별도 스크립트를 사용하세요.)

---

## 1) `run_phase` 순서와 중복 여부

`run_phase`는 의도적으로 분리되어 있고, **출력 아티팩트를 재사용**합니다.

- `prepare`:
  - stage1_prefilter
  - stage2_extract_frames
- `data_filtering_5steps`:
  - 내부적으로 `prepare`를 먼저 보장 호출한 뒤(stage1-2 결과 재사용)
  - stage3_element_parsing
  - stage4_vision_checking
  - stage5_physics_reasoning
  - stage6_scoring
  - stage7_prompt_extending
- `export`:
  - stage8_export만 실행

즉, 순서대로 `prepare -> data_filtering_5steps -> export` 하면 되고,
이미 생성된 파일은 `modes.overwrite: false`일 때 건너뛰므로 불필요한 중복 실행을 줄입니다.

---

## 2) Data Filtering 5단계 입력/출력/역할 (연결 관계)

아래 5단계는 `outputs/<run_name>/` 내부 아티팩트로 서로 연결됩니다.

### Stage3 Element Parsing
- 입력:
  - `metadata_records/shortlist.csv` 기반 row
  - `frame_records/<sample_id>.json`의 `frame_paths`
- 출력:
  - `parse_records/<sample_id>.json` (raw parse)
- 역할:
  - 프레임 + 원문 caption으로 객체/행동/힘 후보 구조화

### Stage4 Vision Checking
- 입력:
  - `parse_records/<sample_id>.json` (raw parse)
  - frame paths
- 출력:
  - 같은 `parse_records/<sample_id>.json`에 `vision_checked_parse` 갱신
- 역할:
  - parse 결과를 프레임 근거로 교정

### Stage5 Physics Reasoning
- 입력:
  - `vision_checked_parse`
  - frame paths
- 출력:
  - `parse_records/<sample_id>.json`에 `physics_reasoning` 추가
- 역할:
  - 인과/물리적 설명 생성

### Stage6 Scoring
- 입력:
  - `parse_records/*.json`
- 출력:
  - 각 parse record에 `physics_richness`, `physics_label`, `penalties` 등 추가
- 역할:
  - 통과/탈락에 필요한 정량 점수 부여

### Stage7 Prompt Extending
- 입력:
  - parse/scoring 결과
  - canonical prompt(`original_caption`)
- 출력:
  - `prompt_records/<sample_id>.json` (`cleaned_prompt`, `extended_prompt`)
- 역할:
  - 최종 학습/생성용 프롬프트 확장

---

## 3) 최종 Export (Stage8)

```bash
python scripts/run_phase.py --phase export
```

생성 위치: `outputs/<run_name>/final_exports/`
- `all_scored_samples.(csv|jsonl)`
- `passed_winners.(csv|jsonl)`
- `rejected_samples.(csv|jsonl)`

---

## 4) 디렉토리 구조 (핵심만)

```text
data/
  panda70m_meta/                 # 입력 메타 CSV
  videos/                        # clip 결과(sample_id.mp4)
  videos_raw/                    # 원본 영상 캐시(videoID.mp4)
  prompts_txt/                   # prompt sidecar txt
  prompts_meta/                  # row sidecar json

outputs/<run_name>/
  metadata_records/              # shortlist.csv/jsonl
  frame_records/                 # frame 경로 기록
  parse_records/                 # stage3~6 누적 결과
  prompt_records/                # stage7 결과
  final_exports/                 # stage8 최종 산출
```

---

## 5) 자주 하는 실수 체크

1. **영상 다운로드 안 했는데 VLM 결과 기대**
   - `modes.metadata_only: true`면 frame 없이도 파이프라인은 돌 수 있으나, 실제 비전 근거는 약해짐.

2. **CSV prompt 컬럼명 불일치**
   - prompt 해석 우선순위: `metadata_caption_field` -> `caption` -> `original_caption` -> `text` -> `prompt`.

3. **매칭 불안**
   - yt-dlp 경로에서는 `--manifest-jsonl`을 반드시 켜서 sample별 status/path를 추적하세요.

4. **prepare에서 두 번 필터링되는 것 같음**
   - `prepare.csv_filter.enabled: true`를 켠 경우 `disable_stage1_filters: true`를 유지하면 stage1 중복 필터링을 막을 수 있습니다.

---

## 6) 설치
```bash
pip install -r requirements.txt
```

## 7) Qwen 모델 사전 다운로드 (선택)
```bash
python scripts/download_qwen_model.py \
  --model-id Qwen/Qwen2.5-3B-Instruct \
  --local-dir models/Qwen2.5-3B-Instruct
```
