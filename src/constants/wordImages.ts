import { ImageSourcePropType } from "react-native";

/**
 * 단어별 연상 이미지 모음.
 *
 * 열쇠는 단어의 철자(= 뜻을 가리키는 conceptId)다. 그림은 철자 하나에 한 장이고,
 * 학년·코스는 철자 목록만 가지므로 같은 철자는 어느 과정에서든 같은 그림을 쓴다.
 *
 * 그림은 assets/words/<첫 글자>/<철자>.png 에 두고, 등록은 글자별 파일
 * (wordImagesByLetter/<글자>.ts) 에 나눠 적는다. 여러 컴퓨터가 알파벳 범위를
 * 나눠 그림을 그려도 등록 파일끼리 충돌하지 않게 하려는 것이다.
 *
 * 이 파일과 글자별 파일은 scripts/sync_word_images.py 가 만든다. 손으로 고치지 않는다.
 */
import { IMAGES_A } from "./wordImagesByLetter/a";
import { IMAGES_B } from "./wordImagesByLetter/b";
import { IMAGES_C } from "./wordImagesByLetter/c";
import { IMAGES_D } from "./wordImagesByLetter/d";
import { IMAGES_E } from "./wordImagesByLetter/e";
import { IMAGES_F } from "./wordImagesByLetter/f";
import { IMAGES_G } from "./wordImagesByLetter/g";
import { IMAGES_H } from "./wordImagesByLetter/h";
import { IMAGES_I } from "./wordImagesByLetter/i";
import { IMAGES_J } from "./wordImagesByLetter/j";
import { IMAGES_K } from "./wordImagesByLetter/k";
import { IMAGES_L } from "./wordImagesByLetter/l";
import { IMAGES_M } from "./wordImagesByLetter/m";
import { IMAGES_N } from "./wordImagesByLetter/n";
import { IMAGES_O } from "./wordImagesByLetter/o";
import { IMAGES_P } from "./wordImagesByLetter/p";
import { IMAGES_Q } from "./wordImagesByLetter/q";
import { IMAGES_R } from "./wordImagesByLetter/r";
import { IMAGES_S } from "./wordImagesByLetter/s";
import { IMAGES_T } from "./wordImagesByLetter/t";
import { IMAGES_U } from "./wordImagesByLetter/u";
import { IMAGES_V } from "./wordImagesByLetter/v";
import { IMAGES_W } from "./wordImagesByLetter/w";
import { IMAGES_X } from "./wordImagesByLetter/x";
import { IMAGES_Y } from "./wordImagesByLetter/y";
import { IMAGES_Z } from "./wordImagesByLetter/z";
import { IMAGES_OTHER } from "./wordImagesByLetter/_";

export const WORD_IMAGES: Record<string, ImageSourcePropType> = {
  ...IMAGES_A,
  ...IMAGES_B,
  ...IMAGES_C,
  ...IMAGES_D,
  ...IMAGES_E,
  ...IMAGES_F,
  ...IMAGES_G,
  ...IMAGES_H,
  ...IMAGES_I,
  ...IMAGES_J,
  ...IMAGES_K,
  ...IMAGES_L,
  ...IMAGES_M,
  ...IMAGES_N,
  ...IMAGES_O,
  ...IMAGES_P,
  ...IMAGES_Q,
  ...IMAGES_R,
  ...IMAGES_S,
  ...IMAGES_T,
  ...IMAGES_U,
  ...IMAGES_V,
  ...IMAGES_W,
  ...IMAGES_X,
  ...IMAGES_Y,
  ...IMAGES_Z,
  ...IMAGES_OTHER,
};
