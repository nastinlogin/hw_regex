from pprint import pprint
import csv
import re

# Читаем адресную книгу
with open("phonebook_raw.csv", encoding="utf-8") as f:
    rows = csv.reader(f, delimiter=",")
    contacts_list = list(rows)

# Функция для обработки ФИО
def process_names(contact):
    """Обработка ФИО с использованием регулярных выражений"""
    # Объединяем первые три поля
    name_parts = " ".join(contact[:3]).strip()
    
    # Регулярка для поиска всех слов (фамилия, имя, отчество)
    names = re.findall(r'[А-ЯЁ][а-яё]+', name_parts)
    
    # Заполняем поля
    while len(names) < 3:
        names.append("")
    
    return names + contact[3:]

# Функция для обработки телефонов (ИСПРАВЛЕННАЯ)
def process_phone(phone):
    """Обработка телефона с помощью регулярных выражений"""
    if not phone:
        return ""
    
    # Отделяем добавочный номер
    ext = ""
    phone_without_ext = phone
    
    ext_match = re.search(r'доб\.?\s*(\d+)', phone, re.IGNORECASE)
    if ext_match:
        ext = f" доб.{ext_match.group(1)}"
        # Удаляем часть с добавочным номером из строки
        phone_without_ext = re.sub(r'доб\.?\s*\d+', '', phone, flags=re.IGNORECASE)
    
    # Извлекаем все цифры из основного номера
    digits = re.sub(r'\D', '', phone_without_ext)
    
    # Форматируем номер
    if len(digits) >= 10:
        # Берем последние 10 цифр для основного номера
        main_digits = digits[-10:]
        formatted = f"+7({main_digits[:3]}){main_digits[3:6]}-{main_digits[6:8]}-{main_digits[8:]}"
        return formatted + ext
    else:
        return phone

# Основная логика обработки
header = contacts_list[0]
contacts_processed = [header]

# Обрабатываем каждый контакт
for contact in contacts_list[1:]:
    # Обработка ФИО
    contact = process_names(contact)
    
    # Обработка телефона
    contact[5] = process_phone(contact[5])
    
    # Добавляем в список
    contacts_processed.append(contact)

# Объединение дублей
contacts_dict = {}
for contact in contacts_processed[1:]:
    key = (contact[0].lower(), contact[1].lower())
    if key not in contacts_dict:
        contacts_dict[key] = contact
    else:
        # Объединяем записи
        for i in range(len(contact)):
            if contact[i] and not contacts_dict[key][i]:
                contacts_dict[key][i] = contact[i]

# Финальный результат
final_result = [header] + list(contacts_dict.values())

# Сохраняем результат
with open("phonebook.csv", "w", encoding="utf-8", newline='') as f:
    datawriter = csv.writer(f, delimiter=',')
    datawriter.writerows(final_result)

print("Обработка завершена! Результат сохранен в phonebook.csv")
print("\nФинальный результат:")
pprint(final_result)
