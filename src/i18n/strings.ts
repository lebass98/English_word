/**
 * 화면에 보이는 문구 모음.
 *
 * 이 앱을 쓰는 사람은 한국인이다. 그래서 화면의 말은 항상 한국어다.
 * 바뀌는 것은 "무엇을 배우느냐"(학습 언어)이지 "화면의 말"이 아니다.
 *
 * 단어 뜻·예문 해석처럼 학습 콘텐츠에 속하는 한국어는
 * src/data/<학습언어>/tr/ko.json 에 따로 둔다.
 */

const ko = {
  // 공통
  "common.back": "뒤로 가기",
  "common.backArrow": "← 돌아가기",
  "common.cancel": "취소",
  "common.delete": "지우기",
  "common.on": "켜짐",
  "common.off": "꺼짐",

  // 아래 탭
  "nav.home": "홈",
  "nav.wordbook": "단어장",
  "nav.settings": "설정",

  // 홈
  "home.myCourse": "내 코스",
  "home.todayRecord": "오늘의 기록",
  "home.seenToday": "오늘 본 단어",
  "home.knownToday": "오늘 외운 단어",
  "home.streak": "연속 학습",
  "home.days": "일",
  "home.reviewStart": "복습 시작",
  "home.firstWordPrompt": "오늘 첫 단어를 시작해 보세요",

  // 이어하기 카드
  "continue.title": "이어하기",
  "continue.resume": "이어서 학습하기",
  "continue.start": "학습 시작하기",

  // 코스 카드
  "course.notStarted": "학습 전",
  "course.studying": "학습중",

  // 유닛 목록
  "level.fallback": "학년",
  "level.preparing": "단어 데이터 준비 중입니다",

  // 학습 화면
  "study.notFound": "단어를 찾을 수 없습니다",
  "study.hide": "가리기",
  "study.show": "보기",
  "study.example": "예문",
  "study.synonyms": "유의어",
  "study.etymology": "어원",
  "study.imagePreparing": "연상 이미지 준비 중",
  "study.prevWord": "이전 단어",
  "study.nextWord": "다음 단어",
  "study.autoAdvanceToggle": "자동 넘김 켜기 끄기",
  "study.speak": "{word} 발음 듣기",
  "study.unsure": "아직 헷갈려요",
  "study.known": "외웠어요!",

  // 단어장
  "wordbook.title": "단어장",
  "wordbook.all": "전체",
  "wordbook.known": "외운 단어",
  "wordbook.unsure": "헷갈리는 단어",
  "wordbook.emptyTitle": "단어장이 아직 비어 있어요",
  "wordbook.emptyDesc": "학습한 단어가 여기에 차곡차곡 쌓여요",
  "wordbook.goStudy": "학습하러 가기",
  "wordbook.noRecords": "아직 기록된 단어가 없어요",
  "wordbook.noKnown": "아직 외운 단어가 없어요",
  "wordbook.noUnsure": "헷갈린다고 표시한 단어가 없어요",

  // 설정
  "settings.title": "설정",
  "settings.myName": "내 이름",
  "settings.namePlaceholder": "이름을 입력하세요",
  "settings.studySettings": "학습 설정",
  "settings.autoAdvance": "자동 넘김",
  "settings.autoAdvanceDesc": "학습 화면에서 다음 단어로 저절로 넘어가요",
  "settings.record": "학습 기록",
  "settings.noRecord": "아직 학습 기록이 없어요",
  "settings.resetProgress": "학습 기록 초기화",
  "settings.resetConfirmTitle": "정말 지울까요?",
  "settings.resetConfirmDesc":
    "외운 단어와 이어하기 지점이 모두 지워져요. 계속할까요?",

  "settings.recordSummary": "외운 단어 {known}개 · 헷갈리는 단어 {unsure}개",

  // 학습 언어 설정
  "settings.studyLang": "학습 언어",
  "settings.studyLangDesc": "어떤 말을 배울지 고르세요. 그림은 그대로 두고 단어만 바뀌어요",

  // 학습 언어 이름
  "studyLang.en": "영어",
  "studyLang.ja": "일본어",

  // 읽어 주는 설명 (화면 낭독기용)
  "a11y.unitProgress": "UNIT {unit}, {total}개 중 {known}개 외움",
  "a11y.reviewWord": "{word} 복습하기",
  "a11y.studyWord": "{word} 학습하기",
  "a11y.courseNotStarted": "{label} 아직 학습 전",
  "a11y.courseProgress": "{label} 학습중, {total}개 중 {known}개 외움",
  "course.wordCount": "{count}개 단어",

  // 영어 코스 단계
  "level.middle-1.label": "중학 1학년",
  "level.middle-1.short": "중1",
  "level.middle-2.label": "중학 2학년",
  "level.middle-2.short": "중2",
  "level.middle-3.label": "중학 3학년",
  "level.middle-3.short": "중3",
  "level.high-1.label": "고등 1학년",
  "level.high-1.short": "고1",
  "level.high-2.label": "고등 2학년",
  "level.high-2.short": "고2",
  "level.high-3.label": "고등 3학년",
  "level.high-3.short": "고3",

  // 일본어 코스 단계 (JLPT)
  "level.jlpt-n5.label": "JLPT N5",
  "level.jlpt-n5.short": "N5",
  "level.jlpt-n4.label": "JLPT N4",
  "level.jlpt-n4.short": "N4",
  "level.jlpt-n3.label": "JLPT N3",
  "level.jlpt-n3.short": "N3",
  "level.jlpt-n2.label": "JLPT N2",
  "level.jlpt-n2.short": "N2",
  "level.jlpt-n1.label": "JLPT N1",
  "level.jlpt-n1.short": "N1",
} as const;

/** 문구 키. 한국어 표가 기준이다 */
export type StringKey = keyof typeof ko;

/** 화면 문구는 한국어 한 벌이다 */
export const STRINGS = ko;
