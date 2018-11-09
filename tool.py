with open("列表页失败链接_temp.txt", "r") as f:
    a = [i.strip("\n") for i in f.readlines()]
len_a = len(a)
print(len_a)
b = []
for i in range(len_a):
    print(i)
    if i % 2 == 0:
        b.append(a[i])

print(len(b))
print(b)
with open("列表页失败链接_temp1.txt", "w") as f:
    for i in b:
        f.write(i+"\n")
