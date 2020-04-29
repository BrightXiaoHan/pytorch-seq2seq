from . import DialogueConfig

class Asr(DialogueConfig):
    """
    话术映射类
    """

    def __init__(self):
        self.city_mapping = {
            "二六": "L"
        }

        self.word_mapping = {
            "a楼": "L",
            "二楼": "L"
        }

        self.province_mapping = {
            "乐": "粤"
        }

        self.force_pinyin_mapping = {
            # 所有I纠正为1
            "ai": "1",
            "i": "1",
            "I": "1",
            # 所有的o纠正成0
            "ou": "0",
            "o": "0",
            "O": "0"
        }

        self.pinyin_mapping = {
            "wei": "V",
            "wai": "Y",
            "ba": "8",
            "yao": "1",
            "cha": "X",
            "bi": "B",
            "xi": "C",
            "yi": "E",
            "di": "D",
            "you": "U",
            "ji": "G",
            "yi": "E",
            "a": "R",
            "ju": "G",
            "kai": "K"
        }

        self.pinyin2text = {
            'yun': '云',
            'liao': '辽',
            'hei': '黑',
            'xiang': '湘',
            'wan': '皖',
            'lu': '鲁',
            'xin': '新',
            'su': '苏',
            'shu': '苏',
            "hui": "贵",
            'gan': '赣',
            'gui': '桂',
            'gan': '甘',
            'jin': '晋',
            'meng': '蒙',
            'shan': '陕',
            'min': '闽',
            'gui': '贵',
            'yue': '粤',
            "ye": '粤',
            "yuan": "粤",
            "you": "粤",
            "dui": "粤",
            "jiang": "湘",
            "chuang": "川",
            "gang": "赣",
            "mian": "闽",
            "mei": "闽",
            "ming": "闽",
            "luan": "皖",
            'zang': '藏',
            'ning': '宁',
            'qiong': '琼',
        }

    def reload(self):
        """
        从数据库中加载话术的相关配置
        """
        self.__init__()
        conn = self._get_connection()
        sql = "SELECT * FROM asr_rule"
        cursor = conn.cursor()
        cursor.execute(sql)

        # # 数据库字段 correct_mode：纠正模式  origin_char：原字符  desti_char: 纠正目标字符   correct_type: 纠正类型，1、字符 2、拼音  id:
        for correct_word, origin_char, desti_char, correct_type, _ in cursor:
            # # 纠正类型为字符
            if correct_type == 1:
                if correct_word == 2001: # city模式
                    self.city_mapping[origin_char] = desti_char
                elif correct_word == 2002: # province 模式
                    self.province_mapping[origin_char] = desti_char
                elif correct_word == 2003: # letter  模式
                    self.word_mapping[origin_char] = desti_char
                elif correct_word == 2004: # all 模式
                    self.city_mapping[origin_char] = desti_char
                    self.province_mapping[origin_char] = desti_char
                    self.word_mapping[origin_char] = desti_char
            # 纠正类型为拼音
            elif correct_type == 2:
                if correct_word == 1001: # force模式
                    self.force_pinyin_mapping[origin_char] = desti_char
                elif correct_word == 1002: # soft 模式
                    self.pinyin_mapping[origin_char] = desti_char
            pass
                
asr_config = Asr()