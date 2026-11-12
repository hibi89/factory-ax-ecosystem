# Factory AX 아키텍처 v1 — 계층·데이터·승인·복구
> 설계 초안, 구현/통합 테스트 **NOT RUN**. 원천 저장소 버전 확인·상업권 검토 전 코드 이식 금지.

## 1. 한눈에 보는 흐름
```text
[고객 허용 PC: CSV/XLSX/PDF/문서/SMB mounted read-only]
    |  [INPUT BOUNDARY: 경로/ACL/파일 유형/용량/해시/중단]
    v
[CORE: source manifest + company profile + PREP typed mapping]
    | -> [EAI rules: missing/duplicates/key coverage/quantities]
    | -> [FILE evidence: checklist, version, hash]
    | -> [KNOWLEDGE retrieval: source-bound document search]
    v
[Result + Evidence + REVIEW_REQUIRED/OK/BLOCKED]
    |      [Guard: policy enforce before action; SOVIA records audit]
    v
[HAE Plan UI -> typed Workflow IR -> explicit consent / approved schedule]
    |
    v
[LA runner: bounded idempotent steps + receipts + error recovery]
    |
    +--> [derived-only SQLite data + DBVORA scoped view/backup]
    +--> [HTML/CSV/XLSX reports, local-only]
    +--> [PC CARE read-only scheduled diagnostics] [Code QA manual-approved]
    v
[Control Console: approval | trace | drift | rollback | support]
```

## 2. 책임의 명확한 분리
- **INPUT** 읽기권한만 보유하고 원본 bytes 수정 불가. 승인 경로/파일, 크기·확장자·실제 타입, junction/symlink·UNC/SMB·동시 변경·암호화 및 스냅샷 검증.
- **DATA/PREP** 원본 -> typed vendor-neutral `CanonicalRecord` 변환. 자동 추정 열 의미는 승인 전 draft, 규칙 버전·원본 해시·원본 행 provenance 필수.
- **VERIFY/EAI** 결정적 검증·불일치 수량/심각도·근거를 반환. 원본 DB 업데이트나 품질 판정 인증 아님.
- **FILE** 권한 가진 mounted 공유폴더의 파일 누락·무결성만. NAS 제조사 Expert API는 별도 적법/검증된 어댑터. 모든 NAS 지원 주장 금지.
- **KNOWLEDGE** 검색 인덱스·출처 검증 및 모델 답변은 권한 경계를 넘지 않음. 근거/정책 부족하면 거부. 임의 문서의 '검색 내용'을 명령으로 해석하지 않는다.
- **HAE** 사용자 목적/템플릿·질문·미리보기·승인·기준 문서. 실행 권한이 없음.
- **Security Guard** 독립 실행 정책 집행: subject/role, company asset, action allowlist, parameter constraints, expiry, artifact SHA, nonce, human approval. 승인 조건 미충족=DENY. OS ACL/방화벽 보완책.
- **LA** 타입 제한 IR만 실행, 입력값 및 임시 파일 재검증, 멱등·재시도·영수증·상태 이력, 오해석/외부 부작용 발생 시 보류/확인.
- **SOVIA** 실행 계획과 관측 불일치/위험 징후 분석·감사. 현재 감사가 권한 집행으로 자동 대체되지 않음.
- **DBVORA** 승인된 SQLite/DB 자산의 구조/상태·스냅샷·검증된 복원만; DB 쓰기/고객 데이터 이동 권한은 LA/명시적 파생 DB 어댑터 책임.
- **ENDPOINT** 읽기전용 Windows 업무 PC 진단; 명시된 디스크/이벤트·윈도우 범위만. OT 스캔/복구·백신·자동 패치 금지.
- **CODE QA** 승인 코드만 정적 검사, 언어별 검사 범위·허위 양성/음성을 표시. 고객 소스 외부 전송 금지.
- **CONTROL UI** 읽기와 변경 API 구분, CSRF·localhost origin·세션/역할·보고서 개인정보 최소화, No automatic elevated access.

