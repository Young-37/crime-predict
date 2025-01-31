from section_maker import *
from const_data import *
import numpy as np
import copy
from module import conv
import matplotlib.pyplot as plt


# 모델이 생성한 결과 * 10
FIRST_PREDICT = copy.deepcopy(SPRING_EVENING_SUNNY)
for i in range(1107):
    FIRST_PREDICT[i] = FIRST_PREDICT[i]*10

'''
<막대 그래프로 표현>
for s in range(3):
    x = np.arange(len(SECTION[s]))
    y = []  
    for i in SECTION[s]:
        y.append(CRIME_PREDICT[i])
    plt.bar(x, y)
    plt.show()
'''
WIDTH = 59
HEIGHT = 32
GRID_NUM = 1107
'''
<5x5 Kernel>
LPF = [[1/36, 1/36, 1/36, 1/36, 1/36],
       [1/36, 2/36, 2/36, 2/36, 1/36],
       [1/36, 2/36, 4/36, 2/36, 1/36],
       [1/36, 2/36, 2/36, 2/36, 1/36],
       [1/36, 1/36, 1/36, 1/36, 1/36]]
'''
LPF = [[1/10, 1/10, 1/10],
       [1/10, 2/10, 1/10],
       [1/10, 1/10, 1/10]]

SECTION_DICT = {
    2: [255, 100, 50],
    1: [50, 255, 100],
    0: [100, 50, 255]
}

# 색상 딕셔너리 생성(총 256단계)
new_0 = {}
new_1 = {}
new_2 = {}
for i in range(256):
    new_0[i] = [255, 255 - i, 255 - i]
for i in range(256):
    new_1[i] = [255 - i, 255, 255 - i]
for i in range(256):
    new_2[i] = [255 - i, 255 - i, 255]

# 그리드 이미지를 배열로 변환
grid = []
img = cv2.imread("img/grid.png", 1)
img = cv2.resize(dsize=(WIDTH, HEIGHT), src=img)
result = np.full((HEIGHT, WIDTH, 3), 255, np.uint8)
for x in range(WIDTH):
    for y in range(HEIGHT):
        if img[y][x][0] != 255 or img[y][x][1] != 255 or img[y][x][2] != 255:
            grid.append([y, x])

# 모델이 생성한 결과를 그리드 배열판에 올림
map = np.zeros(shape=(HEIGHT, WIDTH))
idx = 0
for x in range(WIDTH):
    for y in range(HEIGHT):
        if img[y][x][0] != 255 or img[y][x][1] != 255 or img[y][x][2] != 255:
            map[y][x] = FIRST_PREDICT[idx]
            idx += 1

# 배열판에 올린 숫자들을 LPF로 뭉개줌
CRIME_PREDICT = []
map = conv(map, np.array(LPF), padding=1)

for i in range(1107):
    y, x = grid[i]
    CRIME_PREDICT.append(int(map[y][x]))

# 그리드 별로 색상을 결정
grid_color = np.empty(shape=(1107, 3), dtype=np.uint8)
for i in range(3):
    histogram = np.zeros(256, np.float_)
    for j in SECTION[i]:
        histogram[CRIME_PREDICT[j]] += 1    # Make Histogram!
    for j in range(256):
        histogram[j] /= len(SECTION[i])  # Normalize it!
    for j in range(1, 256):
        histogram[j] += histogram[j - 1]  # Accumulate it!
    for j in range(1, 256):
        histogram[j] = round(histogram[j] * 255)  # Convert to int(round)!
    for j in SECTION[i]:
        key = int(histogram[CRIME_PREDICT[j]])  # 0 to 255
        if i == 0:
            grid_color[j] = new_0[key]
        elif i == 1:
            grid_color[j] = new_1[key]
        elif i == 2:
            grid_color[j] = new_2[key]
        '''
        if key <= 255 and key >= 235:  # 235 is Threshold!
            grid_color[j] = new_d[key]
        else:
            grid_color[j] = new_d[0]
        '''
        crime_img = np.full((HEIGHT, WIDTH), -1, np.uint8)

