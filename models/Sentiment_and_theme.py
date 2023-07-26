import numpy as np
import re
from transformers import BertTokenizer, BertForSequenceClassification
import torch


class BertPredict:

    def __init__(
            self,
            model_save_path_theme='bert_theme.pth',
            model_save_path_sentim='bert_sentiment.pth',
            model_path='cointegrated/rubert-tiny',
            tokenizer_path='cointegrated/rubert-tiny'
    ):
        """
        :param model_save_path_theme: путь к весам модели для классификации по темам
        :param model_save_path_sentim: путь к весам модели для классификации по эмоциональной окраске
        :param model_path: путь до рускоязычной обученной модели Bert *лучше не менять*
        :param tokenizer_path: путь к токенайзеру текста для этой модели *лучше не менять*
        """

        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.tokenizer = BertTokenizer.from_pretrained(tokenizer_path)
        self.max_len = 512

        # загрузка модели для классификации по темам
        self.model_theme = BertForSequenceClassification.from_pretrained(model_path)
        self.out_features = self.model_theme.bert.encoder.layer[1].output.dense.out_features
        self.model_theme.classifier = torch.nn.Linear(self.out_features, 13)
        self.model_theme.to(self.device)
        self.model_theme = torch.load(model_save_path_theme, map_location=torch.device(self.device))

        self.target_univers_theme = {
            0: 'Экономика',
            1: 'Спорт',
            2: 'Из жизни',
            3: 'Интернет и СМИ',
            4: 'Культура',
            5: 'Дом',
            6: 'Бывший СССР',
            7: 'Мир',
            8: 'Наука и техника',
            9: 'Путешествия',
            10: 'Россия',
            11: 'Силовые структуры',
            12: 'Ценности'
        }

        # загрузка модели для классификации по эмоциональной окраске
        self.model_sentim = BertForSequenceClassification.from_pretrained(model_path)
        self.out_features = self.model_sentim.bert.encoder.layer[1].output.dense.out_features
        self.model_sentim.classifier = torch.nn.Linear(self.out_features, 3)
        self.model_sentim.to(self.device)
        self.model_sentim = torch.load(model_save_path_sentim, map_location=torch.device(self.device))

        self.target_univers_sentim = {
            0: 'Негативный',
            1: 'Нейтральный',
            2: 'Позитивный'
        }

    def clean_text(self, txt):

        """
        Очистка текста от лишнего, приведение к нижнему регистру
        """

        if txt is np.NaN or txt == '' or len(txt) == '0' or txt is None:
            return None
        txt = re.sub('[^a-zA-Zа-яА-Я ]', ' ', str(txt).lower())
        txt = re.sub('\s+', ' ', txt)
        txt = txt.replace('.', '')
        txt = re.sub('\n', ' ', txt)
        return txt

    def predict(self, text, sentim=True, theme=True):

        """
        Делаем предсказание для text - текста,
        если нужно сделать предсказание только на темы или только на эмоциональную окраску
        то для ненужной классификации ставим флаг False соответственно
        """

        # Очистка и кодирование текста
        # print(f"predict text: {text}")
        text = self.clean_text(text)
        if not text or text is None:
            return None, None
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            truncation=True,
            padding='max_length',
            return_attention_mask=True,
            return_tensors='pt',
        )

        out = {
              'text': text,
              'input_ids': encoding['input_ids'].flatten(),
              'attention_mask': encoding['attention_mask'].flatten()
          }

        input_ids = out["input_ids"].to(self.device)
        attention_mask = out["attention_mask"].to(self.device)

        class_sentim = None
        class_theme = None

        # Предсказание эмоциональной окраски
        if sentim:
            outputs = self.model_sentim(
                input_ids=input_ids.unsqueeze(0),
                attention_mask=attention_mask.unsqueeze(0)
            )
            prediction = torch.argmax(outputs.logits, dim=1).cpu().numpy()[0]
            class_sentim = self.target_univers_sentim[prediction]

        # Предсказание темы
        if theme:
            outputs = self.model_theme(
                input_ids=input_ids.unsqueeze(0),
                attention_mask=attention_mask.unsqueeze(0)
            )
            prediction = torch.argmax(outputs.logits, dim=1).cpu().numpy()[0]
            class_theme = self.target_univers_theme[prediction]

        return class_sentim, class_theme
