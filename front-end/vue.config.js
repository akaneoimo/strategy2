module.exports = {
  devServer: {
    /**
     * https://github.com/chimurai/http-proxy-middleware#options
     */
    proxy: {
      '/api/': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  chainWebpack: config => {
    config.plugin('html').tap(args => {
      args[0].title = '事件应对智能决策系统';
      return args;
    });
  },
  outputDir: '../back-end/dist',
};