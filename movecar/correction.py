import pickle
import re
from pypinyin import lazy_pinyin as pinyin


asr_config_file = "movecar/data/asr_config.pkl"
with open(asr_config_file, "rb") as f:
    asr_config = pickle.load(f)
    
pinin_need_singing = ["bi", "yi", "di"]

province_letter = ['皖', '鲁', '黑', '辽', '闽', '吉', '陕', '新', '青', '赣', '宁', '甘', '藏', '粤', '浙', '湘', '蒙', '沪', '晋', '苏', '京', '云', '川', '琼', '贵', '渝', '豫', '鄂']

# Define some regx to proccess msg
RE_PLATE_NUMBER = re.compile(
    '[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领]{1}[A-Z查叉插]{1}-?[A-Z0-9查叉插]{4}[A-Z0-9挂学警港澳查叉插]{1}[A-Z0-9查叉插]?')

RE_ALL_LETER = re.compile(
    r"[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领A-Z0-9一二三四五六七八九零]+")


def chinese2arabic(text):
    """
    将消息中的汉字转换为阿拉伯数字
    """
    number_map = {
        '一': '1',
        "二": '2',
        "三": '3',
        "四": '4',
        "五": '5',
        "六": '6',
        "七": '7',
        "八": '8',
        "九": '9',
        "零": '0',
    }

    for key, value in number_map.items():
        text = text.replace(key, value)

    return text

def pronunciation_correction(p, origin_word):
    """
    对用户发音进行纠正，传入字符串为字符的拼音
    """
    force_correct = asr_config.force_pinyin_mapping
    
    if p in force_correct:
        return force_correct[p]

    correction_dict = asr_config.pinyin_mapping
    if p in correction_dict and p != origin_word:
        return correction_dict[p]
    else:
        return origin_word

def rules(text):
     # 小写字母转大写字母
    text = text.upper()
    # 清除干扰车牌识别的一些符号
    text = re.sub("[\\.\\*,。，-]", '', text)

    province_letter_position = []  # 记录省份车牌字符的位置 

    # 使用规则进行车牌纠正
    all_letter = []
    mask = []

    i = 0
    while i < len(text):
        word = text[i]
        two_words = "None" if i == len(text) - 1 else text[i:i+2]
        p = pinyin(word)[0]

        # 车牌省份字符双字符规则纠错
        if two_words in asr_config.province_mapping and asr_config.province_mapping[two_words] == "粤":
            correct_word = asr_config.province_mapping[two_words]
            all_letter.append(correct_word)
            mask.append(True)
            province_letter_position.append(i + 1)
            i += 2

        # 车牌省份字符单字符规则纠错
        elif word in asr_config.province_mapping and asr_config.province_mapping[word] == "粤":
            correct_word = asr_config.province_mapping[word]
            all_letter.append(correct_word)
            mask.append(True)
            province_letter_position.append(i)
            i += 1
        
        # 车牌省份字符拼音规则纠错
        elif p in asr_config.pinyin2text and asr_config.pinyin2text[p] == "粤":
            correct_word = asr_config.pinyin2text[p]
            all_letter.append(correct_word)
            if p not in pinin_need_singing:
                mask.append(True)
            else:
                mask.append(False)
            province_letter_position.append(i)
            i += 1

        
        # 车牌城市双字符规则纠错
        elif two_words in asr_config.city_mapping and i - 1 in province_letter_position:
            correct_word = asr_config.city_mapping[two_words]
            all_letter.append(correct_word)
            mask.append(True)
            i += 2

        # 车牌城市单字符规则纠错
        elif word in asr_config.word_mapping and i - 1 in province_letter_position:
            correct_word = asr_config.word_mapping[word]
            all_letter.append(correct_word)
            mask.append(True)
            i += 1

        # 车牌主体双字符纠错
        elif two_words in asr_config.word_mapping:
            correct_word = asr_config.word_mapping[two_words]
            all_letter.append(correct_word)
            mask.append(True)
            i += 2

        # 车牌主体单字符规则纠错
        elif word in asr_config.word_mapping:
            correct_word = asr_config.word_mapping[word]
            all_letter.append(correct_word)
            mask.append(True)
            i += 1
        
        # 车牌市区字符，主体字符拼音纠错
        elif pronunciation_correction(p, word) != word:
            correct_word = pronunciation_correction(p, word)
            all_letter.append(correct_word)
            if correct_word not in ["E"]:
                mask.append(True)
            else:
                mask.append(False)
            i += 1
        elif len(RE_ALL_LETER.findall(word)) > 0:
            all_letter.append(word)
            mask.append(False)
            i += 1
        # 车牌省份字符双字符规则纠错
        elif two_words in asr_config.province_mapping and asr_config.province_mapping[two_words] != "粤":
            correct_word = asr_config.province_mapping[two_words]
            all_letter.append(correct_word)
            mask.append(True)
            province_letter_position.append(i + 1)
            i += 2

        # 车牌省份字符单字符规则纠错
        elif word in asr_config.province_mapping and asr_config.province_mapping[word] != "粤":
            correct_word = asr_config.province_mapping[word]
            all_letter.append(correct_word)
            mask.append(True)
            province_letter_position.append(i)
            i += 1
        
        # 车牌省份字符拼音规则纠错
        elif p in asr_config.pinyin2text and asr_config.pinyin2text[p] != "粤":
            correct_word = asr_config.pinyin2text[p]
            all_letter.append(correct_word)
            if p not in pinin_need_singing:
                mask.append(True)
            else:
                mask.append(False)
            province_letter_position.append(i)
            i += 1
        else:
            all_letter.append(word)
            mask.append(False)
            i += 1

    all_letter = "".join(all_letter)
    # 将中文数字转化为英文数字
    all_letter = chinese2arabic(all_letter)
    plate_nums = RE_PLATE_NUMBER.findall(all_letter)
    
    if len(plate_nums) > 0:
        return plate_nums[0]
    else:
        return all_letter
