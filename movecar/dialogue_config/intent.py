import re
from . import DialogueConfig

class Intent(DialogueConfig):
    
    def __init__(self):
        self.mapping = {
            "confirm": set(),
            "deny": set(),
            "ambiguous": set()
        }

    def reload(self):
        """
        从数据库中重新加载肯定否定意图的配置
        """
        self.__init__()
        conn = self._get_connection()
        sql = "SELECT * FROM intent_rule"
        cursor = conn.cursor()
        cursor.execute(sql)

        # 数据库字段 desc：意图对应字符串  intent：意图编号 1、肯定，2、否定，3、模糊   id: 配置的id编号
        for desc, intent, _ in cursor:
            if intent == 1:
                self.mapping["confirm"].add(desc)
            elif intent == 2:
                self.mapping["deny"].add(desc)
            elif intent == 3:
                self.mapping["ambiguous"].add(desc)

    def is_confirm(self, text):
        confirm_set = self.mapping["confirm"]
        if not confirm_set:
            return False
        regx = re.compile("(" + "|".join(confirm_set) + ")")
        result = regx.findall(text)
        return len(result) != 0

    def is_deny(self, text):
        deny_set = self.mapping["deny"]
        if not deny_set:
            return False
        regx = re.compile("(" + "|".join(deny_set) + ")")
        result = regx.findall(text)
        return len(result) != 0

    def is_ambiguous(self, text):
        ambiguous_set = self.mapping["ambiguous"]
        if not ambiguous_set:
            return False
        regx = re.compile("(" + "|".join(ambiguous_set) + ")")
        result = regx.findall(text)
        return len(result) != 0


intent_config = Intent()