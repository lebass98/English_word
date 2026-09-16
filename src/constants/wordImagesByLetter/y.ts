import { ImageSourcePropType } from "react-native";

// "y" 로 시작하는 단어 그림. scripts/sync_word_images.py 가 만든다 (손으로 고치지 않는다)
export const IMAGES_Y: Record<string, ImageSourcePropType> = {
  yard: require("../../../assets/words/y/yard.png"),
  yawn: require("../../../assets/words/y/yawn.png"),
  yell: require("../../../assets/words/y/yell.png"),
  yet: require("../../../assets/words/y/yet.png"),
  yield: require("../../../assets/words/y/yield.png"),
};
