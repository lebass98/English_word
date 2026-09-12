/**
 * 화면에 보이는 문구 모음 (표시 언어별).
 *
 * 표시 언어(화면의 말)와 학습 언어(배우는 말)는 서로 다른 축이다.
 * 한국인이 한국어 화면으로 영어를 배울 수도 있고,
 * 일본인이 일본어 화면으로 영어를 배울 수도 있다.
 *
 * 단어 뜻·예문 해석처럼 학습 콘텐츠에 속하는 번역은
 * src/data/<학습언어>/tr/<표시언어>.json 에 따로 둔다.
 * 빠진 문구는 한국어로 자동 대체되므로 한 번에 다 채우지 않아도 된다.
 */

/** 표시 언어 (앱 화면의 말) */
export const UI_LANGS = ["ko", "ja"] as const;
export type UiLangId = (typeof UI_LANGS)[number];

/** 언어 고르는 자리에 쓸 이름. 각 언어는 제 나라 말로 적는다 */
export const UI_LANG_NAMES: Record<UiLangId, string> = {
  ko: "한국어",
  ja: "日本語",
};

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
  "study.save": "저장",
  "study.saved": "저장됨",
  "study.saveToggle": "단어장에 담기 빼기",
  "study.unsure": "헷갈려요",
  "study.known": "외웠어요",

  // 단어장
  "wordbook.title": "단어장",
  "wordbook.all": "전체",
  "wordbook.known": "외운 단어",
  "wordbook.unsure": "헷갈리는 단어",
  "wordbook.saved": "저장한 단어",
  "wordbook.emptyTitle": "단어장이 아직 비어 있어요",
  "wordbook.emptyDesc": "학습한 단어가 여기에 차곡차곡 쌓여요",
  "wordbook.goStudy": "학습하러 가기",
  "wordbook.noRecords": "아직 기록된 단어가 없어요",
  "wordbook.noKnown": "아직 외운 단어가 없어요",
  "wordbook.noUnsure": "헷갈린다고 표시한 단어가 없어요",
  "wordbook.noSaved": "저장한 단어가 없어요",

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
  "settings.language": "언어",
  "settings.uiLang": "표시 언어",
  "settings.uiLangDesc": "앱 화면에 쓰는 말이에요",

  // 학습 언어 이름
  "studyLang.en": "영어",
  "studyLang.ja": "일본어",

  // 품사 이름
  "pos.noun": "명사",
  "pos.verb": "동사",
  "pos.adj": "형용사",
  "pos.adv": "부사",
  "pos.prep": "전치사",
  "pos.conj": "접속사",
  "pos.pron": "대명사",
  "pos.interj": "감탄사",
  "pos.phrase": "구",
  "pos.aux": "조동사",
  "pos.i-adj": "い형용사",
  "pos.na-adj": "な형용사",
  "pos.prenominal": "연체사",
  "pos.counter": "조수사",

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