# 결정된 색상을 result[]에 입혀줌
for i in range(GRID_NUM):
    y, x = grid[i]
    result[y][x][0] = grid_color[i][2]
    result[y][x][1] = grid_color[i][1]
    result[y][x][2] = grid_color[i][0]

'''
<구역별 색상표시>
for i in range(3):
    for j in SECTION[i]:
        color = SECTION_DICT[i]
        y, x = grid[j]
        result[y][x][0] = color[2]
        result[y][x][1] = color[1]
        result[y][x][2] = color[0]
'''
'''
# A 알고리즘
res_A = np.zeros((HEIGHT, WIDTH))
for x in range(2, WIDTH, 4):
    for y in range(2, HEIGHT, 4):
        if img[y][x][0] != 255 or img[y][x][1] != 255 or img[y][x][2] != 255:
            res_A[y][x] = 1

img_A = img
for x in range(WIDTH):
    for y in range(HEIGHT):
        if res_A[y][x] == 1:
            img_A[y][x][0] = 255
            img_A[y][x][1] = 10
            img_A[y][x][2] = 10
img_A = cv2.resize(img_A, dsize=(WIDTH*10, HEIGHT*10), interpolation=cv2.INTER_NEAREST_EXACT)
'''
# C 알고리즘
res_C = np.zeros((HEIGHT, WIDTH))
# y, x는 중앙점
flag = 2
for x in range(2, WIDTH-2, 4):
    for y in range(2, HEIGHT-2, 4):
        if flag == 2:
            flag += 1
        else:
            flag = 2
        maxnum = -1
        maxcord = [y,x]
        # 중앙점 기준 양 옆 2개씩 모아서 대소 비교
        for i in range(-2, 3):
            for j in range(-2, 3):

                a, b = x+i, y+j
                if img[b][a][0] != 255 or img[b][a][1] != 255 or img[b][a][2] != 255:
                    res_C[b][a] = flag
                if map[b][a] > maxnum:
                    maxnum = map[b][a]
                    maxcoord = [b, a]
        # 그 중 최댓값이 d, c
        d, c = maxcoord
        if img[d][c][0] == 255 and img[d][c][1] == 255 and img[d][c][2] == 255:
            res_C[d][c] = 0
        else:
            res_C[d][c] = 1

img_C = img
for x in range(WIDTH):
    for y in range(HEIGHT):
        if res_C[y][x] == 1:
            img_C[y][x][0] = 255
            img_C[y][x][1] = 10
            img_C[y][x][2] = 10
        elif res_C[y][x] == 2:
            img_C[y][x][0] = 200
            img_C[y][x][1] = 180
            img_C[y][x][2] = 200
        elif res_C[y][x] == 3:
            img_C[y][x][0] = 180
            img_C[y][x][1] = 200
            img_C[y][x][2] = 200
img_C = cv2.resize(img_C, dsize=(WIDTH*10, HEIGHT*10), interpolation=cv2.INTER_NEAREST_EXACT)

grey = cv2.imread("grid.png", 0)
grey = cv2.resize(dsize=(WIDTH, HEIGHT), src=grey)

num2grid = []
grid2num = []
for x in range(WIDTH):
    for y in range(HEIGHT):
        if grey[y][x] != 255:
            num2grid.append([y, x])
print(num2grid)

final = []
for i in range(3):
    tmp = []
    print(i)
    for c in SECTION[i]:
        y, x = num2grid[c]
        if res_C[y][x] == 1:
            tmp.append(c)
    final.append(tmp)

print(final)




# 결과 맵을 확대해서 출력
result = cv2.resize(result, dsize=(WIDTH*20, HEIGHT*20), interpolation=cv2.INTER_NEAREST_EXACT)
cv2.imshow('res', img_C)
cv2.waitKey()
