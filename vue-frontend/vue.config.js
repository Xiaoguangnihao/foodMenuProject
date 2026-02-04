// vue.config.js
const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  lintOnSave: false, // 暂时关闭eslint

  // 移除或修改CSS配置
  css: {
    loaderOptions: {
      sass: {
        // 使用 @use 替代 @import
        additionalData: `@use "@/assets/scss/variables.scss" as *;`
      }
    }
  }
})