## 目录结构
- 不再细分文件夹了，全部放在根目录下，方便管理，新建文件尽可能写清模块功能

## 分支策略
 - master分支: 主分支，用于发布稳定版本的代码
   - **禁止在该分支上直接开发，只能通过合并其他分支的代码进行更新**
   - 包含最终版本的代码
 - dev分支:开发测试环境分支
   - 提供测试基础环境
   - 包含测试代码
 - xxx 分支：**基于dev分支创建,开发完成后合并回dev分支**
   - 用于开发新功能
   - 用于修复bug
   - 用于代码优化
 - release分支: 基于dev分支创建, 用于最后的测试和修复
   - 在该分支中删除测试代码
   - 最终合并到main分支发布最终版本
- hotfix分支: 紧急修复分支
  - 基于main分支创建, 用于修复最终版本bug
  - 最终合并到main分支发布最终版本

## 日常开发流程说明
- **记得及时拉取最新的提交，避免后续冲突**
- 基于dev分支创建xxx分支, 例如`feature/improve_draw`、`feature/clear`
- 在xxx分支上进行开发,在本地尝试正常运行后**提交pr到dev分支**
- **!!!!不要在main分支上创建分支, 只基于dev分支上创建分支, 避免后面合并时产生不必要的冲突和麻烦**
- **!!!!不要把pr合并到main分支上,合并到dev分支上**

## 基础版本说明
- 提供三种模式`mode=drag`、`mode=eraser`、`mode=draw`
- 原点通过碰撞按钮切换模式
- 在每种模式下，食指与拇指捏合代表执行当前模式的操作，松开代表无操作
- 提供三种可选画笔颜色，也是碰撞选择
- 提供范围为1-20的画笔粗细,通过碰撞按钮可以增大或减小画笔粗细
- 按钮上均设置了冷却时间，防止手势识别频率过快带来的不便操作
- 按钮功能说明


| <div style="background-color: rgb(255, 0, 0); width: 50px; height: 50px;"></div>   </span> | <div style="background-color: rgb(0, 255, 0); width: 50px; height: 50px;"></div> | <div style="background-color: rgb(0, 0, 255); width: 50px; height: 50px;"></div>   | <div style="background-color: rgb(0, 0, 0); width: 50px; height: 50px;"></div>   | <div style="background-color: rgb(128, 128, 128); width: 50px; height: 50px;"></div>  | <div style="background-color: rgb(200, 200, 200); width: 50px; height: 50px;"></div> | <div style="background-color: rgb(100, 100, 100); width: 50px; height: 50px;"></div> | <div style="background-color: rgb(0, 150, 100); width: 50px; height: 50px;"></div>  |
| :-------: | :-------:| :-------: | :-------: | :-------: | :-------: | :-------: | :-------: |
| 红色笔   | 浅绿色笔 | 蓝色笔   | 变细     | 变粗     | 拖拽模式 | 擦除模式 | 绘画模式 |




## 测试版本说明
- 画布中显示当前模式mode,画笔颜色,画笔粗细,画布偏移量,实时帧率fps
- 终端输出按钮碰撞结果，便于调试