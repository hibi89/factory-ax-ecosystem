# Factory AX 총괄 · 재개 진입점
> 최신 GitHub 원격 기준. 마지막 확인: 2026-11-12 KST. 특정 개인/채팅 세션을 영구 자동 실행하는 시스템은 아니다.

## 담당 총괄 역할
**Factory AX 전담 총괄**은 제품 설계, 안전한 자체 코드 개발, 회귀검증, 원천 자산/권리 추적, GitHub 반영 및 인수인계를 책임진다. 사용자 `ㄱ` = 최신 상태를 조회하고 첫 미완료 작업을 실제로 진척시키라는 지시. 요구되지 않은 고객 접촉, 지출/권한 수정, 데이터 외부전송, 타 저장소 임의 변경, 서비스 공개는 허가하지 않는다.

## 재개 순서 (필수)
1. 정확한 저장소 `hibi89/factory-ax-ecosystem`, default `main`, Private 및 HEAD/현재 기능 브랜치 확인.
2. `HANDOFF.md` → `STATUS.md` → `AGENTS.md` → `REQUIREMENTS.md` → `docs/PRODUCT_BLUEPRINT.md` → `SCHEMA.md`.
3. `docs/BRANCH_STRATEGY.md` 에서 담당 기능 브랜치 확인, `docs/ROADMAP.md` 와 `docs/ACCEPTANCE_MATRIX.md` 에서 미완료 인수조건 선택.
4. 각 원천 저장소의 최신 HANDOFF/STATUS/실제 소스 및 SHA, LICENSE/제3자 약관을 확인. 과거 서술보다 실제 최신 코드·CI를 우선한다.
5. 이전 시도의 실패 유형·복구 경로 확인 후 **검증 가능한 기능 한 단위만** 구현/시험. 임의 자동 승인·타 저장소 병합 금지.
6. 기능별 브랜치에 코드/테스트 커밋 → 필요시 `integration/develop` 로 검증된 단위를 통합 → `main` 은 사용자 승인된 안전한 릴리스 기준만.
7. 중대한 변경 시 `STATUS.md` 와 `HANDOFF.md`를 같은 변경 흐름에서 최신화하고 원격 HEAD·CI 상태/결과 검증. 단순 읽기에는 불필요한 커밋 금지.

## 제품 기준
- **W1 최우선**: Factory AX CORE + VERIFY, 일반 Windows 업무 PC의 CSV/XLSX, 발주/생산/검사/출하의 근거 기반 대사, 고객 허용 범위 내 자료 읽기, 로컬 보고서.
- **최종 목표**: 승인형 내부 AX 시스템(HAE + LA) + 지식검색 + NAS/파일 검수 + 보안정책 집행/SOVIA 감사 + PC CARE 및 코드검수 + 복구/관리 콘솔.
- **사업 모델**: SMAX²와 별도, 공급자 구축 납품형/표준제품+제한된 설정. 고객이 직접 SELF 구축을 강요받지 않는다. PREP 계약만 재사용.
- **절대 금지**: 공장 기계 제어/PLC/SCADA/MES 쓰기, 미승인 운영망 설치, 무인 수리/삭제, AI 임의 쉘 실행, 근거 없이 보안 100%/3초/정확도 100%/매출 보장.

## 현재 기준
- 초기는 문서·Git 브랜치 **구성 단계**. 실행 코드/설치 파일/구매·고객 검수·제조업 E2E/CI/Production 모두 미진행.
- 권리/데이터: 원천 저장소 변경 금지, Private source와 라이선스 검토 후 복사/이식 여부 결정.
- 다음 단위: W1 원천 PREP(계약) vs Python 단일 런타임 설계 확인 → 제조업 가상 4파일 계약/정답 fixture 정의 → 최소 검수 엔진 개발 계획에 따라 구현.
