import { useMemo } from "react";
import { translate } from "../i18n";
import { useAppStore } from "../stores/useAppStore";
import type { StudyLangId } from "./languages";
import { getVocab } from "./words";

/**
 * 화면에 그릴 코스 단계 하나.
 *
 * 이름은 표시 언어에 따라 달라지므로 데이터에 넣어 두지 않고 여기서 붙인다.
 * (한국어면 "중학 1학년", 일본어면 "中学1年")
 */
export interface Grade {
  id: string;
  /** 홈·유닛 목록에서 쓰는 전체 이름 */
  label: string;
  /** 학습 화면 헤더처럼 좁은 자리에서 쓰는 짧은 이름 */
  short: string;
  /** 해당 단계의 전체 단어 수 */
  totalWords: number;
}

/** 지금 학습 언어의 단계 목록 */
export function gradesOf(studyLang: StudyLangId): Grade[] {
  const vocab = getVocab(studyLang);
  return vocab.levels.map((level) => ({
    id: level.id,
    // 아직 이름을 안 채운 단계는 키가 그대로 나오지 않도록 단계 id 를 쓴다
    label: translate(`level.${level.id}.label` as never) || level.id,
    short: translate(`level.${level.id}.short` as never) || level.id,
    totalWords: vocab.totalOf(level.id),
  }));
}

/** 화면에서 쓰는 단계 목록. 학습 언어를 바꾸면 알아서 다시 그려진다 */
export function useGrades(): Grade[] {
  const studyLang = useAppStore((s) => s.studyLang);
  return useMemo(() => gradesOf(studyLang), [studyLang]);
}

/** 단계 하나만 필요할 때 */
export function useGrade(gradeId: string | undefined): Grade | undefined {
  const grades = useGrades();
  return grades.find((g) => g.id === gradeId);
}
