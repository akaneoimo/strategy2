# 事件应对智能决策系统

`front-end` 和 `back-end` 分别为前后端工作目录，可参考各自目录下的 `README.md` 进行安装配置和开发。

开发完成后，运行整个项目只需在 `front-end` 目录下执行

```
yarn build
```
此命令会在 `back-end/dist` 目录下生成打包后的前端代码，然后在 `back-end` 目录下运行

```
uvicorn main:app
```
启动项目即可