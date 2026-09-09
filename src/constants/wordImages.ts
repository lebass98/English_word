import { ImageSourcePropType } from "react-native";

/**
 * 단어별 로컬 연상 이미지 레지스트리.
 * assets/words/<단어id>.png 로 이미지를 넣고 여기에 등록하면
 * 원격 URL 대신 로컬 이미지가 우선 사용된다.
 */
export const WORD_IMAGES: Record<string, ImageSourcePropType> = {
  innocent: require("../../assets/words/innocent.png"),
};
