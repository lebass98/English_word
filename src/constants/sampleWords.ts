export interface Word {
  id: string;
  word: string;
  phonetic: string;
  pos: string; // 품사 (예: "ADJ. 형용사")
  meanings: string[];
  subMeaning?: string;
  example: string;
  exampleKo: string;
  mnemonic: string; // 연상 암기 팁
  imageUrl: string;
  imageTag: string; // 이미지 하단 칩 텍스트
}

export const SAMPLE_WORDS: Word[] = [
  {
    id: "innocent",
    word: "innocent",
    phonetic: "/ˈɪnəsnt/",
    pos: "ADJ. 형용사",
    meanings: ["죄 없는, 결백한"],
    subMeaning: "순진한",
    example: 'He was found innocent of all charges.',
    exampleKo: "그는 모든 혐의에 대해 결백함이 밝혀졌다.",
    mnemonic: '"이 녀석 안 썼(innocent)다고! 죄가 없다며 억울해하는 모습"',
    imageUrl:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuBlxMq93rhYZfQW7o2WCA_Ji6JMz5UuMiCW9xS_EL5uM-XAXy1Q0uCzDgGHxUJzGGvH6QGYxJN7-Pxk_LX_JNYl0QAx7apodGuWhG5zQjbAFu5o7f9dXtMrCifa2B2-Q9bDJ6vTwD2ooRFe-0JorpyWTmL3-HDMcVjakK7D1xn9f2Ac_7qp6Xn5lYomnOT_urVwng7jBEspMOWZD-nKAUjUu8CvXU0HVD2-mQzU8QaoYVF-bxMoREKJ",
    imageTag: "연상 웹툰 #104",
  },
];
