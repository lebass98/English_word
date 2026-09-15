import { getVocab, type Vocab } from "../constants/words";
import { gradesOf } from "../constants/grades";
import { STUDY_LANGS, type StudyLangId } from "../constants/languages";
import { translate } from "../i18n";
import type { UiLangId } from "../i18n/strings";
import { WORD_IMAGES } from "../constants/wordImages";

/**
 * 연상 그림이 아직 없는 단어를 세는 임시 도구.
 *
 * 그림을 다 그릴 때까지만 홈 코스 카드에 "300개 미완료"처럼 띄워 둔다.
 * 그림이 다 채워지면 이 파일과 쓰는 곳을 함께 지운다.
 *
 * 등록표(WORD_IMAGES)를 그 자리에서 세므로, 그림을 새로 등록하면
 * Fast Refresh 로 화면의 숫자가 곧바로 줄어든다.
 */

/**
 * 지금 등록된 그림 수. 화면에서 memo·목록 갱신 조건으로 쓴다.
 * 그림이 새로 등록되면 이 값이 바뀌어서 붙잡아 둔 개수도 다시 센다
 */
export function registeredImageCount(): number {
  return Object.keys(WORD_IMAGES).length;
}

/** 그림 조회 규칙은 학습 화면과 같아야 한다 */
function hasImage(word: { id: string; word: string; conceptId: string }) {
  return Boolean(WORD_IMAGES[word.conceptId] ?? WORD_IMAGES[word.word]);
}

export interface ImageCoverage {
  total: number;
  made: number;
  missing: number;
}

/** 코스 하나의 그림 현황 */
export function imageCoverageOf(vocab: Vocab, levelId: string): ImageCoverage {
  const words = vocab.byLevel[levelId] ?? [];
  let made = 0;
  for (const w of words) if (hasImage(w)) made += 1;
  return { total: words.length, made, missing: words.length - made };
}

/** 낱말 묶음(유닛 등)의 그림 현황 */
export function imageCoverageOfWords(
  words: { id: string; word: string; conceptId: string }[],
): ImageCoverage {
  let made = 0;
  for (const w of words) if (hasImage(w)) made += 1;
  return { total: words.length, made, missing: words.length - made };
}

/** 지금 학습 언어 전체의 그림 현황 */
export function imageCoverageAll(vocab: Vocab): ImageCoverage {
  let total = 0;
  let made = 0;
  for (const level of vocab.levels) {
    const c = imageCoverageOf(vocab, level.id);
    total += c.total;
    made += c.made;
  }
  return { total, made, missing: total - made };
}

/* ── 현황판용 집계 ─────────────────────────────────────────────
   지금 고른 학습 언어만 보는 위 함수들과 달리, 아래는 모든 학습 언어의
   모든 코스를 한 번에 훑는다. 그림 현황판(app/image-status.tsx) 전용이다.
   그림을 다 채우면 이 파일과 현황판을 함께 지운다. */

/** 유닛 하나의 현황. words 는 아직 그리지 않은 낱말들이다 */
export interface BoardUnit {
  no: number;
  total: number;
  missing: number;
  words: string[];
}

/** 코스 하나의 현황 */
export interface BoardCourse {
  /** 코스를 가리키는 고유 키 (en:high-1). 화면에서 펼침 상태를 기억하는 데 쓴다 */
  key: string;
  langId: StudyLangId;
  langName: string;
  label: string;
  total: number;
  made: number;
  missing: number;
  units: BoardUnit[];
}

export interface ImageBoard extends ImageCoverage {
  courses: BoardCourse[];
}

/**
 * 모든 학습 언어 × 모든 코스의 그림 현황.
 *
 * 단어 수천 개를 훑으므로 화면에서는 useMemo 로 감싸고,
 * 등록된 그림 수(registeredImageCount)를 조건에 넣어 새 그림이 등록되면
 * 다시 세도록 한다.
 */
export function imageBoard(uiLang: UiLangId): ImageBoard {
  const courses: BoardCourse[] = [];
  let total = 0;
  let made = 0;

  for (const langId of STUDY_LANGS) {
    const vocab = getVocab(langId, uiLang);
    const langName = translate(uiLang, `studyLang.${langId}` as never) || langId;

    for (const grade of gradesOf(langId, uiLang)) {
      // 아직 단어를 안 넣은 코스는 현황판에 빈 줄로 남기지 않는다
      const cover = imageCoverageOf(vocab, grade.id);
      if (cover.total === 0) continue;

      const units = vocab.unitsOf(grade.id).map((unit) => {
        const missingWords = unit.words.filter((w) => !hasImage(w));
        return {
          no: unit.unitNo,
          total: unit.words.length,
          missing: missingWords.length,
          words: missingWords.map((w) => w.word),
        };
      });

      courses.push({
        key: `${langId}:${grade.id}`,
        langId,
        langName,
        label: grade.label,
        ...cover,
        units,
      });
      total += cover.total;
      made += cover.made;
    }
  }

  return { total, made, missing: total - made, courses };
}
