# 智能课堂考勤与专注度分析系统

本项目为本科毕业设计《智能课堂考勤与专注度分析系统的设计与实现》的配套系统实现。

## 技术栈

- 后端：Python + Flask
- 数据库：SQLite（通过 SQLAlchemy 访问）
- 计算机视觉：OpenCV + NumPy
- 前端：HTML + Bootstrap + Chart.js

## 当前功能

- 学生管理（新增学生、查看学生列表）
- 课程管理（新增课程、课程列表、删除未关联课程）
- 人脸录入（摄像头抓拍并保存人脸特征）
- 课堂考勤（发起课堂、拍照识别签到）
- 专注度分析（上传课堂图片，基于人脸位置规则计算专注度）
- 统计可视化（考勤柱状图 + 专注度饼图）

## 运行环境

- Python 3.9+（推荐）
- Windows 10 及以上

## 安装与启动

安装依赖：

```bash
pip install -r requirements.txt
```

启动开发服务器：

```bash
python app.py
```

启动后访问：

- 首页：`http://127.0.0.1:5000/`
- 课程管理：`http://127.0.0.1:5000/attendance/courses`
- 发起考勤：`http://127.0.0.1:5000/attendance/sessions/start`
- 专注度分析：`http://127.0.0.1:5000/focus/analyze`
- 统计页面：`http://127.0.0.1:5000/stats/overview`

## 说明

- 专注度模块当前为可运行的简化实现：使用 OpenCV 人脸检测，根据人脸在画面中的位置与面积占比生成 0~1 分数并划分等级（low / medium / high）。
- 本仓库默认使用本地 SQLite 数据库文件（`instance/smart_classroom.db`）。