const ja: Partial<Record<StringKey, string>> = {
  "common.back": "戻る",
  "common.backArrow": "← 戻る",
  "common.cancel": "キャンセル",
  "common.delete": "削除",
  "common.on": "オン",
  "common.off": "オフ",

  "nav.home": "ホーム",
  "nav.wordbook": "単語帳",
  "nav.settings": "設定",

  "home.myCourse": "マイコース",
  "home.todayRecord": "今日の記録",
  "home.seenToday": "今日見た単語",
  "home.knownToday": "今日覚えた単語",
  "home.streak": "連続学習",
  "home.days": "日",
  "home.reviewStart": "復習を始める",
  "home.firstWordPrompt": "今日の最初の単語を始めてみましょう",

  "continue.title": "続きから",
  "continue.resume": "続きから学習する",
  "continue.start": "学習を始める",

  "course.notStarted": "未学習",
  "course.studying": "学習中",

  "level.fallback": "コース",
  "level.preparing": "単語データを準備中です",

  "study.notFound": "単語が見つかりません",
  "study.hide": "隠す",
  "study.show": "見る",
  "study.example": "例文",
  "study.synonyms": "類義語",
  "study.etymology": "語源",
  "study.imagePreparing": "イメージを準備中",
  "study.prevWord": "前の単語",
  "study.nextWord": "次の単語",
  "study.autoAdvanceToggle": "自動送りのオン・オフ",
  "study.speak": "{word} の発音を聞く",
  "study.save": "保存",
  "study.saved": "保存済",
  "study.saveToggle": "単語帳に入れる・外す",
  "study.unsure": "あいまい",
  "study.known": "覚えた",

  "wordbook.title": "単語帳",
  "wordbook.all": "すべて",
  "wordbook.known": "覚えた単語",
  "wordbook.unsure": "あいまいな単語",
  "wordbook.saved": "保存した単語",
  "wordbook.emptyTitle": "単語帳はまだ空です",
  "wordbook.emptyDesc": "学習した単語がここにたまっていきます",
  "wordbook.goStudy": "学習しに行く",
  "wordbook.noRecords": "まだ記録された単語がありません",
  "wordbook.noKnown": "まだ覚えた単語がありません",
  "wordbook.noUnsure": "あいまいと記録した単語がありません",
  "wordbook.noSaved": "保存した単語がありません",

  "settings.title": "設定",
  "settings.myName": "名前",
  "settings.namePlaceholder": "名前を入力してください",
  "settings.studySettings": "学習の設定",
  "settings.autoAdvance": "自動送り",
  "settings.autoAdvanceDesc": "学習画面で次の単語へ自動で進みます",
  "settings.record": "学習の記録",
  "settings.noRecord": "まだ学習の記録がありません",
  "settings.resetProgress": "学習記録をリセット",
  "settings.resetConfirmTitle": "本当に削除しますか？",
  "settings.resetConfirmDesc":
    "覚えた単語と続きの位置がすべて消えます。続けますか？",

  "settings.recordSummary": "覚えた単語 {known}個 · あいまいな単語 {unsure}個",

  "settings.language": "言語",
  "settings.uiLang": "表示言語",
  "settings.uiLangDesc": "アプリの画面に使う言語です",
  "settings.studyLang": "学習言語",
  "settings.studyLangDesc": "何を学ぶか選んでください。絵はそのままで単語だけ変わります",

  "studyLang.en": "英語",
  "studyLang.ja": "日本語",

  "pos.noun": "名詞",
  "pos.verb": "動詞",
  "pos.adj": "形容詞",
  "pos.adv": "副詞",
  "pos.prep": "前置詞",
  "pos.conj": "接続詞",
  "pos.pron": "代名詞",
  "pos.interj": "感動詞",
  "pos.phrase": "句",
  "pos.aux": "助動詞",
  "pos.i-adj": "い形容詞",
  "pos.na-adj": "な形容詞",
  "pos.prenominal": "連体詞",
  "pos.counter": "助数詞",

  "a11y.unitProgress": "UNIT {unit}、{total}個中{known}個を記憶",
  "a11y.reviewWord": "{word} を復習する",
  "a11y.studyWord": "{word} を学習する",
  "a11y.courseNotStarted": "{label} 未学習",
  "a11y.courseProgress": "{label} 学習中、{total}個中{known}個を記憶",
  "course.wordCount": "{count}語",

  "level.middle-1.label": "中学1年",
  "level.middle-1.short": "中1",
  "level.middle-2.label": "中学2年",
  "level.middle-2.short": "中2",
  "level.middle-3.label": "中学3年",
  "level.middle-3.short": "中3",
  "level.high-1.label": "高校1年",
  "level.high-1.short": "高1",
  "level.high-2.label": "高校2年",
  "level.high-2.short": "高2",
  "level.high-3.label": "高校3年",
  "level.high-3.short": "高3",

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
};

export const STRINGS: Record<UiLangId, Partial<Record<StringKey, string>>> = {
  ko,
  ja,
};
