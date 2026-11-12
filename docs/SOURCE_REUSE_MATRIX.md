# 원천 코드·자산 재사용/권리·상태 인벤토리
> 2026-11-12 KST GitHub 조회 기반 후보 목록. **이 저장소에는 타 원본 코드/고객 자료를 복사하지 않았다.** 정확 commit SHA·LICENSE/NOTICE·상용권/사용자 사전승인·API 계약을 코드 이식 시 재조회해야 한다.

| 원천 | 기준 참조 브랜치/범위 | 재사용 후보 | 현재 근거/제약 |
|---|---|---|---|
| `hibi89/SMAX` Private | `feature/prep-self-owner-mapping-p8`·`preprocessing/` | Generic CSV/XLSX 파싱·컬럼 매핑·SHA·REVIEW_HOLD (**PREP 기술만**) | Node 기반, SELF 특정 매출 매핑과 제조업 규칙 분리; P21 제한된 Linux/Chromium 검증·전체 Windows/상용 미완 |
| `hibi89/EAI` Private | `feature/kmong-eai-85-p31-20261112` | CSV quality/key coverage/outlier/schema drift, SHA 영수증 | 85% 잠정; Linux 622 PASS/1 Win-only SKIP, 실제 제조업/고객 Windows 미검증 |
| `hibi89/hibi89-ugreen-nas-hackathon` | `lead/ugreen` | ProjectReady 체크리스트·승인/파일 증거 원리 | UGREEN 공식 Skill의 NAS 실장비/다제조사 호환 미검증, 공식 Kit/약관 별도 확인; 상용 범용판 허용·권리 검토 |
| `hibi89/RAG_STUDIO` | `feature/p550-mapped-cited-journey` | 근거 문서 검색, 한글 검수 UI, 로컬 색인 | 검색/근거 기능 후보; 실 PDF/제조 매뉴얼·Windows/폐쇄망 고객 RAG 정확도, 모델/임베딩 라이선스 미검증 |
| `hibi89/HAE` Private | `feature/axflow-mvp` | 사람용 승인/업무 설명·카탈로그/합성 SQLite 자산 | 85% 잠정, 전체 CI에서 기존 패키지 parity 2 FAIL, 고객용 실환경 자동화 HOLD |
| `hibi89/HAE` Private | `feature/la-p17-audit-evidence-20261112` | LA typed 실행·중복/감사 영수증·재개 | 기존 해총 기준 Linux/Windows CI 성공 이력; Factory 실고객 연결/고위험 권한 미검증 |
| `hibi89/SOVIA_sovereign` | `develop` / 최신 기능 브랜치 | 위험관측·정책/감사·승인 전 검토 | 별도 Security Guard 강제 실행/실 LA 관측 인증은 아직 구현·검증 필요, 감사 단독 권한 집행 아님 |
| `hibi89/DBVORA` Private | `feature/p0-db-map` | DB inventory/schema·백업/복원 계약 | 코드 일부 존재하나 복합 고객 업무 DB 연동·복구 실환경 미검증 |
| `hibi89/AX_MART` Private | `feature/pc-care-usb` | Windows 업무 PC 진단 스크립트/보고서 | PC CARE v0.1-alpha, Win10/11 실기기/WinRE·고객 상용 미검증; OT 스캔 금지 |
| `hibi89/ai-code-checker` | `main` / retail feature | Windows 오프라인 Python/JS 정적 검사·보고서 | 언어 범위 한정, 기업용 AV/EDR 아님, Windows 고객 실기기 및 Tcl/Tk·NOTICE/상업권 검증 필요 |
| `hibi89/REA_Web` | `feature/lite-offline-html-20261112` | CSV 로컬 앱/GUI **아이디어만** | Factory AX에 REA_Web 전체 플랫폼 의존성 넣지 않음. GUI는 독립 최소 구현 |
| `hibi89/hibi89-kic-proofinvest` | `lead/kic` | evidence chain/source-span/fail-closed 설계 참고 | 금융 전용 코드 전체 이식 금지; 외부 출처 인증 자동 보증 아님 |
| `hibi89/AI_AutoML_Analyst` | `main` | 향후 생산 품질 통계 ML 실험 | 모델 실공정 검증/데이터 드리프트·설명 가능성 확보 전 기본 판정 엔진에서 제외 |
| `hibi89/self-hosted-n8n-reliability-lab` | `main` | 멱등·재시도·실패 기록 패턴 | n8n 서비스를 Factory W1 필수 런타임으로 사용하지 않음 |
| `hibi89/candle_scraper` | `main` | SQLite 증분/중단 복구·윈도우 포장 방식 참고 | 코인 데이터/거래소 API/라이선스는 제조업 제품 불필요 |
| `hibi89/frontend-foundry-ax` | 개발 브랜치 | 내부 화면 QA·디자인 가이드 | FFAX 전체를 공장 PC에 의존성으로 탑재하지 않음 |
| `hibi89/hibi89-paypal-ai-hackathon` | `lead/paypal` | 계약/마일스톤 승인·인간 통제 원리 참고 | 결제/PayPal/고객 플랫폼 전체 불필요, 금융 인가·권한 혼동 금지 |

## 원본 재사용 절차
1. 원천 최신 HEAD/해당 기능 코드 blob SHA·테스트 증거와 출시 권리/서드파티 LICENSE/NOTICE/모델·폰트/임베딩 라이선스 검수.
2. 외부 데이터를 받을 수 없는 제품군(폐쇄망)의 특정 환경·Windows/Node/Python 의존성과 고객 기기 성능을 확인.
3. 직접 복제 vs 어댑터/계약 재구현 2안 성능·비용·보안·유지보수 평가, 사전 승인 후 **최소 기능만** 선별 이식/참조.
4. 원천 파일 고유 SHA/출처·변경 근거·버전·검증 소스와 라이선스 고지 기록. Public → Private로 가져온다고 제3자 라이선스가 사라지는 것은 아님.
5. 각 기능은 **원본 프로젝트 테스트 결과 != Factory AX 통합 테스트**. 통합 실행·Windows·실제 고객 보안 테스트를 별도 수행.
6. 원본 저장소/브랜치·대회 제출물의 원본 보존. 고객 실자료·비밀을 GitHub로 복사하지 않음.

## 시장/사업 참고
- 크몽 기존 저가 엑셀/로컬 RAG/맞춤 SI 등 대안 존재. 실제 판매량/가격 수용성 검증 전 가설 유지.
- SMAX² 전체 플랫폼·REA_Web 전체는 현재 첫 제품의 필수 의존성이 아니다.
