import { ImageSourcePropType } from "react-native";

// "q" 로 시작하는 단어 그림. scripts/sync_word_images.py 가 만든다 (손으로 고치지 않는다)
export const IMAGES_Q: Record<string, ImageSourcePropType> = {
  quarter: require("../../../assets/words/q/quarter.png"),
  quiet: require("../../../assets/words/q/quiet.png"),
  quit: require("../../../assets/words/q/quit.png"),
  quite: require("../../../assets/words/q/quite.png"),
};
