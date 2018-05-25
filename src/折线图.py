# coding:utf-8
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

time = [0, 2000, 4167, 9662, 26821, 42885, 61998, 72945, 94143, 111963, 131187, 137859, 168730, 184328, 203933, 218100,
        231496, 239921, 257772, 281866, 303320, 314684, 328876, 357014, 388143, 409456, 428272, 434791, 502692, 527090,
        594882, 656410, 758282, 857807, 875141]
elo = [0, 133, 207, 274, 370, 489, 593, 682, 699, 874, 948, 951, 1200, 1287, 1370, 1453, 1635, 1658, 1822, 1988, 2055,
       2237, 2374, 2400, 2476, 2514, 2584, 2665, 2754, 2778, 2787, 2863, 2923, 2939, 2962]
time_labels = [x * 100000 for x in range((time[-1] + 200000) // 100000)]
print(time_labels)
elo_labels = [x * 100 for x in range((elo[-1] + 500) // 100)]
plt.xlabel(u'对局次数/k')
plt.ylabel('elo积分')

plt.plot(time, elo, 'black')
plt.xticks(time_labels, elo_labels)

# plt.legend(bbox_to_anchor=[1, 1])
plt.grid()
plt.savefig('elo.png')
plt.show()
