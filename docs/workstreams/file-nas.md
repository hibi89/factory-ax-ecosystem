# feature/file-nas — 기능 담당 원칙

> 2026-11-12 KST · 현재 설계만, 기능 구현/CI/고객 수락 **NOT RUN** · 출시 RELEASE HOLD

## 책임
W2 로컬/SMB 검사성적서·도면·납품 파일 검수

**진입 단계:** W2
**원천 확인:** [SOURCE_REUSE_MATRIX](../SOURCE_REUSE_MATRIX.md) 의 관련 저장소/브랜치 최신 HEAD·LICENSE/원본을 재조회. 확인 전 코드 복사/타 프로젝트 변경 금지.

## 입력 → 출력
- **입력:** 승인된 폴더/SMB 공유범위·납품 체크리스트
- **출력:** 누락·중복·버전 후보·SHA 근거/보고서
- 변경 전 버전형 [SCHEMA](../../SCHEMA.md), [통합 계약](../INTEGRATION_CONTRACTS.md), [안전 모델](../SECURITY_MODEL.md) 대조. 고객 자료/키/원본 자동수정 금지.

## 먼저 개발할 한 단위와 리스크
SMB mounted Windows share 우선, NAS 전용 Skill/OS 내부 실행 분리

## 필수 검증
다제조사 실 SMB read-only/ACL/경로 탈출/변조·대용량 시험
합성 단위 테스트와 실제 Windows/고객 E2E·제품 출시를 별도로 보고. 명령/실행 로그/정확 소스 SHA/FAIL·SKIP·미검증·복구 경로를 해당 브랜치 HANDOFF 변경 및 총괄 기록에 반영한다.

## 경계/병합
- 담당 외의 원천/브랜치·고객 컴퓨터·외부 서비스 변경 금지.
- 새 API/스토리지/쓰기 권한·고비용 장치/배포/고객 자료 이동은 사전 승인.
- 최소 코드·회귀 후 [BRANCH_STRATEGY](../BRANCH_STRATEGY.md) 규칙대로 `integration/develop` 통합 제안.
- 이 문서가 브랜치에 함께 있다고 해서 제품/브랜치가 개발된 상태라는 뜻은 아니다.
