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
    
    # Сохраняем исходный номер для отладки
    original_phone = phone
    
    # Ищем добавочный номер ТОЛЬКО если есть явный маркер (доб., д., ext.)
    ext = ""
    phone_without_ext = phone
    
    # Проверяем наличие добавочного номера только с явными маркерами
    ext_match = re.search(r'(доб\.?\s*|д\.?\s*|ext\.?\s*)(\d+)', phone, re.IGNORECASE)
    if ext_match:
        ext = f" доб.{ext_match.group(2)}"
        # Удаляем часть с добавочным номером (включая возможные запятые и пробелы)
        phone_without_ext = re.sub(
            r'[\s,\(\)]*?(?:доб\.?\s*|д\.?\s*|ext\.?\s*)\d+', 
            '', 
            phone, 
            flags=re.IGNORECASE
        )
    
    # Очищаем номер от лишних символов, но сохраняем цифры
    # Убираем всё, кроме цифр и знака +
    clean_phone = re.sub(r'[^\d+]', '', phone_without_ext)
    
    # Если номер начинается с 8, заменяем на +7
    if clean_phone.startswith('8'):
        clean_phone = '+7' + clean_phone[1:]
    # Если номер начинается с 7, добавляем +
    elif clean_phone.startswith('7'):
        clean_phone = '+' + clean_phone
    # Если номер не содержит +, но содержит 10 цифр, добавляем +7
    elif len(re.sub(r'\D', '', clean_phone)) == 10:
        clean_phone = '+7' + re.sub(r'\D', '', clean_phone)
    
    # Извлекаем все цифры (уже без добавочного номера)
    digits = re.sub(r'\D', '', clean_phone)
    
    # Если есть код страны (11 цифр с 7 или 8), убираем его для форматирования
    if len(digits) == 11 and (digits.startswith('7') or digits.startswith('8')):
        digits = digits[1:]  # Убираем первую цифру (7 или 8)
    
    # Форматируем номер, если есть 10 цифр
    if len(digits) == 10:
        formatted = f"+7({digits[:3]}){digits[3:6]}-{digits[6:8]}-{digits[8:]}"
        return formatted + ext
    else:
        # Если не удалось распознать, возвращаем с добавленным добавочным (если был)
        return phone_without_ext + ext


# Функция process_names остается без изменений
def process_names(contact):
    """Обработка ФИО с использованием регулярных выражений"""
    name_parts = " ".join(contact[:3]).strip()
    names = re.findall(r'[А-ЯЁ][а-яё]+', name_parts)
    while len(names) < 3:
        names.append("")
    return names + contact[3:]
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
