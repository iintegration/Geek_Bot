from typing import List

import nltk
import numpy as np
import re
import spacy
from nltk.corpus import stopwords

from natasha import (
    Segmenter,
    MorphVocab,

    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,

    PER,
    Doc
)

nltk.download('stopwords')


class Model:
    def __init__(self, model_path=""):
        self.model_path = model_path

        self.nlp = spacy.load(model_path)

        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()
        self.emb = NewsEmbedding()
        self.morph_tagger = NewsMorphTagger(self.emb)
        self.syntax_parser = NewsSyntaxParser(self.emb)

    def __natasha_lemmant(self, input_str):

        doc = Doc(input_str)
        doc.segment(self.segmenter)
        doc.tag_morph(self.morph_tagger)
        doc.parse_syntax(self.syntax_parser)
        for token in doc.tokens:
            token.lemmatize(self.morph_vocab)

        result = ' '.join([_.lemma for _ in doc.tokens])
        return result

    def __clear_string(self, s, stop_words):  # Функция для очистки
        # print(re.sub(r'[^а-яА-ЯёЁa-zA-Z]', ' ', str(s).lower()).split())
        s = ' '.join(
            [val for val in re.sub(r'[^а-яА-ЯёЁa-zA-Z]', ' ', str(s).lower()).split() if not val in stop_words])
        # s = ' '.join([val for val in re.sub(r'[^а-яА-ЯёЁ]', ' ', str(s).lower()).split() if not val in stop_words])
        return s

    def __preprocessing(self, answer):
        stop_words = list(stopwords.words('russian'))

        text_list = []

        for i in range(len(answer)):
            txt = answer[i]['question_2'] + " " + answer[i]['question_3'] + " " + answer[i]['question_4'] + " " + \
                  answer[i]['question_5']
            txt = self.__clear_string(txt, stop_words)
            txt = self.__natasha_lemmant(txt)
            text_list.append(txt)

        return text_list

    def predict(self, answers: list) -> List[int]:

        # Очищаем текст
        answers = self.__preprocessing(answers)

        labels = []

        for ans in answers:
            proba = self.nlp(ans).cats
            # sum_proba = sum(proba)
            # proba = np.array([el/sum_proba for el in proba])

            labels.append(int(max(proba, key=proba.get)))

        return labels
