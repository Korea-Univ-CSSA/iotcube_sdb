sample_files = open("./osscollector/sample_java", "r")
sample = sample_files.readlines()
s = [i.strip().split('/')[-1][:-4] for i in sample]

repo_files = open("./cur_repo_files.txt", "r")
repo_f = repo_files.readlines()
rf = [i.strip().split('@@')[-1] for i in repo_f]

repo_src = open("./cur_test.txt", "r")
repo_s = repo_src.readlines()
rs = [i.strip().split('@@')[-1] for i in repo_s]

cnt = 0
fin = set()
for i in s:
    if i not in rf:
        print(i)
        fin.add(i)
        cnt += 1
print(cnt)

print("\n\n============================\n\n")

cnt = 0
for i in s:
    if i not in rs:
        print(i)
        fin.add(i)
        cnt+=1
print(cnt)

print("\n\n")
print(fin, len(fin))

for i in fin:
    print(i)