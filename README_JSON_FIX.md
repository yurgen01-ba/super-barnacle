# JSONDecodeError Fix Patch

Ошибка:

```text
json.decoder.JSONDecodeError: Unterminated string
```

означает, что Claude вернул невалидный или обрезанный JSON. Из-за этого Streamlit падал до сохранения данных в Memory.

## Что заменить

### 1. Замени файл:

```text
ai/extractor.py
```

на содержимое:

```text
extractor_replacement.py
```

### 2. Замени файл:

```text
extractors/jira_pdf.py
```

на содержимое:

```text
jira_pdf_replacement.py
```

## Что изменилось

- extractor больше не падает сразу на битом JSON;
- добавлен repair-запрос к Claude;
- PDF режется на чанки;
- каждый PDF chunk обрабатывается отдельно;
- если один chunk сломался, остальные продолжают обрабатываться;
- ошибки возвращаются в `result["errors"]`.

## Маленький update в app.py для Jira PDF

В Jira PDF блоке после:

```python
if result["warning"]:
    st.warning(result["warning"])
```

добавь:

```python
if result.get("errors"):
    st.error("Some PDF chunks failed:")
    st.write(result["errors"])
```

## Про warning Whisper

```text
FP16 is not supported on CPU; using FP32 instead
```

Это не ошибка. Это просто предупреждение: Whisper работает на CPU и использует FP32 вместо FP16.
