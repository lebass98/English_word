import { ImageSourcePropType } from "react-native";

// "k" 로 시작하는 단어 그림. scripts/sync_word_images.py 가 만든다 (손으로 고치지 않는다)
export const IMAGES_K: Record<string, ImageSourcePropType> = {
  "keep in mind": require("../../../assets/words/k/keep-in-mind.png"),
  "keep in touch": require("../../../assets/words/k/keep-in-touch.png"),
  kettle: require("../../../assets/words/k/kettle.png"),
  kill: require("../../../assets/words/k/kill.png"),
  kind: require("../../../assets/words/k/kind.png"),
  kindergarten: require("../../../assets/words/k/kindergarten.png"),
  knee: require("../../../assets/words/k/knee.png"),
  knowledge: require("../../../assets/words/k/knowledge.png"),
};
