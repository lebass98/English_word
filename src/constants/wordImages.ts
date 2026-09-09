import { ImageSourcePropType } from "react-native";

/**
 * 단어별 로컬 연상 이미지 레지스트리.
 * assets/words/<단어>.png 로 이미지를 넣고 여기에 등록하면
 * 원격 URL 대신 로컬 이미지가 우선 사용된다.
 */
export const WORD_IMAGES: Record<string, ImageSourcePropType> = {
  // 중학교 1학년 1Unit (20개 단어)
  beyond: require("../../assets/words/beyond.png"),
  either: require("../../assets/words/either.png"),
  neither: require("../../assets/words/neither.png"),
  behind: require("../../assets/words/behind.png"),
  bound: require("../../assets/words/bound.png"),
  below: require("../../assets/words/below.png"),
  without: require("../../assets/words/without.png"),
  belong: require("../../assets/words/belong.png"),
  replace: require("../../assets/words/replace.png"),
  along: require("../../assets/words/along.png"),
  except: require("../../assets/words/except.png"),
  become: require("../../assets/words/become.png"),
  since: require("../../assets/words/since.png"),
  pretend: require("../../assets/words/pretend.png"),
  whether: require("../../assets/words/whether.png"),
  toward: require("../../assets/words/toward.png"),
  while: require("../../assets/words/while.png"),
  unless: require("../../assets/words/unless.png"),
  deserve: require("../../assets/words/deserve.png"),
  teenager: require("../../assets/words/teenager.png"),

  // 단어 ID 매핑 (m1-1 ~ m1-20)
  "m1-1": require("../../assets/words/beyond.png"),
  "m1-2": require("../../assets/words/either.png"),
  "m1-3": require("../../assets/words/neither.png"),
  "m1-4": require("../../assets/words/behind.png"),
  "m1-5": require("../../assets/words/bound.png"),
  "m1-6": require("../../assets/words/below.png"),
  "m1-7": require("../../assets/words/without.png"),
  "m1-8": require("../../assets/words/belong.png"),
  "m1-9": require("../../assets/words/replace.png"),
  "m1-10": require("../../assets/words/along.png"),
  "m1-11": require("../../assets/words/except.png"),
  "m1-12": require("../../assets/words/become.png"),
  "m1-13": require("../../assets/words/since.png"),
  "m1-14": require("../../assets/words/pretend.png"),
  "m1-15": require("../../assets/words/whether.png"),
  "m1-16": require("../../assets/words/toward.png"),
  "m1-17": require("../../assets/words/while.png"),
  "m1-18": require("../../assets/words/unless.png"),
  "m1-19": require("../../assets/words/deserve.png"),
  "m1-20": require("../../assets/words/teenager.png"),

  // 기타 단어
  innocent: require("../../assets/words/innocent.png"),
};
