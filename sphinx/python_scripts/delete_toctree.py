index_file_path = '../index.md'

#Extract text from index.md
index_file = open(index_file_path, 'r')
index_lines = index_file.readlines()
index_file.close()

#find and remove toctree
for i in range(len(index_lines)):
    if '```{eval-rst}' in index_lines[i]:
        toctree_start = i
index_lines = index_lines[:toctree_start]
index_lines[-1] = index_lines[-1].replace('\n', '')    #remove extra newline at the end of the file

#overwrite index.md without including toctree
index_file = open(index_file_path, 'w')
for line in index_lines:
    index_file.write(line)
index_file.close()