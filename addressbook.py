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
    
    # Ищем добавочный номер в ЛЮБОМ виде
    ext = ""
    phone_without_ext = phone
    
    # Расширенный поиск добавочного номера
    ext_patterns = [
        r'(доб\.?\s*)(\d+)',  # доб.1234 или доб 1234
        r'(д\.?\s*)(\d+)',    # д.1234 или д 1234
        r'(ext\.?\s*)(\d+)',  # ext.1234
        r'(\d+)(?=\s*$)'      # цифры в конце строки (может быть добавочный)
    ]
    
    for pattern in ext_patterns:
        ext_match = re.search(pattern, phone, re.IGNORECASE)
        if ext_match:
            # Если это последний паттерн - проверяем, что это действительно добавочный
            if pattern == r'(\d+)(?=\s*$)' and len(ext_match.group(1)) <= 4:
                ext = f" доб.{ext_match.group(1)}"
                # Удаляем эти цифры из конца строки
                phone_without_ext = re.sub(r'\d+\s*$', '', phone)
                break
            elif pattern != r'(\d+)(?=\s*$)':
                ext = f" доб.{ext_match.group(2)}"
                # Удаляем ВСЮ часть с добавочным номером
                phone_without_ext = re.sub(r'[\s,\(\)]*доб\.?\s*\d+|[\s,\(\)]*д\.?\s*\d+|[\s,\(\)]*ext\.?\s*\d+', '', phone, flags=re.IGNORECASE)
                break
    
    # Извлекаем ВСЕ цифры из оставшейся части
    all_digits = re.sub(r'\D', '', phone_without_ext)
    
    # Если цифр больше 10, возможно, это добавочный прилип к основному номеру
    if len(all_digits) > 11:
        # Пробуем найти 10-11 цифр подряд (основной номер)
        main_match = re.search(r'\d{10,11}', phone_without_ext)
        if main_match:
            all_digits = main_match.group(0)
    
    # Форматируем номер
    if len(all_digits) >= 10:
        # Берем последние 10 цифр для основного номера
        main_digits = all_digits[-10:]
        formatted = f"+7({main_digits[:3]}){main_digits[3:6]}-{main_digits[6:8]}-{main_digits[8:]}"
        return formatted + ext
    else:
        # Если номер не удалось распознать, возвращаем как есть
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
