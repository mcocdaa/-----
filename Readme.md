# 波形转事例

## Introduction

None

## To use

您的python需要包含以下模块：

- numpy
- matplotlib
- ROOT
- os
- array

1. 下载本项目到本地
```bash
git clone https://github.com/csq1216/waveform_to_event.git
```
2. 进入项目目录,在`数据请放在这里`文件夹中放入您的波形文件`wave0.txt`

```bash
python 读取csv.py
```
3. 运行`读取csv.py`文件，将会在`root保存`文件夹下面生成`waveform_TQ.root`文件，打开`waveform_TQ.root`文件，可以看到波形数据。
4. 运行`TQ打包.py`,将会在`root保存`文件夹下面生成`Event.root`文件，打开`Event.root`文件，可以看到事例数据。
```bash
python TQ打包.py
```