import math
import re
from collections import Counter


class NaiveBayesClassifier:

    def __init__(self, alpha=1.0):
        self.alpha = alpha
        self.classes = []
        self.class_priors = {}
        self.word_counts = {}
        self.class_word_totals = {}
        self.vocab = set()

    def fit(self, X, y):
        self.classes = list(set(y))
        self.word_counts = {c: Counter() for c in self.classes}
        self.class_word_totals = {c: 0 for c in self.classes}
        self.vocab = set()
        class_doc_counts = Counter()

        for text, label in zip(X, y):
            class_doc_counts[label] += 1
            for w in self._tokenize(text):
                self.word_counts[label][w] += 1
                self.class_word_totals[label] += 1
                self.vocab.add(w)

        n = len(y)
        self.class_priors = {c: math.log(class_doc_counts[c] / n) for c in self.classes}
        return self

    def predict(self, X):
        return [self._predict_one(text) for text in X]

    def _predict_one(self, text):
        V = len(self.vocab)
        best_class, best_score = None, float("-inf")

        for c in self.classes:
            score = self.class_priors[c]
            for w in self._tokenize(text):
                count = self.word_counts[c].get(w, 0)
                total = self.class_word_totals[c]
                prob = (count + self.alpha) / (total + self.alpha * V)
                score += math.log(prob)
            if score > best_score:
                best_score, best_class = score, c

        return best_class

    def score(self, X_test, y_test):
        predictions = self.predict(X_test)
        correct = sum(1 for p, t in zip(predictions, y_test) if p == t)
        return correct / len(y_test)

    @staticmethod
    def _tokenize(text):
        return re.findall(r"\w+", text.lower())