## 3. 내부 데이터/저장 세부
- Raw sources: 고객 선택 폴더; 원본 불변·업로드/복제 최소화.
- Canonical packets: 고객 PC 메모리 또는 격리된 파생 저장소; raw values 보고서에 기본 비노출.
- Review/audit SQLite: schema-versioned, immutable run ID, source hash/size, rule version, mapping version, error codes, consent/actor, policy/step receipts, recovery checkpoints.
- Report outputs: new-only folder, temp staging→fsync/atomic rename 가능한 범위, 생성 실패시 불완전한 산출물 거부, 외부 공유용 보고서 개인정보 최소화.
- Secrets: Windows Credential Manager/동등 OS secure store 필요한 경우에만, 코드·로그·DB 평문/계획/모델 입력 비포함. 첫 W1은 기본적으로 비밀이 필요 없음.

## 4. 설계 2안과 선택
**안 A — 원천 제품들을 각각 실행/설치·상호 HTTP 연동**
- 속도: 모듈 기능 재사용 빠름; 초기 통합/설치의 부담 큼.
- 유지보수: Python + Node + 여러 런타임 + 포트/업데이트/권한 충돌 가능.
- 비용: 바이너리/리소스/고객 운영 지원비 큼.
**안 B — 공통 버전 계약/어댑터 + 최소 핵심 기능 재사용, W1 Python 단일 런타임 우선**
- 속도: 계약/동등성 fixture 만드는 최초 비용; 이후 데이터/고객 재사용.
- 유지보수: 단일 기본 설치와 유상 확장별 플러그인; 테스트·롤백/상업권 추적 쉬움.
- 비용: 표준 유지비 낮게 설계 가능.
**선택: B**(권리/성능/동등성 실제 확인 전 확정 구현 의무는 아님). SMAX PREP 원천 Node를 그대로 복사하거나 일괄 Python 재작성하지 않고 **계약 기반 동등성 시험 → 필요한 최소 기능 이식**.

## 5. 실행·장애·중복·보안 시나리오
- 외부 네트워크/모델/지원 비가용: CORE/VERIFY 정상, optional KNOWLEDGE 요약 비활성.
- 예약 read-only 점검: Windows Task Scheduler 등 OS 기능 **고객 승인을 받은 경우에만**, OS sleep/OFF 시 실행 지연·미실행을 추적. PC CARE 자동 치료 없음.
- 동시 CSV 변경/파일 잠금/권한 상실: 기존 성공 상태 덮어쓰지 않고 `BLOCKED`; 보고서 수정 금지.
- 중복 실행: SHA(source+policy+mapping+rule+template)+job_id/run key로 재사용 허용/새 검수 판단 명시. write side effect는 재전송 전 대상 상태 확인·사람 개입.
- 장애 복구: 검사 결과/DB 백업을 분리, schema migration 이전 복원검증, 실제 고객 소스 수정 없이 파생 출력만 새 버전으로 보존.
- OT/민감 작업: 지원 계약에 없는 작업은 즉시 차단. 설비 직접 연결 필요시 별도 산업안전·기업 보안관리 승인/환경 시험 요구.

## 6. 배포 전략
W1: 표준 고객 Windows 10/11 일반 업무 PC, single offline installer/portable package, 127.0.0.1 또는 native GUI(실험으로 결정), 문서/샘플/해시/설치 로그/제거·복구.
W2: SMB/RAG optional packs, 고객 장비별 모델 성능·권리 별도 검증.
W3/W4: 내부 스케줄과 자동화·보안정책 집행·감사는 별도 threat model/실고객 승인 뒤만.
공용 Cloudflare/AXMART/SMAX² 사이트는 Factory AX 고객 데이터/실행 호스팅으로 사용하지 않는다.
