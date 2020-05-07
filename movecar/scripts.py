import os
import sys
import glob
import zipfile
import re
import json
import random

from tqdm import tqdm

cwd = os.path.abspath(os.path.dirname(__file__))
if cwd not in sys.path:
    sys.path.append(cwd)

source_root = os.path.abspath(os.path.join(cwd, ".."))

# from sample import predictor
from correction import rules
from sample import predictor


def extract_log():
    contents = []
    log_dir = os.path.join(cwd, "data/logs")    
    all_file = glob.glob(os.path.join(log_dir, "*.zip"))
    print("开始解析日志压缩文件")
    for zf in tqdm(all_file):
        z = zipfile.ZipFile(zf) 
        for item in z.filelist:
            f = z.open(item.filename)
            contents.append(f.read().decode("utf-8"))
    
    return contents

regx = re.compile("Round [1-9].*?\nUser_Response: (.*?)\..*?Bot_Response: \[se40\](很抱歉，请重新再说一遍完整的车牌号码。|请仔细核对需要移车的号码为.*?，信息正确请回答是的，信息错误请回答不是。|很抱歉，智能客服未能准确获取您的信息，将为您转接人工客服，请稍等。)\[se40\]\. ", flags=re.DOTALL)

def extract_car_number_response(contents):
    qa_pairs = []
    print("开始使用正则进行用户回答抽取")
    for content in tqdm(contents):
        qa_pairs.extend(regx.findall(content))
        
    return qa_pairs


def predict_log():
    """
    处理日志中的车牌号码
    """
    contents = extract_log()
    qa_pairs = extract_car_number_response(contents)
    all_data = []
    print("开始进行预测")
    random.shuffle(qa_pairs)

    for pair in tqdm(qa_pairs[:1000]):
        result_dict = {}
        text = pair[0]
        result_dict["原文"] = text
        rules_correction = rules(text)
        result_dict["规则纠正结果"] = rules_correction
        dnn_result = predictor.predict([i for i in text])
        result_dict["模型纠正结果"] = "".join(dnn_result[:-1])
        
        result = predictor.predict([i for i in rules_correction])
        result_dict["规则加模型纠正结果"] = "".join(result[:-1])

        all_data.append(result_dict)
        
    with open(".vscode/result.json", "w") as f:
        json.dump(all_data, f, ensure_ascii=False)


def predict_test_data():
    """
    处理测试集的数据
    """
    test_data_file = os.path.join(source_root, "data/movecar/test/data.txt")

    test_data = []
    with open(test_data_file, "r") as f:
        for line in f:
            line = line.strip()
            test_data.append(["".join(item.split(" ")) for item in line.split("\t")])
    
    all_data = []
    for pair in tqdm(test_data):
        result_dict = {}
        text = pair[0]
        result_dict["原文"] = text
        rules_correction = rules(text)
        result_dict["规则纠正结果"] = rules_correction
        dnn_result = predictor.predict([i for i in text])
        result_dict["模型纠正结果"] = "".join(dnn_result[:-1])
        
        result = predictor.predict([i for i in rules_correction])
        result_dict["规则加模型纠正结果"] = "".join(result[:-1])

        result_dict["质检人员标注结果"] = pair[1]

        all_data.append(result_dict)
        
    with open(".vscode/test_result.json", "w") as f:
        json.dump(all_data, f, ensure_ascii=False)        
    

if __name__ == "__main__":
    # predict_log()
    # predict_test_data()
    predict_test_data()