# 브랜치 전략·업무 범위·병합 규칙 — Factory AX
> 브랜치 구분은 '제품 1개당 브랜치'가 아니라 **큰 기능군 별 책임**. 모든 개발 브랜치가 같은 검증된 문서 기준점에서 출발.

## 현재 생성할 10개 브랜치 (main 포함)
| 브랜치 | 담당 | 이번 단계 첫 목표 | 코드/출시 판정 |
|---|---|---|---|
| `main` | 검증된 문서·안정 릴리스 기준 | 최종 100% 설계·문서/승인 | 코드 없음 |
| `integration/develop` | 공통 프로토콜·통합 테스트·CI | feature 간 버전·엔진 계약 | 미구현 |
| `feature/data-verify` | CORE, PREP 기술계약, EAI, W1 VERIFY | 제조업 발주/생산/검사/출하 대사 | **첫 개발 대상** |
| `feature/knowledge-rag` | RAG Studio 검색·출처·로컬 LLM 선택 | 근거/권한 범위 검색 | W2 대기 |
| `feature/file-nas` | FlowPilot·로컬/SMB 파일·NAS | 읽기 전용 납품 파일 검수 | W2 대기 |
| `feature/hae-la` | HAE 상담/계획/승인 + LA typed 실행 | 안전한 read-only 로컬 워크플로 | W3 대기 |
| `feature/security-governance` | 독립 Policy Guard + SOVIA 감사 | 실행권한 강제·승인/감사 계약 | W3 전 필수 설계 |
| `feature/endpoint-codeqa` | PC CARE + AI Code Checker | 업무용 PC 수동/정기 읽기진단·코드 QA | W4 대기 |
| `feature/control-console` | 한글 관리자 GUI·대시보드·접근통제 | W1 검수 UI 최소판 | W1 최소 UI 개발 시 |
| `feature/delivery-ops` | 로컬 설치·업데이트·복구·납품/지원 | Windows/폐쇄망 납품 게이트 | W1 병행 |

## branch ownership
- `main`: 요구사항과 품질 계약 변경이 승인된 stable release. 추정으로 개발률/CI PASS 갱신 금지.
- `integration/develop`: 통합 의존성/경계, 소스/패키지 버전, installer/보안/회귀·자료 보존 검사. 각 브랜치의 코드를 무조건 머지하지 않는다.
- feature별 총괄은 담당 문서에서 input/output/test/security/interface 제약 확인. 다른 브랜치 직접 수정 필요 시 인터페이스 제안/PR로 처리하고 **원천 저장소는 별개**.
- 개인정보/계정/기밀 원본은 브랜치와 관계없이 GitHub에 커밋하지 않는다.
- 각 브랜치 HEAD는 생성 직후 `main`의 동일 문서 baseline SHA. **브랜치가 생겼다고 개별 기능 구현/독립테스트 완료가 아니다.**

## 협업·병합 게이트
1. 기능 브랜치 최신 main 계약·상위 소스/모듈 선행 제약 확인, 문서에 범위/전제.
2. 최소 변경 코드 + 합성 fixture + 정상·실패·보안·복구 테스트 + 스키마 버전/소스 provenance 기록.
3. PR 또는 명확한 리뷰/차이 분석→ `integration/develop` 에 선택적으로 통합. GitHub 최신 base/feature SHA·충돌/변경경로·권리·실험이력 확인.
4. 통합 Windows/기능·민감정보/로그·임시파일/외부 통신/실고객 장비권한 테스트.
5. 승인된 릴리스만 `main`에 반영. 기존 소스/문서·테스트/상용 출시에 대한 정확한 상태 갱신.
6. 비정상 오류에서 force push/기존 history rewrite/CI 무효화·테스트 skip으로 '녹색' 만들지 않는다.

## 우선 작업 순서
`feature/data-verify`(핵심 엔진) + `feature/control-console`(최소 GUI) + `feature/delivery-ops`(Windows 인수) → `integration/develop` 검증 → 첫 W1 납품 후보.
이후 `feature/knowledge-rag`, `feature/file-nas` (읽기 전용) → `feature/security-governance` 정책 집행 강화 → `feature/hae-la` 승인형 실행 → `feature/endpoint-codeqa` 정기 점검/QA → 통합 콘솔.
**보안 정책은 W1부터 필수, 자동화 이후에 추가하는 '옵션'이 아니다**. 별도 Security Guard/고위험 인증 모듈은 W3 이전 준비.

## 서비스/배포
기본은 고객 PC 온프레미스, GitHub/Vercel/Cloudflare Production 연결 **없음**, 실제 customer installer/외부 계정/결제/서비스 공개는 별도 승인.
