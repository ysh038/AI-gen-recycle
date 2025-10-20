# AiNEWT - Frontend React 프로젝트 초기화 템플릿

## 프로젝트 개요

이 프로젝트는 React와 TypeScript를 기반으로 한 프론트엔드 개발을 위한 초기화 템플릿입니다. 일관된 개발 환경과 코드 구조를 제공합니다.

## 기술 스택

### 핵심 기술

- **Core**: React, TypeScript, JavaScript
- **Routing**: React Router Dom
- **클라이언트 상태 관리**: Zustand
- **서버 상태 관리**: TanStack Query (React Query)
- **번들러**: Vite
- **스타일링**: CSS Module, Emotion

### 기술 버전

```
- React: 19.1.0
- React DOM: 19.1.0
- TypeScript: 5.8.3
- React Router Dom: 7.6.0
- Zustand: 5.0.4
- TanStack Query: 5.75.7
- Vite: 6.3.5
- Jest: 29.7.0
- Semantic Release: 24.2.3
- ESLint: 9.25.0
```

### 테스트

- **단위 및 기능 테스트**: Jest
- **E2E 테스트**: Cypress - (필요 시 설치)

### 기타

- **버전 관리**: Semantic Release (Git 커밋 메시지 기반)

## 디렉토리 구조

```

├── 📁 public # 정적 파일 (빌드시 그대로 복사됨)
│ ├── 📁 images # URL로 직접 접근할 이미지
│ ├── 📁 svgs # URL로 직접 접근할 SVG
│ ├── 📁 videos # URL로 직접 접근할 비디오
│ └── 📁 etc # 기타 정적 파일
│
├── 📁 src
│ ├── App.tsx # 최상위 컴포넌트
│ ├── main.tsx # 진입점
│ ├── global.css # 전역 스타일 (폰트, 변수 등)
│ ├── initialize.css # 브라우저 스타일 초기화
│ │
│ ├── 📁 assets # 코드에서 import하는 리소스
│ │ ├── 📁 fonts # 폰트 파일
│ │ ├── 📁 images # 이미지 파일
│ │ ├── 📁 svgs # SVG 파일
│ │ ├── 📁 videos # 비디오 파일
│ │ └── 📁 etc # 기타 리소스
│ │
│ ├── 📁 components # UI 컴포넌트
│ │ └── 📁 shared # 공유 컴포넌트
│ │
│ ├── 📁 hooks # 커스텀 React 훅
│ │ └── 📁 shared # 공유 훅
│ │
│ ├── 📁 queries # API 요청 관련 코드
│ │ └── 📁 shared # 공유 fetch 로직
│ │
│ ├── 📁 routes # 라우팅 설정 및 페이지
│ │
│ ├── 📁 stores # 상태 관리 코드
│ │ └── 📁 shared # 공유 스토어
│ │
│ ├── 📁 templates # 페이지 레이아웃 템플릿
│ │
│ ├── 📁 types # TypeScript 타입 정의
│ │ └── 📁 shared # 공유 타입
│ │
│ └── 📁 utils # 유틸리티 함수
│
├── eslint.config.js # ESLint 설정
├── vite.config.ts # Vite 설정
├── tsconfig.json # TypeScript 설정
├── .releaserc.json # Semantic Release 설정
└── CHANGELOG.md # 변경 사항 로그
```

## 공통화 사용 관리 방안

- **Private**: 각 페이지별로 하위 디렉토리 생성하여 사용 (components, hooks, queries, routes, stores, types 등)
- **Public**: 공용 디렉토리로 기본적으로 페이지별 하위 디렉토리 불필요 (templates, utils 등)

## 정적 파일과 리소스 관리

- **정적 파일(public)**:

  - 빌드 시 그대로 복사되어 배포됨
  - URL을 통해 직접 접근 가능
  - 절대 경로로 접근 (`/images/example.png`)
  - 빌드 시 변환/최적화되지 않음
- **리소스 파일(assets)**:

  - 코드에서 import하여 사용
  - 빌드 과정에서 번들링, 최적화, 해싱됨
  - 작은 이미지는 자동으로 base64로 인라인화 가능
  - 상대 경로로 import (`import logo from '@/assets/images/logo.png'`)

## 버전 관리 (Semantic Versioning)

- **MAJOR**: 호환되지 않는 API 변경 (Breaking Change)
- **MINOR**: 이전 버전과 호환되는 새 기능 추가 (Feature)
- **PATCH**: 이전 버전과 호환되는 버그 수정 (Fix)

`semantic-release` 모듈을 통해 Git 커밋 메시지 기반으로 CHANGELOG.md를 자동 생성하고 버전을 자동화합니다.

### 사용 플러그인

- `@semantic-release/commit-analyzer`: 커밋 메시지 분석
- `@semantic-release/release-notes-generator`: 릴리즈 노트 생성
- `@semantic-release/npm`: package.json 버전 수정 및 npm 배포
- `@semantic-release/github`: GitHub 릴리즈 생성
- `@semantic-release/changelog`: CHANGELOG 작성


## Prettier & ESLint 설정 가이드

## 1. 필요한 확장 및 패키지 설치

### 1) NPM 패키지 설치
```bash
npm install
```

#### 설치 패키지 목록

