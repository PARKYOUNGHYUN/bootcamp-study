def classify_refined(row):
    text = str(row).replace('·', ' ').replace('(', ' ').replace(')', ' ')
    words = text.split()

    if '신입' in words and '경력' in words:
        return None

    if '경력무관' in text.replace(' ', ''):
        return '경력무관'

    if '신입' in words:
        return '신입'

    if '경력' in words or any(char.isdigit() for char in text):
        return '경력'

    return None
