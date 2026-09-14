import { ImageSourcePropType } from "react-native";

// "k" 로 시작하는 단어 그림. scripts/sync_word_images.py 가 만든다 (손으로 고치지 않는다)
export const IMAGES_K: Record<string, ImageSourcePropType> = {
  kind: require("../../../assets/words/k/kind.png"),
  kindergarten: require("../../../assets/words/k/kindergarten.png"),
  knee: require("../../../assets/words/k/knee.png"),
};