| 패키지명                                 | 이유 / 역할                                                                             |
| ------------------------------------ | ----------------------------------------------------------------------------------- |
| **eslint**                           | 코드 품질 검사 도구의 핵심 본체. 모든 규칙의 기반이 되는 Linter.                                           |
| **prettier**                         | 코드 포매터. 줄바꿈, 들여쓰기, 따옴표 등 **스타일 자동 정리** 도구. ESLint가 못 잡는 포맷까지 담당.                    |
| **@typescript-eslint/parser**        | TypeScript 코드를 **ESLint가 이해할 수 있도록 파싱**해주는 파서. `.ts`, `.tsx` 파일을 분석하려면 필수.          |
| **@typescript-eslint/eslint-plugin** | TypeScript 전용 규칙 모음. `no-unused-vars`, `naming-convention` 같은 TS 특화 룰을 추가해줌.        |
| **eslint-plugin-react**              | React JSX 관련 규칙 제공 (`react/prop-types`, `react/jsx-uses-vars` 등).                   |
| **eslint-plugin-react-hooks**        | React Hook의 사용 규칙 검사 (`rules-of-hooks`, `exhaustive-deps` 등). Hook 잘못 쓰는 걸 미리 감지해줌. |
| **eslint-plugin-import**             | `import` 문 정렬, 중복, 순서 등 **모듈 임포트 관련 정리** 규칙 제공. 정렬 기준 커스터마이즈에 필수.                   |
| **eslint-plugin-prettier**           | Prettier 포맷팅 결과를 **ESLint 경고/에러로 함께 보여줌**. ESLint + Prettier 통합을 위한 다리 역할.          |
| **eslint-config-prettier**           | ESLint와 Prettier 간 **충돌 방지** 역할. 포맷 관련 ESLint 규칙들을 끄고 Prettier가 우선되도록 해줌.           |


### 2) VSCode 확장 프로그램 설치(권장)
- [Prettier - Code formatter](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode)
- [ESLint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint)

---

## 2. 적용된 Prettier 규칙 (prettier.config.js)

| 옵션              | 값         | 설명                                      |
|-------------------|------------|-------------------------------------------|
| semi              | false      | 문장 끝에 세미콜론(;)을 붙이지 않음        |
| singleQuote       | true       | 문자열에 작은따옴표(') 사용                |
| trailingComma     | 'all'      | 가능한 모든 곳에 마지막 쉼표(,) 추가        |
| printWidth        | 80         | 한 줄 최대 80자                            |
| tabWidth          | 4          | 들여쓰기 4칸                               |
| bracketSpacing    | true       | 중괄호({}) 안에 띄어쓰기 추가              |
| endOfLine         | 'auto'     | OS에 맞는 줄바꿈 문자 사용                 |

---

## 3. 적용된 ESLint 규칙 (eslint.config.js)

### Prettier 관련
- Prettier 포맷 위반 시 워닝(warning) 발생 (`prettier/prettier: 'warn'`)

### TypeScript 관련
- 사용하지 않는 변수는 경고, 단 변수명이 `_`로 시작하면 무시 (`@typescript-eslint/no-unused-vars`)
- 함수 반환 타입 명시하지 않아도 됨 (`@typescript-eslint/explicit-module-boundary-types`)
- 네이밍 컨벤션 (`@typescript-eslint/naming-convention`):
    - 변수: camelCase, 단 const는 UPPER_CASE 허용
        - boolean 타입 변수: is/has/should/can/must/was/will로 시작
    - 함수: camelCase 와 PascalCase 둘 다 허용
    - 클래스/인터페이스/타입: PascalCase
    - 인터페이스: I로 시작해야 함 (예: IExample)
    - 타입 파라미터: PascalCase, T로 시작

### React 관련
- prop-types 사용하지 않아도 됨 (`react/prop-types`)
- JSX에서 React import 필요 없음 (`react/react-in-jsx-scope`)
- JSX에서 사용된 변수는 정의된 것으로 간주 (`react/jsx-uses-vars`)

### React Hooks 관련
- 훅스 규칙 위반 시 에러 (`react-hooks/rules-of-hooks`)
- 의존성 배열 누락 시 경고 (`react-hooks/exhaustive-deps`)

### Import 정렬 (`import/order`)
- 그룹: builtin, external, internal, parent, sibling, index
- 경로 그룹:
    - `@/**` (internal)
    - `**/*.{css,scss,sass}` (internal)
    - `**/*.{png,jpg,jpeg,gif,svg,webp}` (internal)
- 그룹 간 줄바꿈(always)
- 알파벳순 정렬(asc, 대소문자 구분 없음)

---

## 4. VSCode 에디터 설정(권장)
`.vscode/settings.json`에 아래와 같이 설정되어 있습니다:

```json
{
  "editor.formatOnSave": false,
  "editor.tabSize": 4,
  "editor.detectIndentation": false,
  "eslint.validate": ["javascript", "typescript", "typescriptreact"]
}
```

---

## 5. 코드 자동 정리 명령어
- Prettier로 전체 포맷 수정:  
  ```bash
  npm run prettier:fix
  ```
- ESLint로 자동 수정:  
  ```bash
  npm run lint:fix
  ```

---

## 6. 참고
- 저장 시 자동 포맷은 개별 설정
- 팀원 모두가 동일한 코드 스타일을 유지할 수 있습니다. 