import { ImageSourcePropType } from "react-native";

// "y" 로 시작하는 단어 그림. scripts/sync_word_images.py 가 만든다 (손으로 고치지 않는다)
export const IMAGES_Y: Record<string, ImageSourcePropType> = {
  yell: require("../../../assets/words/y/yell.png"),
};
