from dataclasses import dataclass, field
from typing import List
from datetime import datetime
from transformers import pipeline
import re
import uuid


@dataclass
class Transaction:
    """
        Класс для представления транзакции в системе.
        Attributes:
            id (str): Идентификатор операции
            timestamp: (datetime): Время операции
            user (str): Уникальный идентификатор пользователя
            amount (int): Стоимость операции
            type (str): Тип операции "Пополнение", "Списание", "Бонус"
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: str = ""
    amount: int = 0
    type: str = "Списание"


@dataclass
class Translation:
    """
        Класс для представления перевода в системе.

        Attributes:
            id (str): Идентификатор операции
            timestamp (datetime): Время опреции
            input_text (str): Оригинальный текст
            output_text (str): Переведенный текст
            source_lang (str): Язык оригинала
            target_lang (str): Язык для перевода
            cost (int): Стоимость перевода
        """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    input_text: str = ""
    output_text: str = ""
    source_lang: str = ""
    target_lang: str = ""
    cost: int = 1


@dataclass
class User:
    """
    Класс для представления пользователя в системе.

    Attributes:
        id (int): Уникальный идентификатор пользователя
        email (str): Email пользователя
        password (str): Пароль пользователя
        balance (int): Баланс пользователя
        requests (List[Translation]): Список событий пользователя
        transaсtions (List[Transaction]): Список транзакций пользователя
    """
    id: str
    email: str
    password: str
    balance: int = 0
    requests: List[Translation] = field(default_factory=list)
    transactions: List[Transaction] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._validate_email()
        self._validate_password()

    def _validate_email(self) -> None:
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(self.email):
            raise ValueError("Invalid email format")

    def _validate_password(self) -> None:
        if len(self.password) < 8:
            raise ValueError("Password must be at least 8 characters long")

    def add_request(self, translation: Translation) -> None:
        self.requests.append(translation)

    def get_requests(self) -> List[Translation]:
        return self.requests

    def get_transactions(self) -> List[Transaction]:
        return self.transactions

    def get_balance(self) -> int:
        return self.balance

    def can_afford(self, amount: int) -> bool:
        return self.balance >= amount

    def add_credits(self, amount: int, type="Пополнение"):
        self.balance += amount
        self.transactions.append(Transaction(user_id=self.id, amount=amount, type=type))

    def charge(self, amount: int) -> None:
        if self.balance < amount:
            raise ValueError("Недостаточно средств, пополните баланс")
        self.balance -= amount
        self.transactions.append(Transaction(user_id=self.id, amount=-amount, type="Списание"))


@dataclass
class Admin(User):
    """
    Класс администратора системы.
    """

    def approve_bonus(self, user: User, amount: int, type="Бонусные баллы") -> None:
        user.add_credits(amount, type=type)

    def view_all_transactions(self, users: List[User]) -> List[Transaction]:
        all_transactions = []
        for user in users:
            all_transactions.extend(user.get_transactions())
        return all_transactions

    def view_all_requests(self, users: List[User]) -> List[Translation]:
        all_requests = []
        for user in users:
            all_requests.extend(user.get_requests())
        return all_requests


@dataclass
class Model:
    """
    Класс для перевода.

    Attributes:
    name (str): Название модели

    """
    name: str = "Helsinki-NLP/opus-mt-en-fr"

    def translate(self, origin_text: str, source_lang: str, target_lang: str) -> str:
        translator = pipeline('translation', model=self.name)
        translation = translator(origin_text, src_lang=source_lang, tgt_lang=target_lang)[0]["translation_text"]
        return f"{translation} (переведено с {source_lang} на {target_lang})"


class TextValidationResult:
    """
    Класс результатов проверки текста.
    """

    def __init__(self, is_valid: bool, errors: List[str]):
        self.is_valid = is_valid
        self.errors = errors


@dataclass
class TranslationRequest:
    """
    Класс для выполнения запроса по переводу.

    Attributes:
    user (User): Идентификатор пользователя
    input_text (str): Оригинальный текст
    source_lang (str): Язык оригинала
    target_lang (str): Язык для перевода
    model (Model): Модель для перевода
    cost_per_traslation (int): Стоимость перевода
    """

    user: User
    input_text: str
    source_lang: str
    target_lang: str
    model: Model
    cost_per_translation: int = 1

    def validate_text(self) -> TextValidationResult:
        if not self.input_text or not isinstance(self.input_text, str):
            return TextValidationResult(False, ["Invalid or empty input text."])
        return TextValidationResult(True, [])

    def process(self):
        validation = self.validate_text()
        if not validation.is_valid:
            self.errors = validation.errors
            raise ValueError("Текст некорректен")

        if self.user.can_afford(self.cost_per_translation):
            output = self.model.translate(self.input_text, self.source_lang, self.target_lang)
            self.user.charge(self.cost_per_translation)
            translation = Translation(
                input_text=self.input_text,
                output_text=output,
                source_lang=self.source_lang,
                target_lang=self.target_lang,
                cost=self.cost_per_translation
            )
            self.user.add_request(translation)
            return output
        else:
            raise ValueError("Недостаточный баланс")


# === Пример использования ===

user = User(id="1", email="aghddlwxms@b.com", password="12hjjk3fgd")
admin = Admin(id="0", email="admin@b.com", password="admin123456")

admin.approve_bonus(user, 10)  # Пополнение баланса

model = Model()
req = TranslationRequest(user=user, input_text="Hello", source_lang="en", target_lang="fr", model=model)
result = req.process()

print(f"Результат перевода: {result}")
print(f"Баланс: {user.get_balance()}")
print(f"Транзакции: {user.get_transactions()}")
print(f"Переводы: {user.get_requests()}")