# experiment/

领域代码住本目录：数据构建、拟合、探针等一切脚本在这里落笔。
一个项目一簇脚本，命名带项目前缀，同簇放同目录。
runner 按设计段（experiment-design skill 的设计段规格）落笔，不凭空发明脚本。
历史项目的代码在本仓 git 历史里：`git log --diff-filter=D -- experiment/` 找回被删文件，`git show <rev>:<path>` 取回内容。
