import { gradesOf } from "../constants/grades";
import { STUDY_LANGS, type StudyLangId } from "../constants/languages";
import {
  hasWordImage,
  replacedImageOf,
  type ReplacedImage,
} from "../constants/wordImages";
import { getVocab, type Word } from "../constants/words";
import type { UiLangId } from "../i18n/strings";

/**
 * 그림 현황 화면(app/image-status.tsx)이 쓰는 낱말 목록.
 *
 * 순차 보기와 제작 현황표가 같은 목록을 나눠 쓴다. 현황표에서 그림을 누르면
 * 같은 칸 id 로 순차 보기를 그 자리에서 연다.
 */

/** 넘겨 볼 칸 하나 */
export interface Slide {
  /** 화면 안에서 칸을 가리키는 고유 키 (en:middle-1:en-m1-1) */
  id: string;
  word: Word;
  /** 그림 한 장을 함께 쓰는 낱말끼리 같은 값 */
  imageKey: string;
  courseKey: string;
  /** 고1, N5 같은 짧은 코스 이름 */
  course: string;
  unitNo: number;
  /** 유닛 안에서 몇 번째인지 (1부터) */
  noInUnit: number;
  unitSize: number;
  has: boolean;
  replaced: ReplacedImage | null;
}

export interface SlideCourse {
  key: string;
  /** 짧은 이름 (고1) */
  label: string;
  /** 전체 이름 (고등 1학년) */
  fullLabel: string;
}

/** 모든 학습 언어 × 모든 코스의 낱말을 코스 → 유닛 → 낱말 순서로 늘어놓는다 */
export function buildSlides(uiLang: UiLangId) {
  const slides: Slide[] = [];
  const courses: SlideCourse[] = [];

  for (const langId of STUDY_LANGS as readonly StudyLangId[]) {
    const vocab = getVocab(langId, uiLang);
    for (const grade of gradesOf(langId, uiLang)) {
      const units = vocab.unitsOf(grade.id);
      if (units.length === 0) continue;
      const key = `${langId}:${grade.id}`;
      courses.push({ key, label: grade.short, fullLabel: grade.label });

      for (const unit of units) {
        unit.words.forEach((word, i) => {
          slides.push({
            id: `${key}:${word.id}`,
            word,
            imageKey: word.conceptId || word.word,
            courseKey: key,
            course: grade.short,
            unitNo: unit.unitNo,
            noInUnit: i + 1,
            unitSize: unit.words.length,
            has: hasWordImage(word),
            replaced: replacedImageOf(word),
          });
        });
      }
    }
  }
  return { slides, courses };
}
