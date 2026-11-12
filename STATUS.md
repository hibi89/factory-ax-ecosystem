## 2026-11-12 KST — Factory VERIFY first executable W1-50 checkpoint (feature only)
- Product: **Factory AX VERIFY W1 50% provisional engineering milestone**, limited basic intake/quality. **Whole Factory AX Ecosystem completion remains UNASSESSED**, W2-W4 NOT BUILT, all **RELEASE HOLD**. No customer release claim.
- Original Python 3.11+ stdlib local offline code: four manually approved synthetic/authorized CSV/restricted XLSX sources; exact source SHA, row provenance, versioned mapping; five quality rule families, OK/REVIEW_REQUIRED/BLOCKED; new-only HTML/JSON/CSV summary.
- Local synthetic same source/test files: **54 PASS / 0 FAIL / 0 SKIP**, compileall PASS; actual synthetic four-file CLI return OK; negative CLI review/blocked and no overwrite tested. Product blob SHA `dc4be03b682679211d16aed7c3efd6ac45c41f82`; tests blob SHA `30e014751b2e8c7511d4493d3fde31749ed51d94`; example blob `f7b26da338948e9d4dc404c52cf220f1dc1fdee3`. Exact GitHub blobs verified against local bytes.
- **NOT VERIFIED**: PREP source golden parity (new standalone PREP has no GitHub runtime), EAI integration, cross-stage 1:N and returns/date/quantities, Windows 10/11 PC and Excel exports, concurrency race-free persistence, customer rights/security, installer/CI/Production. Only limited quality OK, not product/customer acceptance.
- Repo `hibi89/factory-ax-ecosystem@feature/data-verify`; baseline `main@29b9653ccbc4bcd36a190f9e9d78954bcc4dae76` untouched. Run `python -m unittest discover -s tests -q` and `python examples/make_synthetic.py /absolute/new/demo`. Evidence `docs/VERIFY_50_EVIDENCE_20261112.md`, user can recover baseline without force.


---

# STATUS — Factory AX Ecosystem
> 2026-11-12 KST · **신규 Private 저장소 문서/브랜치 세팅 단계. 현재 개발은 아직 시작하지 않음.**

## 현재 사실
- GitHub `hibi89/factory-ax-ecosystem`: 사용자 생성, **Private**/default `main`; 새 저장소는 생성 시 빈 상태였고, 총괄이 초기 README/기준 문서/큰 기능군 브랜치 구성을 요청받았다.
- 확정 비전: 공장/보수적 기업 대상 **표준제품 납품형**, W1 CORE+VERIFY 진입→W2 KNOWLEDGE/FILE→W3 HAE+Lightning Azent·Security Guard·SOVIA/DBVORA→W4 PC CARE/Code QA/통합 Console.
- SMAX² 자체는 SELF 플랫폼으로 별도 유지. **PREP의 데이터 전처리 계약만** 기술 재사용 후보. REA_Web 전체 플랫폼은 W1 필수에서 제외.
- 신규 Factory AX 구현·운영 패키지·제조업 실자료·API·고객/실기기·CI/E2E·사업 거래 **0건**, 모든 제품 **RELEASE HOLD**. 완성률 **미측정**, 기존 원천 레포의 85%가 Factory 진척이 아님.
- 소유자·고객 계정/데이터, 권한/비밀/보안설정·클라우드·배포/지출·다른 GitHub 소스/브랜치 변경 **없음**.
- 문서 구성: `README.md`, `START_HERE.md`, `HANDOFF.md`, `STATUS.md`, `AGENTS.md`, `REQUIREMENTS.md`, `SCHEMA.md`, `docs/*`, `docs/workstreams/*`, `.gitignore`.

## 프로젝트/상용 진행 상태
| 목표 | 설계 | 기능 구현 | 테스트 | 출시 |
|---|---|---|---|---|
| W1 CORE+VERIFY | 작성 | NOT BUILT | NOT RUN | HOLD |
| W2 KNOWLEDGE/FILE | 작성 | NOT BUILT | NOT RUN | HOLD |
| W3 승인형 AX HAE/LA/SOVIA/Guard | 작성 | NOT INTEGRATED | NOT RUN | HOLD |
| W4 PC CARE/Code QA/Console | 작성 | NOT INTEGRATED | NOT RUN | HOLD |

## 첫 실제 작업(다음 `ㄱ`)
1. 신규 feature branch `feature/data-verify` 에서 PREP 계약과 EAI 현재 소스를 최신 SHA로 검수; **고객 자료 없는 제조업 4종 합성 스키마/독립 oracle**를 처음 만들고 테스트한다.
2. JavaScript PREP 직접 어댑터 vs Python port 두 안의 동등성·실행/유지보수 비용을 소스/벤치/사용권 기준으로 재검토, 승인된 목표 범위에서 하나 선택.
3. 최소 CORE/VERIFY 기능만 먼저. UI/보안/패키징은 병행할 수 있지만 실제 W1 E2E와 원본 불변·오류 보고 없이 상품 진행률 임의 상승 금지.
4. GitHub CI·Windows 실제 실행/고객 적합성·권리→`integration/develop` 통합→유료 고객 파일럿/출시 승인 전까지 HOLD.

## 문서/브랜치 검증
- 작성 작업 단위에서는 코드/실행/외부 서비스 변경이 없으므로 테스트 0/0이며, GitHub 파일/브랜치 HEAD는 작업 종료 시 **원격 재조회**해야 한다.
- GitHub 커밋 SHA는 self-referential 문서에서 추정하지 않는다. 종료 보고와 다음 채팅에서 실제 HEAD를 확인한다.
- Production URL/Vercel/Cloudflare 프로젝트: **미적용**, 별도 API/라이선스/환경변수 없음.
