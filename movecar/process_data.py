import random
import os
import glob
from openpyxl import load_workbook


cwd = os.path.abspath(os.path.dirname(__file__))
source_root = os.path.abspath(os.path.join(cwd, ".."))


def process(file_path):
    dataset = []
    sheet = load_workbook(filename=file_path).active
    for i, row in enumerate(sheet.rows):
        if i == 0:
            continue
        origin1, target1, origin2, target2 = row[0], row[1], row[2], row[3]
        if origin1.value is not None and target1.value is not None:
            dataset.append([str(origin1.value).strip(),
                            str(target1.value).strip()])

        if origin2.value is not None and target2.value is not None:
            dataset.append([str(origin2.value).strip(),
                            str(target2.value).strip()])
    return dataset


def genreate_fake_data(num):
    """生成车牌号码假数据

    Args:
        num (int): 生成假数据的数量
    """
    provinces = ['皖', '鲁', '黑', '辽', '闽', '吉', '陕', '新', '青', '赣', '宁', '甘', '藏',
                 '粤', '浙', '湘', '蒙', '沪', '晋', '苏', '京', '云', '川', '琼', '贵', '渝', '豫', '鄂']
    letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
               "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    lower_letters = [i.lower() for i in letters]
    numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    chinese = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]

    dataset = []
    for i in range(num):
        car_number = ""
        car_number += random.choice(provinces)
        correction = car_number

        if random.choice([0, 1]):
            city_letter = random.choice(letters)
        else:
            city_letter = random.choice(lower_letters)

        car_number += city_letter
        correction += city_letter.upper()

        for i in range(6):
            if i == 5 and random.choice([0, 1]):
                break
            pool = random.choice([letters, lower_letters, numbers, chinese])
            body = random.choice(pool)

            car_number += body

            if pool == letters:
                correction += body
            elif pool == lower_letters:
                correction += letters[lower_letters.index(body)]
            elif pool == numbers:
                correction += body
            elif pool == chinese:
                correction += numbers[chinese.index(body)]

        dataset.append([car_number, correction])
    return dataset


def generate_train_val_dev(dataset, destination):


    def generate(data, dest):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        
        source = [item[0] for item in data]
        target = [item[1] for item in data]

        source_vocab = set()
        for _ in source:
            source_vocab.update(_)

        with open(os.path.join(dest, "source.vocab"), "w") as f:
            for _ in source_vocab:
                f.write(_)
                f.write("\n")

        target_vocab = set()
        for _ in target:
            target_vocab.update(_)

        with open(os.path.join(dest, "target.vocab"), "w") as f:
            for _ in target_vocab:
                f.write(_)
                f.write("\n")

        with open(os.path.join(dest, "data.txt"), "w") as f:
            for s, t in zip(source, target):
                f.write(" ".join(s) + "\t" + " ".join(t) + "\n")

    random.shuffle(dataset)
    split_ratio = [0.7, 0.2, 0.1]

    split_point1 = int(len(dataset) * split_ratio[0])
    split_point2 = int(len(dataset) * (split_ratio[0] + split_ratio[1]))

    train_set = dataset[:split_point1]
    dev_set = dataset[split_point1:split_point2]
    test_set = dataset[split_point2:]

    assert len(train_set) > 0
    assert len(dev_set) > 0
    assert len(test_set) > 0

    
    generate(train_set, os.path.join(destination, "train"))
    generate(dev_set, os.path.join(destination, "dev"))
    generate(test_set, os.path.join(destination, "test"))

if __name__ == "__main__":

    all_files = glob.glob(os.path.join(cwd, "data/*.xlsx"))
    dataset = []
    for f in all_files:
        sub_data = process(f)
        dataset.extend(sub_data)
    dataset.extend(genreate_fake_data(len(dataset)))

    destination = os.path.join(source_root, "data/movecar")
    generate_train_val_dev(dataset, destination)
